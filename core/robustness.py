"""Uji ketahanan JALA: menjawab keberatan "fraud-nya disisipkan sendiri, jadi wajar kalau terdeteksi".

Lima pemeriksaan, semuanya dihitung kode dan memakai label tersembunyi hanya untuk MENGUKUR:

  1. ablation        fitur per-klaim saja vs + riwayat vs + relasi graf: apakah jaringan benar-benar menambah nilai?
  2. transfer        latih di dunia A, uji di dunia B yang distribusinya bergeser (seed, ukuran cincin, jam kirim,
                     domisili, selisih tarif, dst. berbeda). Model TIDAK dilatih ulang.
  3. evasion         fraud yang sengaja menghindari fitur (kiriman dipecah, kunjungan disebar, domisili setempat, dst.)
                     pada 5 tingkat; model dunia utama diuji tanpa pembaruan, dan juga dilatih ulang (bertahan).
  4. false_positives dari 500 klaim teratas, berapa yang sah, dan klaim sah jenis apa yang paling sering salah ditandai.
  5. repeat_before_after   fitur v1 (19) vs v2 (22) untuk Repeat Billing, di dunia utama, dunia bergeser, dan transfer.

Batasan yang tidak bisa dihapus oleh uji ini: dunia B dan fraud menghindar tetap dibuat oleh keluarga pembangkit
yang sama (parameter berbeda, bukan data nyata). Uji ini mengukur ketahanan terhadap pergeseran parameter, bukan
akurasi di data BPJS.

Jalankan:  python -m core.robustness --json docs/robustness.json
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score

from core.detect import FEATURES, FEATURES_REPEAT, FEATURES_V1, build_features, rule_flags
from core.evaluate import N_FOLDS, _cv_scores, expected_hits, fold_assignment
from core.synthetic import DEFAULT, SEED, SHIFTED, World, WorldConfig, evasive_config, generate_world

SEED_SHIFTED = 777
SEED_TRAIN = 11      # dunia pelatihan model "beku": seed berbeda dari dunia uji agar klaim sah tidak identik
LEVELS = (0.0, 0.25, 0.5, 0.75, 1.0)
K = 500

# Pengelompokan fitur menurut informasi yang dibutuhkan untuk menghitungnya
# per_klaim        : cukup satu baris klaim (+ domisili peserta)
# agregat_entitas  : ringkasan klaim MILIK SATU entitas (peserta atau dokter): jumlah klaim, jumlah faskes, jarak ke klaim
#                    sebelumnya. Ini setara derajat node pada graf, fitur graf paling murah.
# relasi_multi     : butuh catatan entitas LAIN: dokter yang sama di faskes lain pada jam sama, komponen terhubung,
#                    rujukan dua arah, normalisasi terhadap faskes sejenis, pasangan faskes yang saling menagih ulang
G_PER_CLAIM = ["f_out_region", "f_tarif_ratio", "f_ref"]
G_ENTITY = ["f_pat_total", "f_pat_nfaskes", "f_gap_prev_h", "f_dup_recent", "f_doc_nfaskes", "f_tarif_match_prev"]
G_RELATIONAL = [f for f in FEATURES if f not in G_PER_CLAIM + G_ENTITY]
GROUPS = {"per_klaim": G_PER_CLAIM, "agregat_entitas": G_ENTITY, "relasi_multi_entitas": G_RELATIONAL}

CAVEATS = [
    "Dunia B, fraud menghindar, dan dunia utama dibuat oleh keluarga pembangkit yang sama. Pergeseran yang diuji "
    "adalah pergeseran PARAMETER, bukan pola fraud yang benar-benar baru. Ini bukan bukti akurasi di data BPJS.",
    "Tiga fitur Repeat Billing (v2) dirancang setelah melihat mekanisme pembangkit (klaim ulang meniru tarif klaim asli). "
    "Peningkatannya bisa terlalu optimistis; dunia B memakai selisih tarif lebih besar (±8% vs ±3%) untuk menguji hal ini.",
    "Hanya 8 kelompok fraud (3 phantom, 3 repeat, 2 selfref). Selisih kecil antar konfigurasi bisa berasal dari "
    "pembagian fold, bukan dari fitur.",
    "Pada fraud menghindar, penurunan metrik di sini adalah batas bawah yang jujur untuk pembangkit ini; "
    "penyerang nyata dapat memakai strategi yang tidak diwakili pembangkit.",
]


@dataclass
class Prepared:
    world: World
    X: pd.DataFrame
    y: np.ndarray
    typ: np.ndarray
    kind: np.ndarray
    fold: np.ndarray
    rules: np.ndarray


def prepare(world: World) -> Prepared:
    X = build_features(world.claims, world.faskes, world.affiliations, world.patients)
    lab = world.labels.set_index("claim_id").loc[X.index]
    fold = fold_assignment(world).reindex(world.claims.set_index("claim_id").loc[X.index, "faskes_id"]).values
    R = rule_flags(world.claims).loc[X.index]
    return Prepared(world, X, lab.is_fraud.values.astype(int), lab.typology.values, lab.legit_kind.values, fold,
                    (R.rule_over_cap + R.rule_same_day_dup).values.astype(float))


def _block(y, s, typ) -> dict:
    n = len(y)
    k3 = int(round(0.03 * n))
    out = {
        "auc": float(roc_auc_score(y, s)), "ap": float(average_precision_score(y, s)),
        "recall_at_500": float(expected_hits(y, s, (K,))[0] / y.sum()),
        "recall_at_3pct": float(expected_hits(y, s, (k3,))[0] / y.sum()), "k_3pct": k3,
        # k = jumlah fraud sebenarnya: bisa dibandingkan antar dunia yang jumlah fraudnya berbeda
        "r_precision": float(expected_hits(y, s, (int(y.sum()),))[0] / y.sum()),
        "per_typology": {},
    }
    for t in ("phantom", "repeat", "selfref"):
        m = (typ == t) | (y == 0)
        if (typ == t).sum() > 0:
            yt = (typ[m] == t).astype(int)
            out["per_typology"][t] = {"auc": float(roc_auc_score(yt, s[m])), "ap": float(average_precision_score(yt, s[m]))}
    return out


def _fit_predict(Xa, ya, Xb, seed):
    m = HistGradientBoostingClassifier(max_depth=4, learning_rate=.08, max_iter=150, class_weight="balanced",
                                       random_state=seed)
    m.fit(Xa, ya)
    return m.predict_proba(Xb)[:, 1]


def _score_world(p: Prepared, cols: list, seed: int) -> np.ndarray:
    return _cv_scores(p.X[cols], p.y, p.fold, seed)


# ---------------------------------------------------------------------------
def ablation(p: Prepared, seed: int = SEED) -> dict:
    sets = {
        "A. per-klaim saja": G_PER_CLAIM,
        "B. + agregat entitas (derajat)": G_PER_CLAIM + G_ENTITY,
        "C. + relasi multi-entitas (JALA penuh)": FEATURES,
    }
    out = {name: _block(p.y, _score_world(p, cols, seed), p.typ) | {"n_features": len(cols)} for name, cols in sets.items()}
    loo = {}
    for g, cols in GROUPS.items():
        keep = [f for f in FEATURES if f not in cols]
        loo[f"tanpa {g}"] = _block(p.y, _score_world(p, keep, seed), p.typ) | {"n_features": len(keep)}
    return {"bertahap": out, "leave_one_group_out": loo, "groups": {g: len(c) for g, c in GROUPS.items()}}


def transfer(a: Prepared, b: Prepared, seed: int = SEED, cols: list | None = None) -> dict:
    cols = cols or FEATURES
    s_jala = _fit_predict(a.X[cols], a.y, b.X[cols], seed)
    iso = IsolationForest(n_estimators=200, random_state=seed).fit(b.X[cols])
    return {
        "jala_transfer": _block(b.y, s_jala, b.typ),
        "iforest": _block(b.y, -iso.score_samples(b.X[cols]), b.typ),
        "rules": _block(b.y, b.rules, b.typ),
        "n_claims": int(len(b.y)), "n_fraud": int(b.y.sum()),
    }


def evasion(main: Prepared, train: Prepared, seed: int = SEED, levels=LEVELS) -> list:
    """train = dunia default dengan seed lain. Model beku dilatih di sana dan diuji di dunia uji (seed utama)
    pada tiap tingkat penghindaran; pada level 0 dunia ujinya = dunia utama."""
    rows = []
    for L in levels:
        p = main if L == 0 else prepare(generate_world(SEED, cfg=evasive_config(L)))
        frozen = _fit_predict(train.X[FEATURES], train.y, p.X[FEATURES], seed)
        retrained = _score_world(p, FEATURES, seed)
        rows.append({
            "level": L, "n_fraud": int(p.y.sum()),
            "model_beku": _block(p.y, frozen, p.typ),          # dilatih di dunia seed lain, tanpa pembaruan
            "model_dilatih_ulang": _block(p.y, retrained, p.typ),  # defender beradaptasi (validasi silang per kelompok)
            "rules": _block(p.y, p.rules, p.typ),
        })
    return rows


def false_positives(p: Prepared, scores: np.ndarray, k: int = K) -> dict:
    top = np.argsort(-scores, kind="stable")[:k]
    flagged = np.zeros(len(scores), bool)
    flagged[top] = True
    legit = p.y == 0
    pct = pd.Series(scores).rank(pct=True).values
    kinds = {}
    for kd in sorted(set(p.kind[legit])):
        m = legit & (p.kind == kd)
        name = kd or "(sah, tanpa pola khusus)"
        kinds[name] = {"n": int(m.sum()), "salah_ditandai": int((flagged & m).sum()),
                       "fp_rate": float((flagged & m).sum() / m.sum()), "persentil_skor_rata2": float(pct[m].mean())}
    return {
        "k": k, "fraud_di_top_k": int((flagged & ~legit).sum()), "sah_di_top_k": int((flagged & legit).sum()),
        "precision_at_k": float((flagged & ~legit).sum() / k),
        "fp_rate_semua_sah": float((flagged & legit).sum() / legit.sum()),
        "per_jenis_sah": dict(sorted(kinds.items(), key=lambda kv: -kv[1]["salah_ditandai"])),
    }


def repeat_before_after(main: Prepared, shifted: Prepared, seed: int = SEED) -> dict:
    out = {}
    for name, cols in (("v1_19_fitur", FEATURES_V1), ("v2_22_fitur", FEATURES)):
        cv_main = _block(main.y, _score_world(main, cols, seed), main.typ)
        cv_shift = _block(shifted.y, _score_world(shifted, cols, seed), shifted.typ)
        tr = transfer(main, shifted, seed, cols)["jala_transfer"]
        out[name] = {"dunia_utama_cv": cv_main, "dunia_bergeser_cv": cv_shift, "transfer_A_ke_B": tr}
    out["fitur_baru"] = FEATURES_REPEAT
    return out


def repeat_multi_seed(seeds=(1, 2, 3, 4, 5)) -> dict:
    """v1 vs v2 di beberapa dunia (seed berbeda). Satu seed saja tidak cukup: hanya 3 kelompok repeat per dunia."""
    rows = []
    for sd in seeds:
        p = prepare(generate_world(sd))
        r = {"seed": sd}
        for name, cols in (("v1", FEATURES_V1), ("v2", FEATURES)):
            b = _block(p.y, _score_world(p, cols, sd), p.typ)
            r[name] = {"ap_repeat": b["per_typology"]["repeat"]["ap"], "auc_repeat": b["per_typology"]["repeat"]["auc"],
                       "ap_all": b["ap"], "auc_all": b["auc"], "r_precision": b["r_precision"]}
        rows.append(r)
    mean = {n: {k: float(np.mean([r[n][k] for r in rows])) for k in rows[0]["v1"]} for n in ("v1", "v2")}
    return {"per_seed": rows, "mean": mean}


# ---------------------------------------------------------------------------
def run(seed: int = SEED, verbose: bool = False) -> dict:
    def log(msg):
        if verbose:
            print(msg, flush=True)

    log("dunia utama ...")
    main = prepare(generate_world(seed))
    log("dunia bergeser (B) ...")
    shifted = prepare(generate_world(SEED_SHIFTED, cfg=SHIFTED))
    s_main = _score_world(main, FEATURES, seed)
    log("ablasi ...")
    res = {
        "meta": {"seed": seed, "seed_shifted": SEED_SHIFTED, "seed_train_frozen": SEED_TRAIN, "n_claims_main": int(len(main.y)),
                 "n_fraud_main": int(main.y.sum()), "n_claims_shifted": int(len(shifted.y)),
                 "n_fraud_shifted": int(shifted.y.sum()), "k": K, "n_folds": N_FOLDS,
                 "shifted_config": {k: v for k, v in SHIFTED.__dict__.items() if getattr(DEFAULT, k) != v},
                 "evasive_level_1_config": {k: v for k, v in evasive_config(1).__dict__.items() if getattr(DEFAULT, k) != v}},
        "main": _block(main.y, s_main, main.typ),
        "ablation": ablation(main, seed),
    }
    log("transfer A -> B, B -> A ...")
    res["transfer"] = {"A_ke_B": transfer(main, shifted, seed), "B_ke_A": transfer(shifted, main, seed),
                       "cv_dalam_B": _block(shifted.y, _score_world(shifted, FEATURES, seed), shifted.typ)}
    log("fraud menghindar ...")
    res["evasion"] = evasion(main, prepare(generate_world(SEED_TRAIN)), seed)
    log("false positive ...")
    res["false_positives"] = false_positives(main, s_main)
    log("repeat sebelum/sesudah ...")
    res["repeat_before_after"] = repeat_before_after(main, shifted, seed)
    log("repeat multi-seed ...")
    res["repeat_before_after"]["multi_seed"] = repeat_multi_seed()
    res["caveats"] = CAVEATS
    return res


def _print(r: dict) -> None:
    f = lambda b: f"AUC {b['auc']:.3f}  AP {b['ap']:.3f}  R@500 {b['recall_at_500']:.1%}  Rprec {b['r_precision']:.1%}"
    print("\n== Ablasi (CV per kelompok faskes)")
    for k, v in {**r["ablation"]["bertahap"], **r["ablation"]["leave_one_group_out"]}.items():
        print(f"  {k:40s} {f(v)}  | AP/tipologi " + " ".join(f"{t[:3]}={x['ap']:.2f}" for t, x in v["per_typology"].items()))
    print("\n== Transfer (model dunia A tanpa dilatih ulang)")
    for d in ("A_ke_B", "B_ke_A"):
        t = r["transfer"][d]
        print(f"  {d}: JALA {f(t['jala_transfer'])} | iforest {t['iforest']['auc']:.3f} | rules {t['rules']['auc']:.3f}")
    print(f"  CV dalam B: {f(r['transfer']['cv_dalam_B'])}")
    print("\n== Fraud menghindar")
    for e in r["evasion"]:
        print(f"  level {e['level']:.2f} (n_fraud {e['n_fraud']}): beku {f(e['model_beku'])} | ulang {f(e['model_dilatih_ulang'])} | rules R@500 {e['rules']['recall_at_500']:.1%}")
    fp = r["false_positives"]
    print(f"\n== False positive @ {fp['k']}: fraud {fp['fraud_di_top_k']}, sah {fp['sah_di_top_k']}")
    for k, v in list(fp["per_jenis_sah"].items())[:6]:
        print(f"  {k:28s} n={v['n']:5d} salah={v['salah_ditandai']:3d} fp_rate={v['fp_rate']:.1%}")
    print("\n== Repeat Billing sebelum/sesudah (AP)")
    ms = r["repeat_before_after"]["multi_seed"]["mean"]
    print(f"  rata-rata 5 seed: v1 AP repeat {ms['v1']['ap_repeat']:.3f} | v2 {ms['v2']['ap_repeat']:.3f}")
    for k in ("v1_19_fitur", "v2_22_fitur"):
        v = r["repeat_before_after"][k]
        print(f"  {k}: utama {v['dunia_utama_cv']['per_typology']['repeat']['ap']:.3f} | bergeser(CV) {v['dunia_bergeser_cv']['per_typology']['repeat']['ap']:.3f} | transfer {v['transfer_A_ke_B']['per_typology']['repeat']['ap']:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="tulis hasil ke berkas JSON")
    a = ap.parse_args()
    res = run(verbose=True)
    _print(res)
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
        print("ditulis:", a.json)
