"""Data layar JALA yang DIHITUNG dari skor nyata (menggantikan data ilustrasi di data/mock_data.py).

Alur (tanpa membaca label):
  1. klaim berskor >= THRESH dianggap "ditandai"
  2. faskes dihubungkan bila klaim ditandai mengaitkan keduanya (rujukan, dokter yang sama, peserta yang sama);
     sisi dengan bobot < MIN_EDGE dibuang agar kebetulan tidak menyatukan klaster
  3. komunitas Louvain pada graf faskes itu = klaster
  4. tiap klaster diberi skor, tipologi dugaan (dari core.detect.explain), bukti, subgraf, dan profil faskes

Bentuk keluaran sengaja mengikuti skema data/mock_data.py (RISK_CLUSTERS, TRIAGE_QUEUE, CLAIM_DETAILS,
AUDIT_CLUSTER, GRAPH_NODES/EDGES) supaya tampilan lama bisa memakainya tanpa dirombak.

`evaluate_clusters` adalah SATU-SATUNYA fungsi di sini yang menyentuh label, dan hanya untuk menilai (bukan untuk
membangun klaster).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import numpy as np
import pandas as pd

from core.detect import FEATURES, explain
from core.synthetic import PERIOD_DAYS, PERIOD_START, TYPE_LABEL, World

THRESH = 0.5          # skor klaim minimum untuk "ditandai"
MIN_EDGE = 3          # bobot sisi minimum antar-faskes
MIN_CLAIMS = 5        # klaster lebih kecil dari ini diabaikan
AUTO_FLAG = 85        # skor klaster (%) untuk "Auto-Flagged"
SEED = 7

TYPO = {   # tipologi -> (nada lencana, ikon)
    "Phantom Billing": ("amber", "✳"),
    "Repeat Billing": ("amber", "⧉"),
    "Self-Referral": ("green", "♻"),
}
METAPATH = {
    "Phantom Billing": "Peserta–Dokter–Faskes (serentak)",
    "Repeat Billing": "Peserta–Faskes–Faskes (klaim ulang)",
    "Self-Referral": "Dokter–Faskes–Faskes (rujukan)",
}
_MONTH = {7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt"}


def rp(v: float) -> str:
    return "Rp " + f"{int(round(v)):,}".replace(",", ".")


def _pct(x: float) -> str:
    return f"{x:.0%}"


def _status(c: dict, default: tuple) -> tuple:
    """Lencana status; klaster yang disentuh umpan balik verifikator diberi lencana sendiri."""
    fb = c.get("fb")
    if not fb:
        return default
    return {"dismiss": ("Pola wajar (simulasi)", "grey"), "similar": ("Prioritas diturunkan", "amber"),
            "confirm": ("Penangguhan simulasi dikonfirmasi", "teal")}.get(fb["kind"], default)


def _fb_suffix(c: dict) -> str:
    base = c.get("score_base")
    return f" · skor dasar {base}%" if base is not None and base != c["score"] else ""


@dataclass
class Live:
    world: World
    df: pd.DataFrame                  # semua klaim + fitur + score_graph (tanpa label)
    flagged: pd.DataFrame
    typ: pd.Series                    # dugaan tipologi tiap klaim ditandai
    G: nx.Graph                       # graf faskes (klaim ditandai)
    clusters: list = field(default_factory=list)
    modularity: float = 0.0
    by_id: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ baris tabel (skema RISK_CLUSTERS)
    def risk_rows(self) -> list:
        return [self._risk_row(c) for c in self.clusters]

    def _risk_row(self, c) -> dict:
        tone, icon = TYPO.get(c["typology"], ("grey", "◆"))
        s = c["score"]
        return {
            "id": c["id"], "name": c["name"], "subtitle": c["subtitle"],
            "status": _status(c, ("Prioritas otomatis", "red") if s >= AUTO_FLAG else ("Tinjauan awal", "grey")),
            "score": s, "conf": "Prioritas sangat tinggi" if s >= 90 else ("Prioritas tinggi" if s >= AUTO_FLAG else "Tinjauan awal"),
            "metric": c["metric"] + _fb_suffix(c), "typology": (c["typology"], tone), "why": c["why"],
            "actions": ["Lihat subgraf"], "icon": icon, "icon_tone": tone,
        }

    def risk_stats(self, audited: int = 0) -> list:
        n_auto = sum(c["score"] >= AUTO_FLAG for c in self.clusters)
        dens = float(np.mean([c["density"] for c in self.clusters])) if self.clusters else 0.0
        return [
            {"label": "Klaster dalam antrean", "value": str(len(self.clusters)), "tone": "dark", "icon": "🕸", "icon_tone": "grey",
             "note": f"dari {self.flagged.faskes_id.nunique()} faskes dengan klaim ditandai"},
            {"label": f"Prioritas otomatis (≥{AUTO_FLAG}%)", "value": str(n_auto), "tone": "red", "icon": "⚠", "icon_tone": "red",
             "note": "Antrean verifikator prioritas"},
            {"label": "Diaudit di Sesi Ini", "value": str(audited), "tone": "dark", "icon": "✅", "icon_tone": "amber", "note": ""},
            {"label": "Kepadatan Rata-rata Klaster", "value": f"{dens:.2f}", "tone": "teal", "icon": "❋", "icon_tone": "green",
             "note": f"Modularitas Louvain: {self.modularity:.2f}"},
        ]

    # ------------------------------------------------------------------ antrean triase (skema TRIAGE_QUEUE)
    def triage_rows(self) -> list:
        out = []
        for c in self.clusters:
            s = c["score"]
            out.append({
                "id": c["id"], "name": c["name"],
                "nodes": f"{len(c['faskes'])} Faskes · {c['n_doctors']} Dokter · Wilayah {', '.join(c['regions'])}",
                "typology": c["typology"], "faskes": c["faskes_names"], "volume": c["n"], "value": rp(c["value"]),
                "score": s, "status": _status(c, ("Prioritas otomatis", "red") if s >= AUTO_FLAG else ("Menunggu tinjauan", "amber")),
            })
        return out

    def triage_stats(self, auc: float | None = None) -> list:
        crit = sum(c["score"] >= 90 for c in self.clusters)
        exp = sum(c["value"] for c in self.clusters)
        stats = [
            {"label": "Klaster dalam antrean", "value": str(len(self.clusters)), "delta": "", "note": f"{len(self.flagged):,} klaim masuk tinjauan awal dari {len(self.df):,}", "tone": "dark"},
            {"label": "Prioritas Sangat Tinggi (≥90%)", "value": str(crit), "delta": "", "note": "Tinjau lebih dahulu; bukan keputusan otomatis", "tone": "amber"},
            {"label": "Nilai Klaim Ditandai", "value": rp(exp), "delta": "", "note": "Total tarif klaim ditandai (sintetis)", "tone": "dark"},
        ]
        if auc is not None:
            stats.append({"label": "AUC-ROC (data sintetis)", "value": f"{auc:.3f}", "delta": "", "note": "Validasi silang per kelompok faskes", "tone": "teal"})
        return stats

    # ------------------------------------------------------------------ detail klaster (skema CLAIM_DETAILS)
    def detail(self, cid: str) -> dict:
        c = self.by_id[cid]
        tone, _ = TYPO.get(c["typology"], ("grey", "◆"))
        names = c["faskes_names"]
        return {
            "title": c["name"], "typology": (c["typology"], tone),
            "flag": f"Prioritas otomatis ({c['score']}%)" if c["score"] >= AUTO_FLAG else f"Tinjauan awal ({c['score']}%)",
            "profile": [
                ("Fasilitas Kesehatan", names), ("Periode Observasi", "Q3 2026 (Jul - Sep)"),
                ("Total Klaim Ditandai", f"{c['n']} klaim", "red"), ("Keterikatan Metapath", METAPATH.get(c["typology"], "—"), "teal"),
            ],
            "timeline": c["timeline"], "peak": c["peak"], "why": c["why"],
            "why_note": (f"Skor prioritas pemeriksaan {c['score']}/100 dari {c['n']} klaim ditandai. "
                         "Ini bukan probabilitas kecurangan atau bukti; verifikator tetap memeriksa data sumber."),
            "evidence": c["evidence"],
        }

    # ------------------------------------------------------------------ audit (skema AUDIT_CLUSTER / AUDIT_FASKES)
    def audit(self, cid: str) -> dict:
        c = self.by_id[cid]
        tone, _ = TYPO.get(c["typology"], ("grey", "◆"))
        s = c["score"]
        return {
            "id": c["id"], "name": c["name"], "flag": f"Prioritas otomatis ({s}%)" if s >= AUTO_FLAG else f"Tinjauan awal ({s}%)",
            "typology": (c["typology"], tone), "algo": "Deteksi: prototipe fitur graf pada data sintetis (arsitektur target: HAN)",
            "score": s, "score_note": "Kategori: Sangat Tinggi" if s >= 90 else ("Kategori: Tinggi" if s >= AUTO_FLAG else "Kategori: Sedang"),
            "cards": [
                ("Faskes Terkait", f"{len(c['faskes'])} Faskes Terkait", c["faskes_names"], "dark"),
                ("Klaim Ditandai", f"{c['n']} Klaim Ditandai", f"Total tarif {rp(c['value'])}", "red"),
                ("Pola Metapath", METAPATH.get(c["typology"], "—"), c["typology"], "dark"),
                ("Entitas Sentralitas Tertinggi", c["central"][0], f"Degree Centrality: {c['central'][1]:.3f} (inti klaster)", "teal"),
            ],
            "evidence": c["why"], "density": f"Kepadatan graf faskes: {c['density']:.2f}",
            "faskes_rows": c["faskes_rows"], "n_claims": c["n"], "value": c["value"], "n_faskes": len(c["faskes"]),
            "claim_ids": c["idx"],
        }

    # ------------------------------------------------------------------ subgraf (skema GRAPH_NODES / GRAPH_EDGES)
    def graph(self, cid: str, n_pat: int = 6, n_doc: int = 4, n_icd: int = 2):
        c = self.by_id[cid]
        fl = self.flagged.loc[c["idx"]]
        faskes = self.world.faskes.set_index("faskes_id")
        nodes, edges, seen = [], [], set()

        def add(nid, typ, label, sub, risk):
            if nid not in seen:
                seen.add(nid)
                nodes.append({"id": nid, "type": typ, "label": label, "sub": sub, "risk": risk, "x": 0.0, "y": 0.0})

        for f in c["faskes"]:
            r = faskes.loc[f]
            add(f"f_{f}", "faskes", f"{r['name']}", f"{TYPE_LABEL[r['type']]} · {r['region']} · skor {c['score']}", True)
        top_docs = fl.doctor_id.value_counts().head(n_doc).index
        ndoc = self.df.groupby("doctor_id").faskes_id.nunique()
        for d in top_docs:
            add(f"d_{d}", "dokter", f"Dokter {d}", f"menagih di {int(ndoc[d])} faskes", True)
        pats = fl.patient_id.value_counts().head(n_pat).index
        home = self.world.patients.set_index("patient_id").home_region
        freg = faskes.region
        for p in pats:
            pr = fl[fl.patient_id == p].iloc[0]
            oor = home[p] != freg[pr.faskes_id]
            add(f"p_{p}", "pasien", f"Peserta {p}", "Domisili luar wilayah" if oor else "Domisili setempat", True)
        for i in fl.icd.value_counts().head(n_icd).index:
            add(f"i_{i}", "icd", f"ICD: {i}", "", True)

        sel = fl[fl.patient_id.isin(pats) | fl.doctor_id.isin(top_docs)]
        pair = sel.groupby(["patient_id", "faskes_id"]).visit_ts.min()
        for (p, f), t in pair.items():
            if f"p_{p}" in seen and f"f_{f}" in seen:
                edges.append({"src": f"p_{p}", "dst": f"f_{f}", "style": "solid", "label": t.strftime("%d/%m"), "risk": True})
        for (d, f), _n in sel.groupby(["doctor_id", "faskes_id"]).size().items():
            if f"d_{d}" in seen and f"f_{f}" in seen:
                edges.append({"src": f"d_{d}", "dst": f"f_{f}", "style": "dash", "label": "", "risk": True})
        for (f, i), n in fl.groupby(["faskes_id", "icd"]).size().items():
            if f"i_{i}" in seen and f"f_{f}" in seen:
                edges.append({"src": f"f_{f}", "dst": f"i_{i}", "style": "dot", "label": f"×{n}", "risk": True})
        for a, b, w in c["fedges"]:
            edges.append({"src": f"f_{a}", "dst": f"f_{b}", "style": "solid", "label": f"×{w}", "risk": True})

        # tata letak: spring layout, dipetakan ke elips klaster yang digambar JS (pusat 9.4,4.5)
        g = nx.Graph()
        g.add_nodes_from(n["id"] for n in nodes)
        g.add_edges_from((e["src"], e["dst"]) for e in edges)
        pos = nx.spring_layout(g, seed=SEED, k=1.3 / np.sqrt(max(len(g), 1)), iterations=200) if len(g) > 1 else {nodes[0]["id"]: (0, 0)}
        xs, ys = np.array([p[0] for p in pos.values()]), np.array([p[1] for p in pos.values()])
        span = lambda a: (a.max() - a.min()) or 1.0
        for n in nodes:
            px, py = pos[n["id"]]
            n["x"] = round(6.9 + 5.0 * (px - xs.min()) / span(xs), 3) if len(g) > 1 else 9.4
            n["y"] = round(1.5 + 6.0 * (py - ys.min()) / span(ys), 3) if len(g) > 1 else 4.5

        # pembanding normal: faskes sejenis yang tidak berklaster dengan skor klaim terendah
        main = c["faskes"][0]
        peer = self._peer(faskes.loc[main, "type"])
        if peer:
            frows = self.df[self.df.faskes_id == peer]
            r = faskes.loc[peer]
            add("f_peer", "faskes", r["name"], f"{TYPE_LABEL[r['type']]} · pembanding normal", False)
            nodes[-1].update(x=3.0, y=5.0)
            doc = frows.doctor_id.value_counts().index[0]
            add("d_peer", "dokter", f"Dokter {doc}", "praktik di faskes ini", False)
            nodes[-1].update(x=2.2, y=7.0)
            ps = list(dict.fromkeys(frows.patient_id))[:2]
            for k, (p, (x, y)) in enumerate(zip(ps, [(1.6, 4.6), (3.0, 2.6)])):
                add(f"p_peer{k}", "pasien", f"Peserta {p}", "Domisili setempat" if home[p] == r["region"] else "Domisili lain", False)
                nodes[-1].update(x=x, y=y)
                edges.append({"src": f"p_peer{k}", "dst": "f_peer", "style": "solid", "label": "", "risk": False})
            for k, (i, (x, y)) in enumerate(zip(frows.icd.value_counts().index[:2], [(4.6, 6.6), (4.6, 3.6)])):
                add(f"i_peer{k}", "icd", f"ICD: {i}", "", False)
                nodes[-1].update(x=x, y=y)
                edges.append({"src": "f_peer", "dst": f"i_peer{k}", "style": "dot", "label": "", "risk": False})
            edges.append({"src": "d_peer", "dst": "f_peer", "style": "dash", "label": "", "risk": False})
            edges.append({"src": "f_peer", "dst": f"f_{main}", "style": "dot", "label": "", "risk": False, "faint": True})
        return nodes, edges

    def _peer(self, ftype: str):
        taken = {f for c in self.clusters for f in c["faskes"]}
        faskes = self.world.faskes
        cand = faskes[(faskes.type == ftype) & ~faskes.faskes_id.isin(taken)].faskes_id
        g = self.df[self.df.faskes_id.isin(cand)].groupby("faskes_id").score_graph.agg(["mean", "size"])
        g = g[g["size"] >= 20].sort_values("mean")
        return g.index[0] if len(g) else None

    # ------------------------------------------------------------------ dashboard
    def kpis(self) -> list:
        counts = self.typ.value_counts()
        clusters = pd.Series([c["typology"] for c in self.clusters]).value_counts()
        spec = [("Phantom Billing", "Dugaan Phantom Billing (Klaim Palsu)", "", "Peserta luar wilayah, kiriman serentak, dokter lintas faskes"),
                ("Repeat Billing", "Dugaan Repeat Billing", "⧉", "Klaim ulang peserta + diagnosis sama dalam 48 jam, lintas faskes"),
                ("Self-Referral", "Dugaan Rujukan tidak sesuai (Self-referral)", "⇄", "Dokter merujuk ke faskes tempat ia terdaftar, rujukan dua arah")]
        out = []
        for key, label, icon, note in spec:
            k = int(clusters.get(key, 0))
            out.append({"label": label, "badge": (f"{k} klaster", "red" if k else "grey"), "value": f"{int(counts.get(key, 0)):,}",
                        "icon": icon, "note": note})
        return out

    def trend(self):
        wk = ((self.flagged.visit_ts - PERIOD_START).dt.days // 7).clip(upper=12)
        labels = [f"W{i + 1:02d}" for i in range(13)]
        series = {}
        for key in ("Phantom Billing", "Repeat Billing", "Self-Referral"):
            cnt = wk[self.typ == key].value_counts()
            series[key] = [int(cnt.get(i, 0)) for i in range(13)]
        return labels, series

    def dashboard_footer(self) -> list:
        w = self.world
        n_auto = sum(c["score"] >= AUTO_FLAG for c in self.clusters)
        return [
            {"icon": "🕸", "label": "Entitas Dipantau (sintetis)",
             "value": f"{len(w.faskes)} faskes · {self.df.doctor_id.nunique()} dokter · {self.df.patient_id.nunique():,} peserta", "tone": "dark"},
            {"icon": "❋", "label": "Porsi Klaim Ditandai", "value": f"{len(self.flagged) / len(self.df):.1%}",
             "extra": f"({len(self.flagged):,} dari {len(self.df):,} klaim)", "tone": "dark"},
            {"icon": "", "label": "Antrean Verifikator Berikutnya", "value": f"{n_auto} klaster ≥{AUTO_FLAG}% menunggu tinjauan", "tone": "red"},
        ]

    # ------------------------------------------------------------------ pencarian
    def find(self, query: str):
        q = (query or "").lower().strip()
        if not q:
            return None
        fn = self.world.faskes.set_index("faskes_id").name
        for c in self.clusters:
            hay = " ".join([c["id"], c["name"], *c["faskes"], *[fn[f] for f in c["faskes"]], *c["doctors"]]).lower()
            if q in hay:
                return c["id"]
        return None


# ---------------------------------------------------------------------------
def _evidence(fl: pd.DataFrame, typ: str) -> list:
    """Bukti terukur dari fitur klaim ditandai (daftar: ikon, judul, catatan, (lencana, nada))."""
    out = []
    n = len(fl)
    sh = lambda m: float(m.mean())
    if typ == "Phantom Billing":
        a = sh(fl.f_out_region)
        out.append(("👥", "Peserta di luar wilayah", f"{_pct(a)} klaim berasal dari peserta berdomisili di luar wilayah faskes",
                    ("Anomali", "red") if a >= .5 else ("Perlu dicek", "amber")))
        b = sh(fl.f_burst_z > 2)
        out.append(("🕐", "Kiriman serentak", f"{_pct(b)} klaim dikirim serentak (hingga {int(fl.f_burst.max())} klaim dalam ±60 detik)",
                    ("Sinkronisasi", "amber") if b >= .3 else ("Rendah", "grey")))
        d = sh(fl.f_doc_conc >= 1)
        out.append(("🪪", "Dokter lintas faskes", f"{_pct(d)} klaim: dokter yang sama menagih di faskes lain dalam ±30 menit "
                    f"(hingga {int(fl.f_doc_conc.max()) + 1} faskes sekaligus)", ("Kritis", "red") if d >= .3 else ("Rendah", "grey")))
    elif typ == "Repeat Billing":
        dup = fl[fl.f_dup_recent == 1]
        a = len(dup) / n
        gap = float(dup.f_gap_prev_h.median()) if len(dup) else 0
        out.append(("🔁", "Klaim berulang", f"{_pct(a)} klaim ditagih ulang untuk peserta + diagnosis sama (median {gap:.0f} jam setelah klaim sebelumnya)",
                    ("Anomali", "red") if a >= .5 else ("Perlu dicek", "amber")))
        x = sh(dup.f_dup_cross) if len(dup) else 0
        out.append(("🏥", "Lintas faskes", f"{_pct(x)} klaim ulang ditagih oleh faskes berbeda dari klaim sebelumnya",
                    ("Sinkronisasi", "amber") if x >= .3 else ("Rendah", "grey")))
        t = sh(dup.f_tarif_match_prev <= .035) if len(dup) else 0
        out.append(("💰", "Tarif nyaris identik", f"{_pct(t)} klaim ulang bertarif sama dengan klaim sebelumnya (selisih ≤3,5%); "
                    f"pasangan faskes saling menagih ulang hingga {int(fl.f_dup_pair_cross.max())} kali",
                    ("Kritis", "red") if t >= .5 else ("Rendah", "grey")))
    elif typ == "Self-Referral":
        a = sh(fl.f_ref_internal)
        out.append(("↪", "Rujukan ke faskes sendiri", f"{_pct(a)} klaim berasal dari dokter perujuk yang terdaftar (SIP) di faskes tujuan",
                    ("Kritis", "red") if a >= .5 else ("Perlu dicek", "amber")))
        b = float(fl.f_doc_ref_internal.max())
        out.append(("📈", "Konsentrasi rujukan", f"hingga {_pct(b)} rujukan satu dokter berakhir di faskes terafiliasinya",
                    ("Anomali", "red") if b >= .6 else ("Rendah", "grey")))
        r = sh(fl.f_ref_reciprocity >= .2)
        out.append(("⇄", "Rujukan dua arah", f"{_pct(r)} klaim berada pada pasangan faskes yang saling merujuk (siklus)",
                    ("Sinkronisasi", "amber") if r >= .2 else ("Rendah", "grey")))
    else:
        out.append(("◆", "Skor model tinggi", "Klaim berskor tinggi tanpa pola tipologi yang dikenali aturan penjelas.", ("Perlu dicek", "amber")))
    return out


def _why(typ: str, ev: list, n: int) -> str:
    head = {"Phantom Billing": "Dugaan Phantom Billing (Klaim Palsu)", "Repeat Billing": "Dugaan Repeat Billing",
            "Self-Referral": "Dugaan Rujukan tidak sesuai (Self-referral)"}.get(typ, "Anomali jaringan")
    body = "; ".join(e[2] for e in ev[:2])
    return f"{head} pada {n} klaim ditandai: {body}."


def _timeline(df_all: pd.DataFrame, fl: pd.DataFrame, faskes: list):
    edges = np.linspace(0, PERIOD_DAYS, 7)
    labels, flagged, others = [], [], []
    base = df_all[df_all.faskes_id.isin(faskes) & ~df_all.index.isin(fl.index)]
    vd_f = (fl.visit_ts - PERIOD_START).dt.total_seconds() / 86400
    vd_o = (base.visit_ts - PERIOD_START).dt.total_seconds() / 86400
    for lo, hi in zip(edges[:-1], edges[1:]):
        d0 = PERIOD_START + pd.Timedelta(days=float(lo))
        labels.append(f"{d0.day:02d} {_MONTH.get(d0.month, d0.strftime('%b'))}")
        flagged.append(int(((vd_f >= lo) & (vd_f < hi)).sum()))
        others.append(int(((vd_o >= lo) & (vd_o < hi)).sum()))
    peak_day = fl.visit_ts.dt.floor("D").value_counts()
    peak = f"{int(peak_day.max())} klaim/hari ({peak_day.idxmax().strftime('%d/%m')})" if len(peak_day) else ""
    return {"labels": labels, "flagged": flagged, "others": others}, peak


def link_counts(flagged: pd.DataFrame) -> dict:
    """Bobot sisi antar-faskes dari klaim ditandai: jumlah rujukan, dokter yang sama, dan peserta yang sama
    yang menghubungkan dua faskes. Kunci: (faskes_a, faskes_b) terurut."""
    cnt: dict = {}

    def add(a, b):
        if a != b and pd.notna(a) and pd.notna(b):
            k = tuple(sorted((a, b)))
            cnt[k] = cnt.get(k, 0) + 1

    for a, b in zip(flagged.faskes_id, flagged.referral_from_faskes):
        add(a, b)
    for key in ("doctor_id", "patient_id"):
        for _, g in flagged.groupby(key):
            fs = sorted(g.faskes_id.unique())
            for i in range(len(fs)):
                for j in range(i + 1, len(fs)):
                    add(fs[i], fs[j])
    return cnt


def build(world: World, scored: pd.DataFrame, thr: float = THRESH, min_edge: int = MIN_EDGE, seed: int = SEED) -> Live:
    """scored: keluaran core.evaluate.benchmark(...).scored (fitur + score_graph). Kolom label diabaikan."""
    df = world.claims.set_index("claim_id").join(scored[FEATURES + ["score_graph"]])
    flagged = df[df.score_graph >= thr].copy()
    typ = flagged.apply(lambda r: explain(r)["typology"], axis=1).fillna("Tidak terklasifikasi")

    # graf faskes dari klaim ditandai
    cnt = link_counts(flagged)
    G = nx.Graph()
    G.add_nodes_from(flagged.faskes_id.unique())
    G.add_weighted_edges_from((a, b, n) for (a, b), n in cnt.items() if n >= min_edge)
    comms = nx.community.louvain_communities(G, weight="weight", seed=seed)
    mod = float(nx.community.modularity(G, comms, weight="weight")) if G.number_of_edges() else 0.0

    live = Live(world=world, df=df, flagged=flagged, typ=typ, G=G, modularity=mod)
    faskes = world.faskes.set_index("faskes_id")
    ndoc_all = df.groupby("doctor_id").faskes_id.nunique()
    for cm in comms:
        fl = flagged[flagged.faskes_id.isin(cm)]
        if len(fl) < MIN_CLAIMS:
            continue
        order = list(fl.faskes_id.value_counts().index)
        top = np.sort(fl.score_graph.values)[::-1][:max(5, int(0.2 * len(fl)))]
        score = int(round(100 * float(top.mean())))
        tvc = typ.loc[fl.index].value_counts()
        tvc = tvc[tvc.index != "Tidak terklasifikasi"]
        tname = str(tvc.index[0]) if len(tvc) else "Tidak terklasifikasi"
        names = [faskes.loc[f, "name"] for f in order]
        names_s = ", ".join(names[:2]) + (f" +{len(names) - 2} faskes" if len(names) > 2 else "")
        ev = _evidence(fl, tname)
        doctors = list(fl.doctor_id.value_counts().index)
        sub = G.subgraph(order)
        density = float(nx.density(sub)) if len(order) > 1 else 0.0
        # sentralitas: graf entitas (faskes-dokter-peserta) dari klaim ditandai di klaster
        eg = nx.Graph()
        for r in fl.itertuples():
            eg.add_edge(f"F:{r.faskes_id}", f"D:{r.doctor_id}")
            eg.add_edge(f"F:{r.faskes_id}", f"P:{r.patient_id}")
        cen = nx.degree_centrality(eg)
        cname, cval = max(cen.items(), key=lambda kv: kv[1])
        kind, ident = cname.split(":")
        central = (f"{'Dokter' if kind == 'D' else 'Faskes' if kind == 'F' else 'Peserta'} {ident}" if kind != "F"
                   else f"{faskes.loc[ident, 'name']}", cval)
        tl, peak = _timeline(df, fl, order)
        rows = []
        for f in order:
            sf = fl[fl.faskes_id == f]
            inr = int(sf.referral_from_faskes.notna().sum())
            outr = int((fl.referral_from_faskes == f).sum())
            if f == order[0]:
                role = ("Simpul Utama", "red")
            elif inr > outr and inr:
                role = ("Penerima Rujukan", "amber")
            elif outr > inr:
                role = ("Pengirim Rujukan", "amber")
            else:
                role = ("Anggota Klaster", "green")
            rows.append((f"{f} · {faskes.loc[f, 'name']}", faskes.loc[f, "region"], TYPE_LABEL[faskes.loc[f, "type"]], role,
                         len(sf), rp(sf.tarif.sum())))
        c = {
            "id": f"JALA-{min(cm)}", "faskes": order, "idx": list(fl.index), "n": len(fl), "value": int(fl.tarif.sum()),
            "score": score, "typology": tname, "name": f"Jejaring {names[0]}" + (f" (+{len(order) - 1} faskes)" if len(order) > 1 else ""),
            "subtitle": f"{names_s} · {len(doctors)} dokter terkait", "faskes_names": names_s, "doctors": doctors, "n_doctors": len(doctors),
            "regions": sorted({faskes.loc[f, "region"] for f in order}),
            "metric": f"{len(fl)} klaim ditandai · skor tertinggi {fl.score_graph.max():.2f}",
            "evidence": ev, "why": _why(tname, ev, len(fl)), "timeline": tl, "peak": peak, "density": density,
            "central": central, "faskes_rows": rows,
            "fedges": [(a, b, int(d["weight"])) for a, b, d in sub.edges(data=True)],
        }
        live.clusters.append(c)
    live.clusters.sort(key=lambda c: (-c["score"], -c["n"]))
    live.by_id = {c["id"]: c for c in live.clusters}
    return live


# ---------------------------------------------------------------------------
def evaluate_clusters(live: Live) -> dict:
    """Menilai klaster terhadap label tersembunyi (HANYA evaluasi): berapa kelompok fraud yang terpulihkan?

    Kelompok terpulihkan bila >=80% klaim fraud-nya yang ditandai jatuh di satu klaster dan >=80% klaim ditandai
    klaster itu berasal dari kelompok tersebut (murni).
    """
    lab = live.world.labels.set_index("claim_id")
    fl = live.flagged.join(lab[["is_fraud", "group"]])
    groups = sorted(g for g in lab.group.unique() if g)
    rec, per = 0, {}
    for g in groups:
        gm = fl[(fl.group == g) & (fl.is_fraud == 1)]
        if gm.empty:
            per[g] = False
            continue
        best = max(live.clusters, key=lambda c: gm.index.isin(c["idx"]).sum())
        share = gm.index.isin(best["idx"]).sum() / len(gm)
        purity = (fl.loc[best["idx"], "group"] == g).mean()
        ok = bool(share >= .8 and purity >= .8)
        per[g] = ok
        rec += ok
    pure_fraud = [c for c in live.clusters if (fl.loc[c["idx"], "is_fraud"] == 1).mean() >= .5]
    return {
        "n_groups": len(groups), "recovered": int(rec), "per_group": per,
        "n_clusters": len(live.clusters), "clusters_mostly_fraud": len(pure_fraud),
        "clusters_without_fraud": sum(float(fl.loc[c["idx"], "is_fraud"].mean()) == 0 for c in live.clusters),
        "flagged_precision": float(fl.is_fraud.mean()),
        "flagged_recall": float(fl.is_fraud.sum() / lab.is_fraud.sum()),
    }
