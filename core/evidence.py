"""Berkas bukti per klaster: satu zip yang bisa diserahkan ke pemeriksa dokumen.

Isi zip: ringkasan.md, klaim_terkait.csv, faskes.csv, dokter.csv (termasuk dampak jika dokter dikeluarkan),
subgraf.svg (gambar jaringan, tanpa dependensi tambahan) dan subgraf.json.

Posisi Jala: lapisan penyaring di depan. Berkas ini memprioritaskan apa yang diperiksa, bukan temuan;
keputusan akhir ada pada verifikator. Data prototipe ini sintetis.
"""
from __future__ import annotations

import io
import json
import zipfile
from html import escape

import pandas as pd

from core import modus, whatif
from core.detect import explain
from core.live import AUTO_FLAG, Live
from core.synthetic import TYPE_LABEL

CHECKLIST = {
    "Phantom Billing": [
        "Konfirmasi keberadaan peserta (identitas, domisili) dan bukti kunjungan di tiap faskes.",
        "Cocokkan jadwal praktik dan SIP dokter dengan jam pelayanan pada klaim yang serentak.",
        "Bandingkan pola pengiriman klaim serentak dengan faskes sejenis di wilayah yang sama.",
    ],
    "Repeat Billing": [
        "Bandingkan tanggal/jam pelayanan dan nomor SEP pada klaim berulang.",
        "Periksa apakah ada indikasi medis yang sah untuk kunjungan ulang (mis. dialisis terjadwal, kontrol UGD).",
        "Periksa klaim ulang lintas faskes yang saling menagih pasien yang sama.",
    ],
    "Self-Referral": [
        "Periksa afiliasi dan kepemilikan dokter perujuk pada faskes tujuan (SIP).",
        "Periksa indikasi medis rujukan dan rujukan balik.",
        "Bandingkan dengan alternatif faskes rujukan terdekat untuk pasien yang sama.",
    ],
}


def _rp(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def _md_cell(x) -> str:
    return str(x).replace("|", "\\|").replace("\n", " ")


def claims_table(live: Live, cid: str) -> pd.DataFrame:
    c = live.by_id[cid]
    fl = live.flagged.loc[c["idx"]]
    names = live.world.faskes.set_index("faskes_id").name
    rows = []
    for claim_id, r in fl.iterrows():
        ex = explain(r)
        rows.append({
            "claim_id": claim_id, "faskes_id": r.faskes_id, "faskes": names[r.faskes_id], "doctor_id": r.doctor_id,
            "patient_id": r.patient_id, "icd": r.icd, "tarif_rp": int(r.tarif),
            "visit_ts": str(r.visit_ts), "submit_ts": str(r.submit_ts),
            "referral_from_faskes": r.referral_from_faskes if pd.notna(r.referral_from_faskes) else "",
            "referral_from_doctor": r.referral_from_doctor if pd.notna(r.referral_from_doctor) else "",
            "skor": round(float(r.score_graph), 4), "dugaan_tipologi": ex["typology"] or "",
            "alasan": "; ".join(ex["reasons"]),
        })
    return pd.DataFrame(rows).sort_values("skor", ascending=False).reset_index(drop=True)


def faskes_table(live: Live, cid: str) -> pd.DataFrame:
    c = live.by_id[cid]
    fl = live.flagged.loc[c["idx"]]
    fk = live.world.faskes.set_index("faskes_id")
    g = fl.groupby("faskes_id").agg(klaim_ditandai=("tarif", "size"), nilai_tarif_rp=("tarif", "sum")).reset_index()
    g["nama"] = g.faskes_id.map(fk.name)
    g["tipe"] = g.faskes_id.map(lambda f: TYPE_LABEL[fk.loc[f, "type"]])
    g["wilayah"] = g.faskes_id.map(fk.region)
    g["nilai_tarif_rp"] = g.nilai_tarif_rp.astype(int)
    return g[["faskes_id", "nama", "tipe", "wilayah", "klaim_ditandai", "nilai_tarif_rp"]] \
        .sort_values("klaim_ditandai", ascending=False).reset_index(drop=True)


def doctor_table(live: Live, cid: str) -> pd.DataFrame:
    c = live.by_id[cid]
    fl = live.flagged.loc[c["idx"]]
    aff = live.world.affiliations.groupby("doctor_id").faskes_id.apply(lambda s: ",".join(sorted(s)))
    ranked = {r["doctor"]: r for r in whatif.rank_doctors(live, cid, top=25)}
    rows = []
    for d, r in ranked.items():
        sub = fl[fl.doctor_id == d]
        rows.append({
            "doctor_id": d, "klaim_menangani": len(sub), "klaim_merujuk": int((fl.referral_from_doctor == d).sum()),
            "faskes_menagih": ",".join(sorted(sub.faskes_id.unique())), "terdaftar_sip_di": aff.get(d, ""),
            "peran_struktur": r["role"], "klaim_terkait_pct": round(100 * r["claims_share"], 1),
            "bobot_hubungan_hilang_pct": round(100 * r["weight_lost_share"], 1),
            "komponen_sebelum": r["components_before"], "komponen_sesudah": r["components_after"],
            "jika_dikeluarkan": r["verdict"],
        })
    return pd.DataFrame(rows)


def _print_layout(nodes: list[dict], edges: list[dict], W: int, H: int) -> dict:
    """Tata letak untuk cetak: faskes inti melingkar (tetap, agar tidak menumpuk), pembanding di kiri, sisanya mengambang."""
    import math
    import networkx as nx
    core = [n["id"] for n in nodes if n["type"] == "faskes" and n.get("risk")]
    peer = [n["id"] for n in nodes if n["type"] == "faskes" and not n.get("risk")]
    init, k = {}, len(core)
    for i, nid in enumerate(core):
        a = 2 * math.pi * i / max(k, 1) + math.pi / 2
        init[nid] = (0.6 + 0.2 * math.cos(a), 0.5 + 0.2 * math.sin(a)) if k > 1 else (0.6, 0.5)
    for j, nid in enumerate(peer):
        init[nid] = (0.07, 0.5 + 0.15 * j)
    g = nx.Graph()
    g.add_nodes_from(n["id"] for n in nodes)
    g.add_edges_from((e["src"], e["dst"]) for e in edges if e["src"] != e["dst"])
    pos = nx.spring_layout(g, pos=init, fixed=list(init) or None, k=0.2, iterations=250, seed=7) if len(g) > 1 else {nodes[0]["id"]: (0.5, 0.5)}
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    sx, sy = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    return {nid: (80 + (p[0] - min(xs)) / sx * (W - 160), 100 + (p[1] - min(ys)) / sy * (H - 230)) for nid, p in pos.items()}


def subgraph_svg(nodes: list[dict], edges: list[dict], title: str) -> str:
    W, H = 1000, 700
    pos = _print_layout(nodes, edges, W, H)
    color = {"faskes": "#0F766E", "dokter": "#F97316", "pasien": "#64748B", "icd": "#475569"}
    dash = {"solid": "", "dash": ' stroke-dasharray="7 5"', "dot": ' stroke-dasharray="2 5"'}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Arial,sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#F8FAFC"/>',
           f'<text x="24" y="34" font-size="18" font-weight="700" fill="#132A1C">{escape(title)}</text>',
           '<text x="24" y="54" font-size="11" fill="#64748B">Prototipe pada data sintetis · garis putus-putus: dokter, titik-titik: diagnosis, tebal: antar-faskes</text>']
    for e in edges:
        if e["src"] not in pos or e["dst"] not in pos:
            continue
        (x1, y1), (x2, y2) = pos[e["src"]], pos[e["dst"]]
        col = "#B91C1C" if e.get("risk") else "#CBD5E1"
        w = 3 if e["src"].startswith("f_") and e["dst"].startswith("f_") else 1.4
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" '
                   f'opacity=".65"{dash.get(e.get("style", "solid"), "")}/>')
        if e.get("label"):
            out.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{(y1 + y2) / 2 - 3:.1f}" font-size="9" fill="#64748B" '
                       f'text-anchor="middle">{escape(str(e["label"]))}</text>')
    for n in nodes:
        x, y = pos[n["id"]]
        col, op = color.get(n["type"], "#64748B"), (1 if n.get("risk") else .45)
        stroke = "#B91C1C" if n.get("risk") else "#94A3B8"
        if n["type"] == "faskes":
            shape = f'<rect x="{x - 15:.1f}" y="{y - 15:.1f}" width="30" height="30" rx="5" fill="{col}" opacity="{op}" stroke="{stroke}" stroke-width="2"/>'
        elif n["type"] == "icd":
            shape = f'<rect x="{x - 12:.1f}" y="{y - 8:.1f}" width="24" height="16" rx="8" fill="{col}" opacity="{op}"/>'
        else:
            shape = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{11 if n["type"] == "dokter" else 8}" fill="{col}" opacity="{op}" stroke="{stroke}" stroke-width="1.5"/>'
        out.append(shape)
        out.append(f'<text x="{x:.1f}" y="{y + 29:.1f}" font-size="10.5" font-weight="600" fill="#132A1C" text-anchor="middle">{escape(n["label"])}</text>')
        if n.get("sub"):
            out.append(f'<text x="{x:.1f}" y="{y + 41:.1f}" font-size="9" fill="#64748B" text-anchor="middle">{escape(n["sub"])}</text>')
    lx = 24
    for k, lab in (("faskes", "Faskes"), ("dokter", "Dokter"), ("pasien", "Peserta"), ("icd", "Diagnosis (ICD)")):
        out.append(f'<circle cx="{lx + 6}" cy="{H - 24}" r="6" fill="{color[k]}"/><text x="{lx + 18}" y="{H - 20}" font-size="11" fill="#475569">{lab}</text>')
        lx += 130
    out.append(f'<text x="{lx + 10}" y="{H - 20}" font-size="11" fill="#B91C1C">Garis/merah: klaim ditandai · pudar: pembanding normal</text>')
    out.append("</svg>")
    return "\n".join(out)


def summary_md(live: Live, cid: str, feedback: dict | None, generated_at: str, doc_df: pd.DataFrame,
               fk_df: pd.DataFrame, cl_df: pd.DataFrame) -> str:
    c = live.by_id[cid]
    fl = live.flagged.loc[c["idx"]]
    s = c["score"]
    status = "Auto-Flagged" if s >= AUTO_FLAG else "Standard Review"
    fb = (feedback or {}).get(cid)
    score_line = f"{s}% ({status})"
    if c.get("score_base") is not None and c["score_base"] != s:
        score_line += f", skor dasar {c['score_base']}% sebelum umpan balik verifikator"
    L = [f"# Berkas Bukti Klaster {cid}", "",
         f"Dibuat: {generated_at}", "",
         "> **Prototipe pada data sintetis.** Berkas ini memprioritaskan pemeriksaan, bukan temuan. "
         "Keputusan akhir ada pada verifikator. JALA berposisi sebagai lapisan penyaring sebelum pemeriksaan dokumen.", "",
         "## 1. Ringkasan", "", "| Item | Nilai |", "|---|---|",
         f"| Nama klaster | {_md_cell(c['name'])} |", f"| Skor jaringan | {score_line} |",
         f"| Dugaan tipologi | {c['typology']} |",
         f"| Klaim ditandai | {c['n']} klaim, total tarif Rp {_rp(fl.tarif.sum())} |",
         f"| Faskes terkait | {len(c['faskes'])} ({_md_cell(c['faskes_names'])}) |",
         f"| Dokter terkait | {c['n_doctors']} |",
         f"| Wilayah | {', '.join(c['regions'])} |",
         f"| Rentang kunjungan | {fl.visit_ts.min():%Y-%m-%d} s.d. {fl.visit_ts.max():%Y-%m-%d} |",
         f"| Puncak klaim | {c['peak']} |", f"| Kepadatan graf faskes | {c['density']:.2f} |", "",
         "## 2. Mengapa ditandai", "", c["why"], ""]
    m = modus.info(c["typology"])
    if m:
        L += [f"**{modus.headline(c['typology'])}.** Definisi: {m['definisi']}", "",
              f"**Batas pembuktian:** {m['batas']}", ""]
    L += ["### Bukti terukur", ""]
    for icon, title, note, (badge, _tone) in c["evidence"]:
        L.append(f"- **{title}** [{badge}]: {note}")
    L += ["", "## 3. Faskes dalam klaster", "",
          "| Faskes | Nama | Tipe | Wilayah | Klaim | Tarif (Rp) |", "|---|---|---|---|---|---|"]
    for r in fk_df.itertuples():
        L.append(f"| {r.faskes_id} | {_md_cell(r.nama)} | {r.tipe} | {r.wilayah} | {r.klaim_ditandai} | {_rp(r.nilai_tarif_rp)} |")
    L += ["", "## 4. Dokter dan struktur jaringan", "",
          "Simulasi struktural: klaim dokter dibuang dari klaster, lalu graf antar-faskes dihitung ulang. "
          "Ini bukan penilaian peran hukum dokter.", "",
          "| Dokter | Peran | Klaim terkait | Bobot hubungan hilang | Klaster |", "|---|---|---|---|---|"]
    for r in doc_df.head(8).itertuples():
        L.append(f"| {r.doctor_id} | {r.peran_struktur} | {r.klaim_terkait_pct:.0f}% | {r.bobot_hubungan_hilang_pct:.0f}% | "
                 f"{r.komponen_sebelum} → {r.komponen_sesudah} bagian |")
    if len(doc_df):
        L += ["", f"Contoh: {doc_df.iloc[0].jika_dikeluarkan}"]
    L += ["", f"## 5. Klaim terkait ({len(cl_df)} klaim; lengkap di klaim_terkait.csv, 10 teratas)", "",
          "| Klaim | Faskes | Dokter | ICD | Skor | Alasan |", "|---|---|---|---|---|---|"]
    for r in cl_df.head(10).itertuples():
        L.append(f"| {r.claim_id} | {r.faskes_id} | {r.doctor_id} | {r.icd} | {r.skor:.2f} | {_md_cell(r.alasan) or '-'} |")
    L += ["", "## 6. Saran untuk pemeriksa dokumen", "",
          "_Daftar ini saran kerja, bukan ketentuan regulasi._", ""]
    L += [f"- [ ] {x}" for x in CHECKLIST.get(c["typology"], ["Periksa pola klaim sesuai catatan di atas."])]
    L += ["", "## 7. Keputusan verifikator", ""]
    if fb:
        L.append(f"- Keputusan: **{fb['verdict']}** pada {fb['at']}" + (f". Catatan: {fb['note']}" if fb.get("note") else "."))
    else:
        L.append("- Belum ada keputusan pada klaster ini.")
    L += ["", "## 8. Batasan", "", f"- {modus.PRINSIP}",
          "- Data sintetis; skor dihitung fitur graf + gradient boosting, bukan GNN/HAN.",
          "- Klaster adalah prioritas pemeriksaan. Klaster dengan pola sah (mis. dialisis terjadwal) juga bisa tertandai.",
          "- Alasan per klaim dihasilkan otomatis dari fitur teramati dan perlu diverifikasi manusia.", ""]
    return "\n".join(L)


def build_pack(live: Live, cid: str, feedback: dict | None = None, generated_at: str | None = None,
               role: str = "Supervisor") -> bytes:
    from datetime import datetime
    from core.privacy import mask_graph, mask_participant_id
    ts = generated_at or datetime.now().strftime("%Y-%m-%d %H:%M")
    cl, fk, dk = claims_table(live, cid), faskes_table(live, cid), doctor_table(live, cid)
    nodes, edges = live.graph(cid)[:2]
    if role == "Verifikator":
        cl["patient_id"] = cl["patient_id"].map(mask_participant_id)
        nodes, edges = mask_graph(nodes, edges)
    nodes_j = [{k: (float(v) if k in ("x", "y") else v) for k, v in n.items()} for n in nodes]
    svg = subgraph_svg(nodes_j, edges, f"Subgraf {cid} · {live.by_id[cid]['typology']}")
    files = {
        "ringkasan.md": summary_md(live, cid, feedback, ts, dk, fk, cl),
        "klaim_terkait.csv": cl.to_csv(index=False),
        "faskes.csv": fk.to_csv(index=False),
        "dokter.csv": dk.to_csv(index=False),
        "subgraf.svg": svg,
        "subgraf.json": json.dumps({"nodes": nodes_j, "edges": edges}, ensure_ascii=False, indent=1),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(f"{cid}/{name}", text.encode("utf-8"))
    return buf.getvalue()
