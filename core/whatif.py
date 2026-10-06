"""Simulasi struktural: "bagaimana kalau dokter ini dikeluarkan dari klaster?"

Versi murah dan murni struktur graf. Untuk satu klaster, klaim ditandai milik dokter D (sebagai dokter yang
menangani ATAU dokter perujuk) dibuang, lalu graf antar-faskes dihitung ulang dengan aturan yang sama dengan
core.live.build (`link_counts`, sisi dengan bobot >= MIN_EDGE). Yang diukur: apakah klaster pecah, berapa
bobot hubungan antar-faskes yang hilang, dan berapa klaim yang bergantung pada dokter itu.

Bukan penilaian peran hukum dokter, dan tidak memakai label. Hanya prioritas untuk pemeriksa lapangan.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd

from core.live import MIN_EDGE, Live, link_counts

TOP_DOCTORS = 12
_ROLE_RANK = {"inti": 0, "pendukung": 1, "periferal": 2}


def structure(fl: pd.DataFrame, min_edge: int = MIN_EDGE) -> nx.Graph:
    """Graf antar-faskes untuk sekumpulan klaim ditandai (simpul = faskes yang masih punya klaim)."""
    G = nx.Graph()
    if fl.empty:
        return G
    G.add_nodes_from(sorted(fl.faskes_id.unique()))
    for (a, b), n in link_counts(fl).items():
        if n >= min_edge and a in G and b in G:
            G.add_edge(a, b, weight=n)
    return G


def _involved(fl: pd.DataFrame, doctor_id: str) -> pd.Series:
    return (fl.doctor_id == doctor_id) | (fl.referral_from_doctor == doctor_id)


def _weight(G: nx.Graph) -> int:
    return int(sum(d["weight"] for _, _, d in G.edges(data=True)))


def evaluate_removal(live: Live, cid: str, doctor_id: str, min_edge: int = MIN_EDGE) -> dict:
    c = live.by_id[cid]
    fl = live.flagged.loc[c["idx"]]
    mask = _involved(fl, doctor_id)
    rest = fl[~mask]
    before, after = structure(fl, min_edge), structure(rest, min_edge)

    n_total, n_rem = len(fl), int(mask.sum())
    val_total, val_rem = float(fl.tarif.sum()), float(fl.tarif[mask].sum())
    w_before, w_after = _weight(before), _weight(after)
    comp_before = nx.number_connected_components(before) if before.number_of_nodes() else 0
    comp_after = nx.number_connected_components(after) if after.number_of_nodes() else 0
    lost = sorted(set(before.nodes) - set(after.nodes))                       # faskes tanpa klaim ditandai lagi
    cut = sorted(n for n in after.nodes if before.degree(n) > 0 and after.degree(n) == 0)   # faskes terputus
    sizes = sorted((len(x) for x in nx.connected_components(after)), reverse=True)

    claims_share = n_rem / n_total if n_total else 0.0
    w_lost = (w_before - w_after) / w_before if w_before else 0.0
    split = comp_after > comp_before
    if n_rem == n_total or split or w_lost >= .5 or claims_share >= .5:
        role = "inti"
    elif w_lost >= .2 or claims_share >= .2:
        role = "pendukung"
    else:
        role = "periferal"

    d = f"dokter {doctor_id}"
    if n_rem == n_total:
        verdict = f"Seluruh klaim ditandai di klaster ini melibatkan {d}; tanpa dia klaster tidak punya klaim tersisa."
    elif split:
        verdict = (f"Tanpa {d} klaster pecah menjadi {comp_after} bagian (dari {comp_before}); "
                   f"{w_lost:.0%} bobot hubungan antar-faskes hilang dan {claims_share:.0%} klaim ikut lepas.")
    elif w_before == 0:
        verdict = (f"Klaster ini tidak punya hubungan antar-faskes yang bisa diputus; {d} hanya terkait "
                   f"{claims_share:.0%} klaim ditandai.")
    elif role == "inti":
        verdict = (f"Klaster tetap utuh tanpa {d}, tetapi {w_lost:.0%} bobot hubungan antar-faskes hilang "
                   f"dan {claims_share:.0%} klaim lepas: dia penghubung utama.")
    else:
        verdict = (f"Jaringan tidak bergantung pada {d}: klaster tetap utuh, {w_lost:.0%} hubungan hilang, "
                   f"{claims_share:.0%} klaim terkait.")
    return {
        "doctor": doctor_id, "role": role, "split": bool(split),
        "claims_total": n_total, "claims_removed": n_rem, "claims_share": claims_share,
        "value_removed": val_rem, "value_share": val_rem / val_total if val_total else 0.0,
        "faskes_before": before.number_of_nodes(), "faskes_after": after.number_of_nodes(),
        "faskes_lost": lost, "faskes_cut": cut,
        "components_before": comp_before, "components_after": comp_after, "component_sizes_after": sizes,
        "weight_before": w_before, "weight_after": w_after, "weight_lost_share": w_lost,
        "verdict": verdict,
    }


def cluster_doctors(live: Live, cid: str, top: int = TOP_DOCTORS) -> list[str]:
    fl = live.flagged.loc[live.by_id[cid]["idx"]]
    inv = pd.concat([fl.doctor_id, fl.referral_from_doctor.dropna()]).value_counts()
    return list(inv.head(top).index)


def rank_doctors(live: Live, cid: str, top: int = TOP_DOCTORS) -> list[dict]:
    """Dokter dalam klaster, dari yang paling menentukan struktur jaringan."""
    res = [evaluate_removal(live, cid, d) for d in cluster_doctors(live, cid, top)]
    res.sort(key=lambda r: (_ROLE_RANK[r["role"]], -(r["components_after"] - r["components_before"]),
                            -r["weight_lost_share"], -r["claims_share"], r["doctor"]))
    return res
