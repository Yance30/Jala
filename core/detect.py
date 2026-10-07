"""Fitur graf + skor risiko klaim JALA.

Aturan keras: modul ini HANYA membaca kolom yang teramati (klaim, faskes, afiliasi SIP, peserta).
Kolom label (is_fraud, typology, group) ditolak oleh `assert_no_labels`.

Relasi yang dipakai (graf heterogen Peserta-Dokter-Faskes-ICD, dihitung tanpa Neo4j):
  * dokter <-> faskes  : afiliasi SIP dan faskes tempat ia menagih
  * faskes -> faskes   : rujukan (arah), rujukan balik, dan "konkurensi dokter" (satu dokter, banyak faskes, jam sama)
  * peserta <-> faskes : domisili vs wilayah faskes, riwayat kunjungan
Fitur dinormalisasi terhadap faskes sejenis (peer group) agar RS besar tidak otomatis dianggap mencurigakan.

Catatan: ini BUKAN GNN/HAN. Ini fitur graf + model pohon (gradient boosting) dan Isolation Forest,
sebagai prototipe yang terukur. HAN adalah arsitektur target.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import networkx as nx

from core import contract
from core.synthetic import ICD_CAP

LABEL_COLS = {"is_fraud", "typology", "group", "label", "fraud", "legit_kind"}

FEATURES = [
    "f_out_region",         # domisili peserta != wilayah faskes
    "f_faskes_oor_z",       # porsi peserta luar wilayah di faskes ini vs faskes sejenis (z)
    "f_pat_total",          # total klaim peserta di seluruh jaringan
    "f_pat_nfaskes",        # jumlah faskes berbeda yang dikunjungi peserta
    "f_burst",              # klaim dari faskes sama yang dikirim dalam +-60 detik
    "f_burst_z",            # idem, dinormalisasi per tipe faskes
    "f_doc_conc",           # faskes lain tempat dokter yang sama menagih dalam +-30 menit
    "f_doc_nfaskes",        # jumlah faskes tempat dokter menagih
    "f_conc_component",     # ukuran komponen faskes yang terhubung lewat konkurensi dokter
    "f_gap_prev_h",         # jam sejak klaim sebelumnya (peserta + ICD sama)
    "f_dup_recent",         # ada klaim sama < 48 jam sebelumnya
    "f_dup_cross",          # ... dan klaim sebelumnya di faskes lain
    "f_ref",                # klaim berasal dari rujukan
    "f_ref_internal",       # dokter perujuk terdaftar (SIP) di faskes tujuan
    "f_doc_ref_internal",   # porsi rujukan dokter itu yang berakhir di faskes terafiliasinya
    "f_ref_doc_share",      # porsi rujukan ke faskes ini yang berasal dari dokter itu
    "f_ref_reciprocity",    # rujukan dua arah antar pasangan faskes (min/max)
    "f_tarif_ratio",        # tarif / plafon
    "f_volume_z",           # klaim per kapasitas vs faskes sejenis (z)
]

# Fitur tambahan untuk Repeat Billing (titik terlemah di v1). Dua dari tiga memakai relasi antar-faskes.
FEATURES_REPEAT = [
    "f_tarif_match_prev",   # selisih relatif tarif vs klaim sebelumnya (peserta + ICD sama, < 48 jam); 1.0 jika tidak ada
    "f_dup_pair_cross",     # berapa kali pasangan faskes (sebelumnya -> ini) saling menagih ulang peserta < 48 jam
    "f_dup_faskes_z",       # porsi klaim ulang < 48 jam di faskes ini vs faskes sejenis (z)
]
FEATURES_V1 = list(FEATURES)            # sebelum perbaikan Repeat Billing (untuk perbandingan sebelum/sesudah)
FEATURES = FEATURES_V1 + FEATURES_REPEAT


def assert_no_labels(*frames: pd.DataFrame) -> None:
    for fr in frames:
        bad = LABEL_COLS & set(fr.columns)
        if bad:
            raise ValueError(f"Kolom label bocor ke detektor: {sorted(bad)}")


def _z_by_group(values: pd.Series, groups: pd.Series) -> pd.Series:
    g = values.groupby(groups)
    return ((values - g.transform("mean")) / (g.transform("std").fillna(0) + 1e-6)).clip(-6, 12)


def _within(sorted_t: np.ndarray, t: np.ndarray, w: float):
    return np.searchsorted(sorted_t, t - w, "left"), np.searchsorted(sorted_t, t + w, "right")


def build_features(claims, faskes, affiliations, patients) -> pd.DataFrame:
    assert_no_labels(claims, faskes, affiliations, patients)
    contract.validate(claims, faskes, affiliations, patients)
    t0 = claims.visit_ts.min()
    df = (claims.merge(faskes[["faskes_id", "type", "region", "capacity"]], on="faskes_id", how="left")
                .merge(patients, on="patient_id", how="left"))
    df["visit_s"] = (df.visit_ts - t0).dt.total_seconds()
    df["submit_s"] = (df.submit_ts - t0).dt.total_seconds()
    out = pd.DataFrame(index=df.claim_id.values)

    # --- peserta vs wilayah ---
    df["oor"] = (df.home_region != df.region).astype(int)
    out["f_out_region"] = df.oor.values
    share = df.groupby("faskes_id").oor.transform("mean")
    out["f_faskes_oor_z"] = _z_by_group(share, df["type"]).values
    out["f_pat_total"] = df.groupby("patient_id").claim_id.transform("count").values
    out["f_pat_nfaskes"] = df.groupby("patient_id").faskes_id.transform("nunique").values

    # --- lonjakan pengiriman (burst) ---
    burst = np.zeros(len(df))
    for _, idx in df.groupby("faskes_id").indices.items():
        s = np.sort(df.submit_s.values[idx])
        lo, hi = _within(s, df.submit_s.values[idx], 60)
        burst[idx] = hi - lo - 1
    df["burst"] = burst
    out["f_burst"] = burst
    out["f_burst_z"] = _z_by_group(pd.Series(np.log1p(burst), index=df.index), df["type"]).values

    # --- konkurensi dokter: satu dokter, banyak faskes, jam yang sama ---
    conc = np.zeros(len(df))
    pair_cnt: dict = {}
    fname = df.faskes_id.values
    for _, idx in df.groupby("doctor_id").indices.items():
        order = idx[np.argsort(df.visit_s.values[idx])]
        v = df.visit_s.values[order]
        lo, hi = _within(v, v, 1800)
        fn = fname[order]
        for j in range(len(order)):
            win = slice(lo[j], hi[j])
            others = set(fn[win]) - {fn[j]}
            conc[order[j]] = len(others)
            for o in others:
                key = tuple(sorted((fn[j], o)))
                pair_cnt[key] = pair_cnt.get(key, 0) + 1
    out["f_doc_conc"] = conc
    out["f_doc_nfaskes"] = df.groupby("doctor_id").faskes_id.transform("nunique").values
    G = nx.Graph()
    G.add_nodes_from(faskes.faskes_id)
    G.add_edges_from([k for k, c in pair_cnt.items() if c >= 6])
    comp = {n: len(c) for c in nx.connected_components(G) for n in c}
    out["f_conc_component"] = df.faskes_id.map(comp).fillna(1).values

    # --- klaim berulang (peserta + ICD sama) ---
    d = df.sort_values(["patient_id", "icd", "visit_s"])
    same = (d.patient_id.values[1:] == d.patient_id.values[:-1]) & (d.icd.values[1:] == d.icd.values[:-1])
    gap = np.full(len(d), 999.0)
    cross = np.zeros(len(d))
    gap[1:] = np.where(same, (d.visit_s.values[1:] - d.visit_s.values[:-1]) / 3600, 999.0)
    cross[1:] = np.where(same, d.faskes_id.values[1:] != d.faskes_id.values[:-1], 0)
    gap = np.minimum(gap, 999.0)
    ser_gap = pd.Series(gap, index=d.index).reindex(df.index)
    ser_cross = pd.Series(cross, index=d.index).reindex(df.index)
    out["f_gap_prev_h"] = ser_gap.values
    out["f_dup_recent"] = (ser_gap.values < 48).astype(int)
    out["f_dup_cross"] = ((ser_gap.values < 48) & (ser_cross.values > 0)).astype(int)

    # --- perbaikan Repeat Billing: tarif sama, pasangan faskes konsorsium, intensitas klaim ulang per faskes ---
    recent = gap < 48
    ptar = np.full(len(d), np.nan)
    ptar[1:] = np.where(same, d.tarif.values[:-1], np.nan)
    pfas = np.full(len(d), "", dtype=object)
    pfas[1:] = np.where(same, d.faskes_id.values[:-1], "")
    tm = np.where(recent, np.abs(d.tarif.values / np.where(np.isnan(ptar), 1.0, ptar) - 1), 1.0)
    out["f_tarif_match_prev"] = pd.Series(np.minimum(tm, 1.0), index=d.index).reindex(df.index).values
    cross_ev = recent & (cross > 0)
    pa = np.where(pfas < d.faskes_id.values, pfas, d.faskes_id.values)
    pb = np.where(pfas < d.faskes_id.values, d.faskes_id.values, pfas)
    ev = pd.DataFrame({"a": pa, "b": pb, "x": cross_ev}, index=d.index)
    pair_n = ev[ev.x].groupby(["a", "b"]).size()
    pair_val = np.array([pair_n.get((a_, b_), 0) if x_ else 0 for a_, b_, x_ in zip(ev.a, ev.b, ev.x)], float)
    out["f_dup_pair_cross"] = pd.Series(pair_val, index=d.index).reindex(df.index).values
    rate = pd.Series(recent.astype(float), index=d.index).reindex(df.index).groupby(df.faskes_id).transform("mean")
    out["f_dup_faskes_z"] = _z_by_group(rate, df["type"]).values

    # --- rujukan ---
    aff = set(map(tuple, affiliations[["doctor_id", "faskes_id"]].values))
    is_ref = df.referral_from_doctor.notna()
    out["f_ref"] = is_ref.astype(int).values
    internal = np.array([(rd, f) in aff if isinstance(rd, str) else False
                         for rd, f in zip(df.referral_from_doctor, df.faskes_id)])
    df["internal"] = internal.astype(int)
    r = df[is_ref]
    out["f_ref_internal"] = df.internal.values
    ratio = r.groupby("referral_from_doctor").internal.agg(["mean", "count"])
    ratio = ratio["mean"].where(ratio["count"] >= 5, 0.0)
    out["f_doc_ref_internal"] = df.referral_from_doctor.map(ratio).fillna(0).values
    into = r.groupby("faskes_id").claim_id.count()
    pair_doc = r.groupby(["faskes_id", "referral_from_doctor"]).claim_id.count()
    share_doc = pd.Series([pair_doc[(f, d_)] / into[f] if (f, d_) in pair_doc.index and into.get(f, 0) >= 8 else 0.0
                           for f, d_ in zip(df.faskes_id, df.referral_from_doctor)], index=df.index)
    out["f_ref_doc_share"] = share_doc.where(is_ref, 0.0).values
    pc = r.groupby(["referral_from_faskes", "faskes_id"]).claim_id.count()
    rf_arr, f_arr = df.referral_from_faskes.to_numpy(), df.faskes_id.to_numpy()
    fwd = np.nan_to_num(pc.reindex(pd.MultiIndex.from_arrays([rf_arr, f_arr])).to_numpy(float))
    rev = np.nan_to_num(pc.reindex(pd.MultiIndex.from_arrays([f_arr, rf_arr])).to_numpy(float))
    lo, hi = np.minimum(fwd, rev), np.maximum(fwd, rev)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(hi > 0, lo / hi, 0.0)
    out["f_ref_reciprocity"] = np.where(is_ref.to_numpy() & (lo >= 3), ratio, 0.0)

    # --- tarif & volume ---
    out["f_tarif_ratio"] = (df.tarif / df.icd.map(ICD_CAP)).values
    vol = df.groupby("faskes_id").claim_id.transform("count") / df.capacity
    out["f_volume_z"] = _z_by_group(vol, df["type"]).values
    return out[FEATURES]


# ---------------------------------------------------------------------------
# Baseline berbasis aturan: memeriksa tiap klaim secara terpisah (cara lama)
# ---------------------------------------------------------------------------
def rule_flags(claims: pd.DataFrame) -> pd.DataFrame:
    """Asumsi saya tentang mesin aturan lama: (1) tarif melewati plafon, (2) klaim ganda identik
    (peserta + ICD + faskes) pada hari yang sama. Tidak melihat relasi antar-faskes/dokter."""
    assert_no_labels(claims)
    day = claims.visit_ts.dt.floor("D")
    dup = claims.assign(day=day).groupby(["patient_id", "icd", "faskes_id", "day"]).cumcount() > 0
    over = claims.tarif > claims.icd.map(ICD_CAP)
    return pd.DataFrame({"rule_over_cap": over.astype(int).values, "rule_same_day_dup": dup.astype(int).values},
                        index=claims.claim_id.values)


# ---------------------------------------------------------------------------
# Penjelasan per klaim (bahasa awam)
# ---------------------------------------------------------------------------
def explain(row: pd.Series) -> dict:
    """Alasan yang bisa dibaca verifikator + dugaan tipologi, dari fitur teramati."""
    reasons: dict[str, list[str]] = {"Phantom Billing": [], "Repeat Billing": [], "Self-Referral": []}
    if row.f_out_region and row.f_faskes_oor_z > 2:
        reasons["Phantom Billing"].append(
            f"Peserta berdomisili di luar wilayah faskes; porsi peserta luar wilayah faskes ini {row.f_faskes_oor_z:.1f} simpangan baku di atas faskes sejenis.")
    if row.f_burst_z > 2:
        reasons["Phantom Billing"].append(
            f"Dikirim serentak: {int(row.f_burst)} klaim dari faskes yang sama dalam ±60 detik, tidak lazim untuk faskes sejenis.")
    if row.f_doc_conc >= 1:
        reasons["Phantom Billing"].append(
            f"Dokter yang sama menagih di {int(row.f_doc_conc) + 1} faskes dalam rentang 30 menit.")
    if row.f_dup_recent:
        lintas = " dan di faskes berbeda" if row.f_dup_cross else ""
        reasons["Repeat Billing"].append(
            f"Peserta dengan diagnosis sama ditagih lagi {row.f_gap_prev_h:.0f} jam setelah klaim sebelumnya{lintas}.")
    if row.f_dup_recent and row.f_tarif_match_prev <= .035:
        reasons["Repeat Billing"].append(
            f"Tarif nyaris identik dengan klaim sebelumnya (selisih {row.f_tarif_match_prev:.1%}).")
    if row.f_dup_pair_cross >= 5:
        reasons["Repeat Billing"].append(
            f"Pasangan faskes ini berulang kali menagih peserta yang sama dalam 48 jam ({int(row.f_dup_pair_cross)} kejadian).")
    if row.f_ref_internal and row.f_doc_ref_internal >= .6:
        reasons["Self-Referral"].append(
            f"Dokter perujuk terdaftar di faskes tujuan; {row.f_doc_ref_internal:.0%} rujukannya berakhir di faskes terafiliasi.")
    if row.f_ref_reciprocity >= .2:
        reasons["Self-Referral"].append("Pasangan faskes saling merujuk dua arah dalam volume sebanding (siklus rujukan).")
    best = max(reasons, key=lambda k: len(reasons[k]))
    return {"typology": best if reasons[best] else None, "reasons": [x for v in reasons.values() for x in v]}
