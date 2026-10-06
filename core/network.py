"""Graf relasi antar-faskes JALA, dibangun HANYA dari kolom teramati.

Tidak ada label di modul ini — sama seperti core.detect. Dua kegunaannya:
  * mengelompokkan faskes berisiko menjadi klaster/cincin (komunitas Louvain) untuk Risk Ranking
  * menyediakan node + edge + koordinat untuk layar Network Graph

Tiga relasi teramati yang menghubungkan dua faskes:
  dup  : peserta + diagnosis sama ditagih di dua faskes dalam 48 jam
  conc : satu dokter menagih di dua faskes dalam rentang 30 menit (mustahil secara fisik)
  ref  : rujukan antar faskes (dipakai untuk gambar, bukan untuk pengelompokan)
"""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

DUP_WINDOW_H = 48.0
CONC_WINDOW_S = 1800.0
TOP_N_FASKES = 20          # berapa faskes berisiko tertinggi yang dikelompokkan menjadi cincin
EDGE_KIND_LABEL = {"dup": "Klaim ganda <48 jam", "conc": "Dokter sama, jam sama", "ref": "Rujukan"}


def faskes_edges(claims: pd.DataFrame) -> pd.DataFrame:
    """Semua tepi antar-faskes yang terlihat dari data teramati, dengan bobot = jumlah kejadian."""
    t0 = claims.visit_ts.min()
    c = claims.assign(visit_s=(claims.visit_ts - t0).dt.total_seconds())
    rows: list[tuple] = []

    def add(pairs: pd.Series, kind: str) -> None:
        for key, n in pairs.value_counts().items():
            a, b = key.split("|")
            rows.append((a, b, kind, float(n)))

    # --- klaim ganda lintas faskes (peserta + diagnosis sama, < 48 jam) ---
    d = c.sort_values(["patient_id", "icd", "visit_s"])
    g = d.groupby(["patient_id", "icd"], sort=False)
    gap = (g.visit_s.diff() / 3600).to_numpy()
    prev_f = g.faskes_id.shift().fillna("").to_numpy()
    cur_f = d.faskes_id.to_numpy()
    hit = np.isfinite(gap) & (gap < DUP_WINDOW_H) & (prev_f != "") & (prev_f != cur_f)
    if hit.any():
        add(pd.Series([f"{min(a, b)}|{max(a, b)}" for a, b in zip(prev_f[hit], cur_f[hit])]), "dup")

    # --- konkurensi dokter: satu dokter, dua faskes, selisih <= 30 menit ---
    dd = c.sort_values(["doctor_id", "visit_s"])
    vis, fas = dd.visit_s.to_numpy(), dd.faskes_id.to_numpy()
    conc: dict = {}
    for idx in dd.groupby("doctor_id", sort=False).indices.values():
        v, f = vis[idx], fas[idx]
        lo = np.searchsorted(v, v - CONC_WINDOW_S, "left")
        hi = np.searchsorted(v, v + CONC_WINDOW_S, "right")
        for j in range(len(v)):
            for o in set(f[lo[j]:hi[j]]) - {f[j]}:
                conc[f"{min(f[j], o)}|{max(f[j], o)}"] = conc.get(f"{min(f[j], o)}|{max(f[j], o)}", 0) + 1
    add(pd.Series(list(conc), index=list(conc.values())), "conc")

    # --- rujukan antar faskes ---
    r = c.dropna(subset=["referral_from_faskes"])
    r = r[r.referral_from_faskes != r.faskes_id]
    for (a, b), n in r.groupby(["referral_from_faskes", "faskes_id"]).size().items():
        rows.append((a, b, "ref", float(n)))

    return pd.DataFrame(rows, columns=["src", "dst", "kind", "weight"])


def faskes_risk(scored: pd.DataFrame, score_col: str = "score_graph",
                faskes_col: str = "faskes_id") -> pd.Series:
    """Risiko faskes = rata-rata skor klaim tertingginya (10% teratas, minimal 5 klaim).

    Memakai ekor atas, bukan rata-rata seluruh klaim: satu cincin hanya menagih sebagian kecil
    klaimnya secara curang, sisanya kunjungan warga yang sah.
    """
    out = {}
    for f, s in scored.groupby(faskes_col)[score_col]:
        v = np.sort(s.to_numpy())[::-1]
        out[f] = float(v[:max(5, len(v) // 10)].mean())
    return pd.Series(out).sort_values(ascending=False)


def build_graph(edges: pd.DataFrame, nodes, kinds=("dup", "conc")) -> nx.Graph:
    """Graf berbobot antar-faskes.

    `ref` sengaja tidak dipakai untuk pengelompokan: rujukan sah sangat padat, jadi seluruh faskes
    di satu wilayah akan menyatu menjadi satu komunitas dan cincin fraud justru tenggelam.
    """
    e = edges[edges.kind.isin(kinds)]
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for (a, b, kind), w in e.groupby(["src", "dst", "kind"], sort=False).weight.sum().items():
        if not G.has_edge(a, b):
            G.add_edge(a, b, weight=0.0, kinds=[])
        G[a][b]["weight"] += float(w)
        G[a][b]["kinds"].append(kind)
    return G


def rings(G: nx.Graph, seed: int = 0, max_ring: int = 8) -> list[set]:
    """Pecah graf menjadi cincin. Komponen kecil diambil utuh; komponen besar dipecah Louvain."""
    out = []
    for comp in nx.connected_components(G):
        if len(comp) < 2:
            continue
        sub = G.subgraph(comp)
        if len(sub) <= max_ring:
            out.append(set(sub))
            continue
        for part in nx.community.louvain_communities(sub, weight="weight", seed=seed, resolution=1.15):
            if len(part) >= 2:
                out.append(set(part))
    return sorted(out, key=lambda s: (-len(s), sorted(s)))


def select_rings(claims: pd.DataFrame, scored: pd.DataFrame, top_n: int = TOP_N_FASKES,
                 seed: int = 0) -> tuple[list[dict], nx.Graph, pd.Series]:
    """Ambil faskes berisiko tertinggi, lalu kelompokkan menjadi cincin.

    Mengembalikan (daftar cincin urut risiko, graf penuh, risiko per faskes). Faskes berisiko tinggi
    yang tidak punya tetangga muncul sebagai cincin berisi satu faskes — tetap layak diperiksa,
    hanya tidak ada bukti jejaringnya.
    """
    risk = faskes_risk(scored)
    hot = list(risk.head(top_n).index)
    G = build_graph(faskes_edges(claims), set(claims.faskes_id))
    groups = rings(G.subgraph(hot), seed=seed)
    grouped = {f for g in groups for f in g}

    per_faskes = claims.groupby("faskes_id").agg(n=("claim_id", "size"), nilai=("tarif", "sum"))
    sc = claims.merge(scored[["claim_id", "score_graph"]], on="claim_id")

    out = []
    for members in groups + [{f} for f in hot if f not in grouped]:
        m = sorted(members)
        cm = sc[sc.faskes_id.isin(m)]
        flagged = cm[cm.score_graph >= 0.5]
        sub = G.subgraph(m)
        out.append({
            "members": m,
            "n_faskes": len(m),
            "risk": float(np.mean([risk[f] for f in m])),
            "n_claims": int(per_faskes.loc[per_faskes.index.isin(m), "n"].sum()),
            "nilai": float(per_faskes.loc[per_faskes.index.isin(m), "nilai"].sum()),
            "flagged_claims": int(len(flagged)),
            "flagged_nilai": float(flagged.tarif.sum()),
            "density": float(nx.density(sub)) if len(m) > 1 else 0.0,
            "degree": {f: float(w) for f, w in sub.degree(weight="weight")} if len(m) > 1 else {m[0]: 0.0},
            "kinds": sorted({k for _, _, d in sub.edges(data=True) for k in d.get("kinds", [])}),
        })
    out.sort(key=lambda c: (-c["risk"], c["members"][0]))
    for i, c in enumerate(out, start=1):
        c["id"] = f"JALA-NET-{i:03d}"
    return out, G, risk


def hetero_subgraph(claims: pd.DataFrame, faskes: pd.DataFrame, affiliations: pd.DataFrame,
                    patients: pd.DataFrame, scored: pd.DataFrame, members, max_extra: int = 7):
    """Node + edge untuk menggambar satu cincin sebagai jaringan heterogen
    Faskes-Dokter-Peserta-ICD. Koordinat dari spring layout, bukan posisi yang diketik manual."""
    m = sorted(members)
    c = claims[claims.faskes_id.isin(m)].merge(scored[["claim_id", "score_graph"]], on="claim_id")
    fname = dict(zip(faskes.faskes_id, faskes["name"]))
    ftype = dict(zip(faskes.faskes_id, faskes.type))
    freg = dict(zip(faskes.faskes_id, faskes.region))
    phome = dict(zip(patients.patient_id, patients.home_region))

    hot = {f: float(c.loc[c.faskes_id == f, "score_graph"].mean()) for f in m}
    nodes = [{"id": f, "type": "faskes", "risk": hot[f] > 0.5, "label": fname.get(f, f),
              "sub": f"{ftype.get(f, '?')} · {freg.get(f, '?')} · skor {hot[f]:.2f}"} for f in m]
    edges: list[dict] = []

    def add_node(nid: str, ntype: str, risk: bool, label: str, sub: str) -> None:
        if not any(n["id"] == nid for n in nodes):
            nodes.append({"id": nid, "type": ntype, "risk": risk, "label": label, "sub": sub})

    # dokter yang menagih di cincin ini, diambil yang skornya tertinggi
    doc = c.groupby("doctor_id").agg(n=("claim_id", "size"), s=("score_graph", "mean"),
                                     f=("faskes_id", "nunique")).sort_values("s", ascending=False)
    for d, r in doc.head(max_extra).iterrows():
        add_node(d, "dokter", bool(r.s > 0.5), f"dr. {d}",
                 f"{int(r.n)} klaim di {int(r.f)} faskes cincin ini")
        for f in m:
            if ((c.doctor_id == d) & (c.faskes_id == f)).any():
                edges.append({"src": d, "dst": f, "kind": "treats", "risk": bool(r.s > 0.5)})
        for other in sorted(set(affiliations.loc[affiliations.doctor_id == d, "faskes_id"]) - set(m))[:1]:
            add_node(other, "faskes", False, fname.get(other, other),
                     f"{ftype.get(other, '?')} · SIP dokter ini juga terdaftar di sini")
            edges.append({"src": d, "dst": other, "kind": "sip", "risk": False})

    # peserta yang paling mencurigakan di cincin ini
    pat = c.groupby("patient_id").agg(n=("claim_id", "size"), s=("score_graph", "max"),
                                      f=("faskes_id", "nunique")).sort_values(["s", "n"], ascending=False)
    regions = {freg[f] for f in m}
    for p, r in pat.head(max_extra).iterrows():
        add_node(p, "pasien", bool(r.s > 0.5), f"Peserta {p}",
                 f"{int(r.n)} klaim · {int(r.f)} faskes"
                 + ("" if phome.get(p) in regions else f" · domisili {phome.get(p, '?')} (luar wilayah)"))
        for f in m:
            if ((c.patient_id == p) & (c.faskes_id == f)).any():
                edges.append({"src": p, "dst": f, "kind": "claim", "risk": bool(r.s > 0.5)})

    # diagnosis yang paling banyak ditagih cincin ini
    for code, r in c.groupby("icd").agg(n=("claim_id", "size"), nilai=("tarif", "sum")) \
                    .sort_values("n", ascending=False).head(4).iterrows():
        add_node(code, "icd", False, f"ICD-10 {code}", f"{int(r.n)} klaim · Rp {r.nilai:,.0f}")
        for f in m:
            if ((c.icd == code) & (c.faskes_id == f)).any():
                edges.append({"src": f, "dst": code, "kind": "icd", "risk": False})

    # tepi antar-faskes di dalam cincin
    inner = faskes_edges(claims)
    inner = inner[inner.src.isin(m) & inner.dst.isin(m)].sort_values("weight", ascending=False)
    for r in inner.itertuples():
        edges.append({"src": r.src, "dst": r.dst, "kind": r.kind, "risk": r.kind in ("dup", "conc"),
                      "label": f"{int(r.weight)}×"})

    G = nx.Graph()
    G.add_nodes_from([n["id"] for n in nodes])
    G.add_edges_from([(e["src"], e["dst"]) for e in edges])
    pos = nx.spring_layout(G, seed=7, k=1.15) if len(G) else {}

    xs = np.array([p[0] for p in pos.values()]) if pos else np.zeros(1)
    ys = np.array([p[1] for p in pos.values()]) if pos else np.zeros(1)
    span_x, span_y = float(xs.max() - xs.min()) or 1.0, float(ys.max() - ys.min()) or 1.0
    for n in nodes:
        p = pos[n["id"]]
        n["x"] = round(1.0 + (p[0] - xs.min()) / span_x * 11.5, 3)
        n["y"] = round(1.0 + (ys.max() - p[1]) / span_y * 7.0, 3)
    return nodes, edges
