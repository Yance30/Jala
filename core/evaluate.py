"""Evaluasi JALA: skor dihitung kode, dibandingkan dengan label tersembunyi.

Tiga pemberi skor dibandingkan:
  rules     : mesin aturan per-klaim (cara lama)
  iforest   : Isolation Forest di atas fitur graf, TANPA label (unsupervised)
  graph_gbm : gradient boosting di atas fitur graf, dilatih dengan validasi silang PER KELOMPOK FASKES
              (cincin/jaringan fraud yang sama tidak pernah ada di data latih dan uji sekaligus)

Jalankan:  python -m core.evaluate            (ringkasan di terminal)
           python -m core.evaluate --seeds 5  (stabilitas antar seed)
           python -m core.evaluate --json docs/benchmark.json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score

from core.detect import FEATURES, build_features, rule_flags
from core.synthetic import SEED, World, generate_world

KS = (100, 250, 500, 1000)
CURVE_KS = list(range(0, 1201, 20))
N_FOLDS = 4

CAVEATS = [
    "Data 100% sintetis dan fraud disisipkan oleh pembangkit yang sama dengan yang membuat fitur-fiturnya; "
    "angka ini mengukur apakah logika deteksi bekerja pada pola yang didefinisikan, bukan akurasi di data BPJS nyata.",
    "Validasi silang dilakukan per kelompok faskes: cincin dan jaringan fraud yang sama tidak pernah dipakai melatih "
    "sekaligus menguji. Hanya ada 8 kelompok fraud, jadi variansnya tinggi.",
    "Baseline aturan adalah asumsi kami tentang mesin lama (plafon tarif dan klaim ganda hari yang sama), bukan sistem BPJS sebenarnya.",
    "Prevalensi fraud (≈4%) ditentukan pembangkit; precision@k bergantung padanya. Recall@k lebih tahan terhadap pilihan ini.",
    "Model yang diukur adalah fitur graf + gradient boosting, bukan GNN/HAN.",
]


@dataclass
class Benchmark:
    metrics: dict
    scored: pd.DataFrame     # satu baris per klaim: skor, fitur, label


def fold_assignment(world: World, n_folds: int = N_FOLDS) -> pd.Series:
    """Fold per faskes. Kelompok fraud dibagi bergilir menurut tipologi; faskes dalam satu kelompok
    selalu berada di fold yang sama."""
    fg = world.faskes_group
    groups = sorted(set(fg.values()))
    order = []
    for i in range(max(sum(g.startswith(t) for g in groups) for t in ("phantom", "repeat", "selfref"))):
        for t in ("phantom", "repeat", "selfref"):
            names = sorted(g for g in groups if g.startswith(t))
            if i < len(names):
                order.append(names[i])
    fold_of_group = {g: i % n_folds for i, g in enumerate(order)}
    rng = np.random.default_rng(world.seed)
    legit = [f for f in world.faskes.faskes_id if f not in fg]
    for i, f in enumerate(rng.permutation(legit)):
        fold_of_group[f] = i % n_folds
    return pd.Series({f: fold_of_group[fg.get(f, f)] for f in world.faskes.faskes_id})


def _cv_scores(X: pd.DataFrame, y: np.ndarray, fold: np.ndarray, seed: int) -> np.ndarray:
    oof = np.zeros(len(X))
    for k in range(N_FOLDS):
        tr, te = fold != k, fold == k
        m = HistGradientBoostingClassifier(max_depth=4, learning_rate=.08, max_iter=150,
                                           class_weight="balanced", random_state=seed)
        m.fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
    return oof


def expected_hits(y: np.ndarray, score: np.ndarray, ks) -> np.ndarray:
    """Jumlah fraud yang tertangkap di k teratas. Skor kembar (mis. aturan 0/1) dipecah rata (nilai harapan)."""
    order = np.argsort(-score, kind="stable")
    s, yy = score[order], y[order]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    ends = np.r_[starts[1:], len(s)]
    cum = np.r_[0, np.cumsum(yy)]
    out = []
    for k in ks:
        g = np.searchsorted(starts, k, "right") - 1
        full = cum[starts[g]]
        size = ends[g] - starts[g]
        out.append(full + (cum[ends[g]] - cum[starts[g]]) * min(k - starts[g], size) / size)
    return np.array(out)


def _summarize(y, score, ks=KS) -> dict:
    hits = expected_hits(y, score, ks)
    n_fraud = int(y.sum())
    return {
        "auc": float(roc_auc_score(y, score)),
        "ap": float(average_precision_score(y, score)),
        "precision_at_k": {int(k): float(h / k) for k, h in zip(ks, hits)},
        "recall_at_k": {int(k): float(h / n_fraud) for k, h in zip(ks, hits)},
        "curve": [float(v) for v in expected_hits(y, score, CURVE_KS) / n_fraud],
    }


def benchmark(seed: int = SEED, world: World | None = None) -> Benchmark:
    w = world or generate_world(seed)
    X = build_features(w.claims, w.faskes, w.affiliations, w.patients)
    lab = w.labels.set_index("claim_id").loc[X.index]
    y = lab.is_fraud.values.astype(int)
    R = rule_flags(w.claims).loc[X.index]
    fold = fold_assignment(w).reindex(w.claims.set_index("claim_id").loc[X.index, "faskes_id"]).values

    s_rules = (R.rule_over_cap + R.rule_same_day_dup).values.astype(float)
    s_gbm = _cv_scores(X, y, fold, seed)
    iso = IsolationForest(n_estimators=200, random_state=seed).fit(X)
    s_iso = -iso.score_samples(X)

    n = len(y)
    scorers = {"rules": s_rules, "iforest": s_iso, "graph_gbm": s_gbm}
    metrics = {
        "seed": seed, "n_claims": n, "n_fraud": int(y.sum()), "prevalence": float(y.mean()),
        "n_faskes": int(len(w.faskes)), "n_folds": N_FOLDS, "ks": list(KS), "curve_ks": CURVE_KS,
        "scorers": {k: _summarize(y, v) for k, v in scorers.items()},
        "random": {"recall_at_k": {int(k): k / n for k in KS}, "precision_at_k": {int(k): float(y.mean()) for k in KS},
                   "curve": [k / n for k in CURVE_KS]},
        "caveats": CAVEATS,
    }

    # per tipologi: tipologi itu vs klaim sah (fraud tipologi lain dikeluarkan)
    typ = lab.typology.values
    per_typ = {}
    for t in ("phantom", "repeat", "selfref"):
        m = (typ == t) | (y == 0)
        yt = (typ[m] == t).astype(int)
        per_typ[t] = {"n": int(yt.sum())}
        for name, sc in scorers.items():
            per_typ[t][name] = {"auc": float(roc_auc_score(yt, sc[m])), "ap": float(average_precision_score(yt, sc[m]))}
    metrics["per_typology"] = per_typ

    # fraud yang lolos aturan tetapi tertangkap jaringan (k=500)
    top_g = np.argsort(-s_gbm)[:500]
    caught = np.zeros(n, bool); caught[top_g] = True
    rule_hit = s_rules > 0
    metrics["graph_only_at_500"] = {
        "caught_by_graph": int((caught & (y == 1)).sum()),
        "of_which_missed_by_rules": int((caught & (y == 1) & ~rule_hit).sum()),
        "fraud_total_missed_by_rules": int(((y == 1) & ~rule_hit).sum()),
    }

    # tingkat faskes (untuk Risk Ranking)
    sc = pd.DataFrame({"faskes_id": w.claims.set_index("claim_id").loc[X.index, "faskes_id"].values,
                       "s": s_gbm, "y": y})
    fa = sc.groupby("faskes_id").agg(risk=("s", lambda v: float(np.mean(np.sort(v)[::-1][:max(5, len(v) // 10)]))),
                                    fraud=("y", "max"), n=("y", "size"))
    top10 = fa.sort_values("risk", ascending=False).head(10)
    metrics["faskes_level"] = {
        "n_fraud_faskes": int(fa.fraud.sum()),
        "auc": float(roc_auc_score(fa.fraud, fa.risk)),
        "precision_at_10": float(top10.fraud.mean()),
    }

    # Audit kelompok sintetis: false-positive rate di tingkat klaim pada ambang skor 0.5.
    # Ini audit data pembangkit, bukan bukti keadilan pada data operasional.
    facility_meta = w.faskes.set_index("faskes_id")[["type", "region"]]
    audit = pd.DataFrame({"faskes_id": sc.faskes_id, "score": s_gbm, "fraud": y})
    audit = audit.join(facility_meta, on="faskes_id")
    audit["false_positive"] = (audit.score >= 0.5) & (audit.fraud == 0)
    metrics["fairness_synthetic"] = {
        "threshold": 0.5,
        "by_type": [{"group": str(k), "n_claims": int(len(g)), "n_legit": int((g.fraud == 0).sum()),
                     "false_positive_rate": float(g.loc[g.fraud == 0, "false_positive"].mean())
                     if (g.fraud == 0).any() else 0.0}
                    for k, g in audit.groupby("type", sort=True)],
        "by_region": [{"group": str(k), "n_claims": int(len(g)), "n_legit": int((g.fraud == 0).sum()),
                       "false_positive_rate": float(g.loc[g.fraud == 0, "false_positive"].mean())
                       if (g.fraud == 0).any() else 0.0}
                      for k, g in audit.groupby("region", sort=True)],
        "caveat": "Audit pada data sintetis seed tetap; bukan bukti keadilan atau dampak di data operasional.",
    }

    # AUC per fitur (satu fitur saja) -> tunjukkan tidak ada fitur tunggal yang membocorkan label
    aucs = {c: float(max(roc_auc_score(y, X[c]), 1 - roc_auc_score(y, X[c]))) for c in FEATURES}
    metrics["single_feature_auc"] = dict(sorted(aucs.items(), key=lambda kv: -kv[1]))

    scored = X.copy()
    scored["score_graph"], scored["score_iforest"], scored["score_rules"] = s_gbm, s_iso, s_rules
    scored["is_fraud"], scored["typology"] = y, typ
    scored["faskes_id"] = w.claims.set_index("claim_id").loc[X.index, "faskes_id"].values
    return Benchmark(metrics, scored)


def multi_seed(seeds) -> dict:
    rows = []
    for s in seeds:
        m = benchmark(s).metrics
        rows.append({"seed": s,
                     "auc_graph": m["scorers"]["graph_gbm"]["auc"], "auc_rules": m["scorers"]["rules"]["auc"],
                     "auc_iforest": m["scorers"]["iforest"]["auc"],
                     "recall500_graph": m["scorers"]["graph_gbm"]["recall_at_k"][500],
                     "recall500_rules": m["scorers"]["rules"]["recall_at_k"][500],
                     "recall500_random": m["random"]["recall_at_k"][500],
                     "recall1000_graph": m["scorers"]["graph_gbm"]["recall_at_k"][1000],
                     "recall1000_rules": m["scorers"]["rules"]["recall_at_k"][1000],
                     "recall1000_random": m["random"]["recall_at_k"][1000]})
    df = pd.DataFrame(rows)
    return {"per_seed": rows, "mean": df.drop(columns="seed").mean().to_dict(),
            "std": df.drop(columns="seed").std().to_dict()}


def _print(m: dict) -> None:
    print(f"{m['n_claims']} klaim, {m['n_fraud']} fraud ({m['prevalence']:.1%}), {m['n_faskes']} faskes")
    print(f"{'':12s}{'AUC':>7s}{'AP':>7s}" + "".join(f"{'R@'+str(k):>8s}" for k in m['ks']) + "".join(f"{'P@'+str(k):>8s}" for k in m['ks']))
    for name, s in m["scorers"].items():
        print(f"{name:12s}{s['auc']:7.3f}{s['ap']:7.3f}" + "".join(f"{s['recall_at_k'][k]:8.1%}" for k in m['ks'])
              + "".join(f"{s['precision_at_k'][k]:8.1%}" for k in m['ks']))
    r = m["random"]
    print(f"{'random':12s}{0.5:7.3f}{m['prevalence']:7.3f}" + "".join(f"{r['recall_at_k'][k]:8.1%}" for k in m['ks'])
          + "".join(f"{r['precision_at_k'][k]:8.1%}" for k in m['ks']))
    for t, v in m["per_typology"].items():
        print(f"  {t:8s} n={v['n']:4d} " + "  ".join(f"{k}: AUC {v[k]['auc']:.3f} AP {v[k]['ap']:.3f}" for k in ("rules", "iforest", "graph_gbm")))
    print("graph-only@500:", m["graph_only_at_500"])
    print("tingkat faskes:", m["faskes_level"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=0, help="jalankan N seed berbeda (stabilitas)")
    ap.add_argument("--json", help="tulis metrik ke berkas JSON")
    a = ap.parse_args()
    bm = benchmark()
    _print(bm.metrics)
    out = {"main": bm.metrics}
    if a.seeds:
        ms = multi_seed(range(1, a.seeds + 1))
        print("\nstabilitas antar seed:", json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in ms.items() if k != "per_seed"}, indent=1))
        out["multi_seed"] = ms
    if a.json:
        import os
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        json.dump(out, open(a.json, "w"), indent=1)
        print("ditulis:", a.json)
