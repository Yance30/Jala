"""Strict CSV adapter for external test datasets; no silent row dropping.

All timestamps are normalized to UTC without timezone. Naive timestamps are
interpreted as UTC. A rejected package is not partially scored.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, replace
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

from core import batch
from core.contract import MINIMAL
from core.data_quality import require_valid
from core.detect import assert_no_labels, rule_flags
from core.workload import require_budget

MAX_FILE_BYTES = 5_000_000


@dataclass
class Dataset:
    tables: dict
    labels: pd.DataFrame | None
    tariff_caps: dict
    provenance: dict


def _csv(raw: bytes, name: str, mapping: dict) -> pd.DataFrame:
    text = raw.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text), strict=True)
    try:
        header = next(reader, [])
    except csv.Error as error:
        raise ValueError(f"{name}: header CSV tidak valid.") from error
    if not header or len(header) != len(set(header)):
        raise ValueError(f"{name}: header kosong atau duplikat.")
    try:
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(f"{name}: jumlah kolom tidak sesuai pada record {line_number}.")
    except csv.Error as error:
        raise ValueError(f"{name}: struktur CSV tidak valid.") from error
    if not isinstance(mapping, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()):
        raise ValueError(f"{name}: mapping harus source_column → canonical_column.")
    if not set(mapping).issubset(header):
        raise ValueError(f"{name}: kolom sumber mapping tidak ditemukan.")
    frame = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if name != "labels":
        assert_no_labels(frame)
    frame = frame.rename(columns=mapping)
    if frame.columns.duplicated().any():
        raise ValueError(f"{name}: mapping menghasilkan kolom duplikat.")
    if name != "labels":
        assert_no_labels(frame)
    expected = MINIMAL[name] if name in MINIMAL else ["claim_id", "is_fraud"]
    if set(frame.columns) != set(expected):
        raise ValueError(f"{name}: gunakan tepat kolom kontrak: {', '.join(expected)}.")
    # Preserve string identifiers (including leading zeros); normalize only surrounding whitespace.
    for column in frame:
        frame[column] = frame[column].str.strip().replace("", None)
    for column in ("tarif", "capacity", "is_fraud"):
        if column in frame:
            try:
                frame[column] = pd.to_numeric(frame[column], errors="raise")
            except (ValueError, TypeError) as error:
                raise ValueError(f"{name}.{column}: nilai numerik tidak valid.") from error
    for column in ("visit_ts", "submit_ts"):
        if column in frame:
            try:
                frame[column] = pd.to_datetime(frame[column], format="ISO8601", utc=True, errors="raise").dt.tz_convert(None)
            except (ValueError, TypeError) as error:
                raise ValueError(f"{name}.{column}: waktu ISO 8601 tidak valid.") from error
    return frame


def load(files: dict[str, bytes]) -> Dataset:
    required = {f"{name}.csv" for name in MINIMAL} | {"tariff_caps.json"}
    if not required.issubset(files):
        raise ValueError("File wajib belum lengkap: " + ", ".join(sorted(required - set(files))))
    if set(files) - required - {"mapping.json", "labels.csv"}:
        raise ValueError("Paket memuat nama file yang tidak dikenal.")
    if any(len(raw) > MAX_FILE_BYTES for raw in files.values()):
        raise ValueError("Setiap file dibatasi 5 MB.")
    mapping = json.loads(files.get("mapping.json", b"{}"))
    if not isinstance(mapping, dict) or set(mapping) - set(MINIMAL) - {"labels"}:
        raise ValueError("mapping.json harus berisi nama tabel yang dikenali.")
    tables = {name: _csv(files[f"{name}.csv"], name, mapping.get(name, {})) for name in MINIMAL}
    require_valid(**tables)
    require_budget(**tables)
    caps = json.loads(files["tariff_caps.json"])
    if not isinstance(caps, dict) or not caps or any(
        not isinstance(v, (int, float)) or isinstance(v, bool) or not np.isfinite(v) or v <= 0
        for v in caps.values()
    ):
        raise ValueError("tariff_caps.json harus berupa pemetaan kode ke angka positif terbatas.")
    if not tables["claims"].icd.isin(caps).all():
        raise ValueError("Referensi tarif belum mencakup seluruh kode diagnosis.")
    labels = _csv(files["labels.csv"], "labels", mapping.get("labels", {})) if "labels.csv" in files else None
    if labels is not None:
        if (labels.claim_id.isna().any() or labels.claim_id.duplicated().any()
                or not labels.is_fraud.isin([0, 1]).all()
                or not labels.claim_id.isin(tables["claims"].claim_id).all()):
            raise ValueError("Label harus unik, biner, dan terkait dengan klaim dalam paket.")
    return Dataset(tables, labels, dict(caps), {
        "adapter_version": "csv-v1", "timestamps": "UTC; naive input interpreted as UTC",
        "files_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())},
        "rows": {name: len(frame) for name, frame in tables.items()},
    })


def run_holdout(dataset: Dataset, *, cutoff, capacity=500, feature_set="base"):
    cutoff = pd.Timestamp(cutoff)
    if cutoff.tzinfo is not None:
        cutoff = cutoff.tz_convert("UTC").tz_localize(None)
    tables = dataset.tables
    claims = tables["claims"]
    historical = claims[claims.submit_ts <= cutoff].copy()
    incoming = claims[claims.submit_ts > cutoff].copy()
    if pd.isna(cutoff) or historical.empty or incoming.empty or dataset.labels is None:
        raise ValueError("Perlu klaim sebelum dan setelah cutoff, serta labels.csv untuk data latih.")
    labels = dataset.labels
    refs = {name: frame for name, frame in tables.items() if name != "claims"}
    model = batch.train(historical, **refs, labels=labels[labels.claim_id.isin(historical.claim_id)],
                        cutoff=cutoff, tariff_caps=dataset.tariff_caps, feature_set=feature_set)
    scores = batch.predict(model, incoming, as_of=incoming.submit_ts.max())
    report = {"provenance": dataset.provenance, "model": model.metadata,
              "test_start": incoming.submit_ts.min().isoformat(), "test_end": incoming.submit_ts.max().isoformat(),
              "n_predicted": len(scores), "evaluation_available": False,
              "limitations": ["External test package, not a verified BPJS integration.",
                              "Historical labels assumed available at cutoff; reference tables are static.",
                              "Complete current batch visible at close; not streaming inference."]}
    outcomes = labels[labels.claim_id.isin(incoming.claim_id)]
    if set(outcomes.claim_id) == set(incoming.claim_id):
        report["evaluation_available"] = True
        report["jala"] = batch.evaluate(scores, outcomes, capacity=capacity)
        rules = rule_flags(incoming, tariff_caps=dataset.tariff_caps)
        baseline = pd.DataFrame({"claim_id": rules.index,
                                 "priority_score": rules.rule_over_cap + rules.rule_same_day_dup})
        report["rules"] = batch.evaluate(baseline, outcomes, capacity=capacity)
    return model, scores, report


def predict_saved(dataset: Dataset, model, *, capacity=500, observations=None, retain_observations=False):
    """Use a fixed saved model on an entirely new batch; labels are evaluation-only."""
    if dataset.tariff_caps != model.tariff_caps:
        raise ValueError("Referensi tarif berbeda dari model tersimpan; gunakan referensi asal atau latih model baru.")
    claims = dataset.tables["claims"]
    refs = {k: v.copy() for k, v in dataset.tables.items() if k != "claims"}
    previous = claims.iloc[:0].copy()
    if observations:
        if claims.submit_ts.max() < pd.Timestamp(observations["as_of"]):
            raise ValueError("Batch lebih lama daripada snapshot terakhir; gunakan model terpisah untuk replay historis.")
        previous = pd.DataFrame(observations["claims"])
        for column in ("visit_ts", "submit_ts"):
            previous[column] = pd.to_datetime(previous[column])
        overlap = set(previous.claim_id) & set(claims.claim_id)
        if overlap:
            a = previous.set_index("claim_id").loc[sorted(overlap), MINIMAL["claims"][1:]].fillna("")
            b = claims.set_index("claim_id").loc[sorted(overlap), MINIMAL["claims"][1:]].fillna("")
            try:
                pd.testing.assert_frame_equal(a, b, check_dtype=False, check_exact=True)
            except AssertionError:
                raise ValueError("Klaim lama diubah; buat snapshot/model baru untuk koreksi, jangan timpa riwayat.")
        for name in refs:
            refs[name] = pd.concat([pd.DataFrame(observations["references"][name]), refs[name]],
                                   ignore_index=True).drop_duplicates()
    history = pd.concat([model.history, previous[~previous.claim_id.isin(claims.claim_id)]], ignore_index=True)
    working_model = replace(model, history=history)
    scores = batch.predict(working_model, claims, as_of=claims.submit_ts.max(), references=refs)
    report = dict(provenance=dataset.provenance, model=model.metadata, n_predicted=len(scores),
                  n_previous_observations=len(previous), evaluation_available=False,
                  inference="Saved model; no retraining",
                  context="Prior observed batches included" if observations else "Training history and current batch")
    cumulative = pd.concat([previous[~previous.claim_id.isin(claims.claim_id)], claims], ignore_index=True)
    if retain_observations:
        serial = cumulative.astype(object).where(pd.notna(cumulative), None)
        for column in ("visit_ts", "submit_ts"):
            serial[column] = cumulative[column].map(lambda value: value.isoformat())
        report["_observations"] = dict(as_of=claims.submit_ts.max().isoformat(),
            claims=serial.to_dict("records"),
            references={name: frame.astype(object).where(pd.notna(frame), None).to_dict("records")
                        for name, frame in refs.items()})
    if dataset.labels is not None and set(dataset.labels.claim_id) == set(claims.claim_id):
        report["evaluation_available"] = True
        report["jala"] = batch.evaluate(scores, dataset.labels, capacity=capacity)
        rules = rule_flags(claims, tariff_caps=model.tariff_caps)
        report["rules"] = batch.evaluate(pd.DataFrame(dict(claim_id=rules.index,
                            priority_score=rules.rule_over_cap + rules.rule_same_day_dup)), dataset.labels, capacity=capacity)
    return model, scores, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--capacity", type=int, default=500)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    allowed = [f"{name}.csv" for name in MINIMAL] + ["labels.csv", "mapping.json", "tariff_caps.json"]
    files = {}
    for name in allowed:
        path = args.input / name
        if path.is_file():
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError(f"{name} melebihi 5 MB.")
            files[name] = path.read_bytes()
    _, _, report = run_holdout(load(files), cutoff=args.cutoff, capacity=args.capacity)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{report['n_predicted']} claims scored; evaluation_available={report['evaluation_available']}; report: {args.json}")


if __name__ == "__main__":
    main()
