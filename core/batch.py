"""Versioned, chronological batch experiment, separate from the legacy dashboard.

Training consumes labels once. Prediction accepts only observed tables and a
closed batch; it never trains or reads labels. This is not streaming inference.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

from core.data_quality import require_valid, require_time_resolution
from core.contract import MINIMAL
from core.detect import FEATURES, assert_no_labels, build_features, explain, rule_flags
from core.evaluate import expected_hits
from core.synthetic import DEFAULT, ICD_CAP, PERIOD_START, SEED, generate_world
from core.workload import require_budget

VERSION = "batch-gbm-v3"
DATA_VERSION = "synthetic-chronology-v2"
TEMPORAL_VERSION = "batch-gbm-temporal-v2"
UPCODING_VERSION = "batch-gbm-upcoding-v2"
MODE_VERSION = {"base": VERSION, "temporal": TEMPORAL_VERSION, "upcoding": UPCODING_VERSION}


def feature_names(feature_set):
    if feature_set == "base":
        return list(FEATURES)
    if feature_set == "temporal":
        from core.temporal_features import EXTRA_FEATURES
        return list(FEATURES) + EXTRA_FEATURES
    if feature_set == "upcoding":
        from core.upcoding_features import UPCODING_FEATURES
        return list(FEATURES) + UPCODING_FEATURES
    raise ValueError("feature_set harus base, temporal, atau upcoding.")


@dataclass
class BatchModel:
    estimator: HistGradientBoostingClassifier
    history: pd.DataFrame
    faskes: pd.DataFrame
    affiliations: pd.DataFrame
    patients: pd.DataFrame
    metadata: dict
    tariff_caps: dict


def _features(claims, faskes, affiliations, patients, tariff_caps, feature_set="base"):
    require_valid(claims, faskes, affiliations, patients)
    require_time_resolution(claims)
    require_budget(claims, faskes=faskes, affiliations=affiliations, patients=patients)
    if not claims.icd.isin(tariff_caps).all():
        raise ValueError("Kode diagnosis belum memiliki referensi tarif prototipe; pemetaan perlu dilengkapi.")
    normalized = claims.copy()
    for column in ("referral_from_faskes", "referral_from_doctor"):
        normalized[column] = normalized[column].replace(r"^\s*$", None, regex=True)
    x = build_features(normalized, faskes, affiliations, patients, tariff_caps=tariff_caps)
    feature_names(feature_set)
    if feature_set == "temporal":
        from core.temporal_features import extend
        x = extend(normalized, x)
    elif feature_set == "upcoding":
        from core.upcoding_features import extend
        x = extend(normalized, x, faskes)
    if not np.isfinite(x.to_numpy(dtype=float)).all():
        raise ValueError("Fitur mengandung nilai tidak terbatas; periksa kualitas data dan referensi.")
    return x


def _labels(labels, ids):
    if not {"claim_id", "is_fraud"}.issubset(labels.columns):
        raise ValueError("Label terpisah wajib memiliki claim_id dan is_fraud.")
    if labels.claim_id.duplicated().any() or set(labels.claim_id) != set(ids):
        raise ValueError("Label harus unik dan tepat sesuai klaim yang dievaluasi/dilatih.")
    y = labels.set_index("claim_id").loc[ids, "is_fraud"]
    if not y.isin([0, 1]).all():
        raise ValueError("Label harus berupa 0 atau 1 tanpa nilai kosong.")
    return y.to_numpy(dtype=int)


def train(claims, faskes, affiliations, patients, labels, *, cutoff, seed=SEED, tariff_caps=None, feature_set="base") -> BatchModel:
    cutoff = pd.Timestamp(cutoff)
    caps = dict(ICD_CAP if tariff_caps is None else tariff_caps)
    if not caps or any(not isinstance(k, str) or not isinstance(v, (int, float))
                       or isinstance(v, bool) or not np.isfinite(v) or v <= 0 for k, v in caps.items()):
        raise ValueError("Referensi tarif harus berisi kode dan angka positif terbatas.")
    x = _features(claims, faskes, affiliations, patients, caps, feature_set)
    if pd.isna(cutoff) or (claims.submit_ts > cutoff).any():
        raise ValueError("Data latih melewati batas waktu pelatihan.")
    y = _labels(labels, x.index)
    if len(np.unique(y)) != 2:
        raise ValueError("Pelatihan memerlukan kedua kelas pada label historis.")
    estimator = HistGradientBoostingClassifier(max_depth=4, learning_rate=.08, max_iter=150,
                                               class_weight="balanced", random_state=seed)
    estimator.fit(x, y)
    fingerprint = hashlib.sha256()
    for frame in (claims, faskes, affiliations, patients, labels):
        fingerprint.update(pd.util.hash_pandas_object(frame, index=True).values.tobytes())
    metadata = dict(version=MODE_VERSION[feature_set], sklearn_version=sklearn.__version__, seed=seed,
                    cutoff=cutoff.isoformat(), n_training_claims=len(claims), features=list(x.columns), feature_set=feature_set,
                    training_fingerprint=fingerprint.hexdigest(),
                    score_semantics="Ranking signal, not a calibrated fraud probability",
                    inference="Closed batch; training data and current batch form the observable snapshot")
    metadata["tariff_fingerprint"] = hashlib.sha256(json.dumps(caps, sort_keys=True).encode()).hexdigest()
    return BatchModel(estimator, claims.copy(deep=True), faskes.copy(deep=True),
                      affiliations.copy(deep=True), patients.copy(deep=True), metadata, caps)


def predict(model: BatchModel, claims: pd.DataFrame, *, as_of, references=None) -> pd.DataFrame:
    """Score a NEW batch using a fixed model; input labels are rejected."""
    mode = model.metadata.get("feature_set", "base")
    if mode not in MODE_VERSION or model.metadata.get("version") != MODE_VERSION[mode]:
        raise ValueError("Model berasal dari versi lama; jalankan pelatihan ulang sebelum prediksi.")
    if model.metadata["features"] != feature_names(mode):
        raise ValueError("Skema fitur model berbeda; latih ulang dengan versi kode yang sesuai.")
    refs = dict(faskes=model.faskes, affiliations=model.affiliations, patients=model.patients)
    if references is not None:
        if set(references) != set(refs):
            raise ValueError("Referensi batch harus memuat faskes, affiliations, patients.")
        for name, old in refs.items():
            new = references[name]
            assert_no_labels(new)
            keys = {"faskes": ["faskes_id"], "patients": ["patient_id"],
                    "affiliations": ["doctor_id", "faskes_id"]}[name]
            if not set(MINIMAL[name]).issubset(new.columns):
                raise ValueError(f"Skema referensi {name} tidak lengkap.")
            if new.duplicated(keys).any():
                raise ValueError(f"Kunci referensi {name} duplikat.")
            # Exact repeated rows are allowed; conflicting existing IDs are not.
            merged = pd.concat([old[MINIMAL[name]], new[MINIMAL[name]]], ignore_index=True).drop_duplicates()
            if merged.duplicated(keys).any():
                raise ValueError(f"Referensi {name} bertentangan dengan snapshot pelatihan.")
            refs[name] = merged
    require_valid(claims, **refs)
    require_time_resolution(claims)
    end, cutoff = pd.Timestamp(as_of), pd.Timestamp(model.metadata["cutoff"])
    if pd.isna(end) or end <= cutoff or (claims.submit_ts <= cutoff).any() or (claims.submit_ts > end).any():
        raise ValueError("Batch harus setelah cutoff pelatihan dan tidak melewati as_of.")
    if claims.claim_id.isin(model.history.claim_id).any():
        raise ValueError("ID klaim batch bertumpang tindih dengan data latih.")
    snapshot = pd.concat([model.history, claims], ignore_index=True)
    x = _features(snapshot, **refs, tariff_caps=model.tariff_caps, feature_set=mode).loc[claims.claim_id]
    score = model.estimator.predict_proba(x)[:, 1]
    result = pd.DataFrame({"claim_id": x.index, "priority_score": score * 100})
    result["indicators"] = [json.dumps(explain(row), ensure_ascii=False) for _, row in x.iterrows()]
    from core.indicator_evidence import attach
    result["comparison_evidence"] = attach(snapshot, x)
    if mode == "temporal":
        from core.temporal_features import indicators
        result["temporal_indicators"] = [json.dumps(indicators(row), ensure_ascii=False) for _, row in x.iterrows()]
    elif mode == "upcoding":
        from core.upcoding_features import indicators
        result["upcoding_indicators"] = [json.dumps(indicators(row), ensure_ascii=False) for _, row in x.iterrows()]
    result["model_version"] = model.metadata["version"]
    result["as_of"] = end.isoformat()
    return result.sort_values(["priority_score", "claim_id"], ascending=[False, True]).reset_index(drop=True)


def evaluate(scores, labels, *, capacity=500):
    if capacity < 1 or scores.empty or scores.claim_id.duplicated().any():
        raise ValueError("Kapasitas harus positif dan skor klaim harus unik serta tidak kosong.")
    y = _labels(labels, scores.claim_id)
    s = scores.priority_score.to_numpy(dtype=float)
    k = min(int(capacity), len(y))
    hits = float(expected_hits(y, s, [k])[0])
    both = len(np.unique(y)) == 2
    return dict(n_claims=len(y), n_fraud=int(y.sum()), capacity=k,
                auc=float(roc_auc_score(y, s)) if both else None,
                average_precision=float(average_precision_score(y, s)) if y.sum() else None,
                expected_fraud_at_k=hits, precision_at_k=hits / k,
                expected_false_reviews=k - hits, expected_fraud_missed=int(y.sum()) - hits,
                recall_at_k=hits / y.sum() if y.sum() else None,
                tie_policy="Expected hits averaged over tied scores")


def demo(*, seed=SEED, training_days=60, capacity=500):
    if not 7 <= training_days <= 85:
        raise ValueError("training_days harus antara 7 dan 85.")
    world = generate_world(seed, cfg=replace(DEFAULT, chronological_submissions=True))
    cutoff = PERIOD_START + pd.Timedelta(days=training_days)
    history = world.claims[world.claims.submit_ts <= cutoff].copy()
    incoming = world.claims[world.claims.submit_ts > cutoff].copy()
    train_labels = world.labels[world.labels.claim_id.isin(history.claim_id)]
    model = train(history, world.faskes, world.affiliations, world.patients, train_labels,
                  cutoff=cutoff, seed=seed)
    scores = predict(model, incoming, as_of=incoming.submit_ts.max())
    # Outcomes are accessed only AFTER prediction, in this evaluation harness.
    outcomes = world.labels[world.labels.claim_id.isin(incoming.claim_id)]
    rules = rule_flags(incoming)
    baseline = pd.DataFrame({"claim_id": rules.index,
                             "priority_score": rules.rule_over_cap + rules.rule_same_day_dup})
    report = dict(data_version=DATA_VERSION, model=model.metadata,
                  test_start=incoming.submit_ts.min().isoformat(), test_end=incoming.submit_ts.max().isoformat(),
                  quality=require_valid(world.claims, world.faskes, world.affiliations, world.patients),
                  jala=evaluate(scores, outcomes, capacity=capacity),
                  rules=evaluate(baseline, outcomes, capacity=capacity),
                  limitations=["Synthetic data from the same generator family, not operational BPJS data.",
                               "One temporal holdout; reference tables are static synthetic snapshots.",
                               "The complete test batch is visible at batch close; not real-time prediction.",
                               "Historical labels are assumed available at training cutoff.",
                               "Scores are not calibrated probabilities; indicators are not model attributions.",
                               "This experiment does not replace the legacy grouped-CV benchmark."])
    return model, scores, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--training-days", type=int, default=60)
    parser.add_argument("--capacity", type=int, default=500)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    _, _, report = demo(seed=args.seed, training_days=args.training_days, capacity=args.capacity)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
