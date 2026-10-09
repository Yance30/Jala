"""Alat bantu verifikator di layar: berkas bukti, simulasi "dokter dikeluarkan", dan umpan balik dismiss."""
from html import escape
import csv
import io
from datetime import datetime

import streamlit as st
from data.mock_data import FOOTER_CUTOFF, QUARTER

from components import bench, cards
from core import evidence, feedback, modus, whatif
from core.synthetic import SEED

_REVIEW_CSV_COLUMNS = [
    "event_id", "case_id", "at", "actor", "action", "note", "score_before", "score_after",
    "lingkungan_data", "periode_data", "batas_data", "waktu_ekspor",
]


def review_history_csv(history: list[dict]) -> bytes:
    """Buat ekspor UTF-8 BOM agar langsung terbaca rapi di spreadsheet umum."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=_REVIEW_CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for event in history:
        row = {column: event.get(column, "") for column in _REVIEW_CSV_COLUMNS}
        row.update({"lingkungan_data": "Data sintetis; prototipe", "periode_data": QUARTER,
                    "batas_data": FOOTER_CUTOFF,
                    "waktu_ekspor": datetime.now().astimezone().isoformat(timespec="seconds")})
        writer.writerow(row)
    return stream.getvalue().encode("utf-8-sig")


def review_timeline(cid: str, key: str) -> None:
    """Tampilkan jejak keputusan untuk satu klaster pada sesi demo aktif."""
    history = bench.get_review_history(cid)
    with st.expander("Riwayat pemeriksaan klaster", key=key):
        storage_error = st.session_state.get("review_history_error")
        if storage_error:
            st.warning(storage_error + " Catatan hanya tersedia pada sesi aktif.")
        elif bench.review_history_persistent():
            st.caption(
                "Tersimpan di basis data lokal instance demo dan dapat terlihat oleh pengguna instance ini. "
                "Gunakan ID serta catatan sintetis; jangan masukkan data pribadi atau data nyata."
            )
        else:
            st.caption(
                "Catatan hanya tersimpan pada sesi aktif Anda dan hilang saat sesi berakhir. "
                "Gunakan ID serta catatan sintetis; jangan masukkan data pribadi atau data nyata."
            )
        if not history:
            st.caption("Belum ada tindakan tercatat untuk klaster ini.")
            return
        st.download_button(
            "Unduh riwayat kasus (.CSV)",
            data=review_history_csv(history),
            file_name=f"jala_riwayat_{cid}.csv",
            mime="text/csv; charset=utf-8",
            key=f"{key}_download",
            width="stretch",
        )
        for event in reversed(history):
            note = escape(event.get("note", ""))
            before, after = event.get("score_before"), event.get("score_after")
            score_text = ""
            if before is not None and after is not None:
                score_text = (
                    f"Skor prioritas: {before}% → {after}%"
                    if before != after else f"Skor prioritas tidak berubah ({after}%)"
                )
            note_html = (f'<div style="margin-top:7px;font-size:13px;white-space:pre-wrap;'
                         f'overflow-wrap:anywhere;">{note}</div>' if note else "")
            st.markdown(
                f'<div class="j-card" style="margin:8px 0;padding:12px 14px;">'
                f'<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;">'
                f'<b>{escape(event["action"])}</b><span class="j-sub">{escape(event["at"])}</span></div>'
                f'<div class="j-sub" style="margin-top:3px;">{escape(event["actor"])} · {score_text}</div>'
                f'{note_html}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------- berkas bukti
def _feedback_signature(feedback: dict) -> tuple:
    """Bentuk hashable dari keputusan verifikator agar cache paket bukti invalid saat umpan balik berubah."""
    return tuple(sorted(
        (cid, item.get("verdict"), item.get("note", ""), item.get("at", ""))
        for cid, item in feedback.items()
    ))


@st.cache_data(show_spinner=False)
def _build_evidence_pack(cid: str, role: str, signature: tuple, seed: int) -> bytes:
    live = bench.get_live(seed)
    return evidence.build_pack(live, cid, bench.get_feedback(), role=role)


def evidence_button(cid: str, key: str) -> None:
    role = st.session_state.get("demo_role", "Verifikator")
    pack = _build_evidence_pack(cid, role, _feedback_signature(bench.get_feedback()), SEED)
    st.download_button(
        "Unduh paket pemeriksaan (.zip)", pack,
        file_name=f"jala_bukti_{cid}.zip", mime="application/zip", width="stretch", key=key,
        help="Ringkasan, klaim terkait, faskes, dokter, dampak jika dokter dikeluarkan, dan gambar subgraf, "
             "untuk diserahkan ke pemeriksa dokumen.",
    )


# ---------------------------------------------------------------- umpan balik
def _changes(live):
    return feedback.changes(bench.get_live_base(), live)


def feedback_card(live, cid: str) -> None:
    """Kartu di Audit Action: status umpan balik klaster ini dan dampaknya pada antrean."""
    fb = bench.get_feedback()
    c = live.by_id[cid]
    info = c.get("fb")
    if not info:
        return
    rank = [x["id"] for x in live.clusters].index(cid) + 1
    base = c["score_base"]
    if info["kind"] == "dismiss":
        head = f"Pola ditandai wajar pada {fb[cid]['at']}. Skor {base}% → <b>{c['score']}%</b>, urutan saat ini #{rank}."
    elif info["kind"] == "similar":
        head = (f"Skor diturunkan {base}% → <b>{c['score']}%</b> (urutan #{rank}) karena pola diagnosis serupa "
                f"({info['sim']:.2f}) dengan {info['source']} yang ditandai wajar. Klaster ini sendiri belum diputuskan: "
                f"tinjau, atau batalkan catatan pola wajar di {info['source']} bila keliru.")
    else:
        head = f"Simulasi penangguhan dikonfirmasi pada {fb[cid]['at']}. Tidak ada pembayaran yang ditangguhkan."
    effects = [feedback.describe(x) for x in _changes(live) if x["source"] == cid and x["id"] != cid]
    lis = "".join(f"<li>{e}</li>" for e in effects)
    st.markdown(
        f"""
        <div class="j-alert-teal" style="margin:12px 0;">
          <b>🔁 UMPAN BALIK VERIFIKATOR</b>
          <span class="j-pill grey" style="margin-left:8px;">Kalibrasi ringan · belum melatih ulang model</span>
          <div style="margin-top:8px;">{head}</div>
          {f'<div class="j-label" style="margin:10px 0 4px;">Klaster lain yang ikut berubah</div><ul style="margin:0 0 0 18px;font-size:13px;">{lis}</ul>' if lis else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if info["kind"] in ("dismiss", "confirm") and st.button("↩ Batalkan umpan balik klaster ini", key=f"undo_{cid}"):
        bench.undo_verdict(cid)
        st.rerun()


def feedback_banner(live) -> None:
    """Spanduk di Risk Ranking: ringkasan seluruh umpan balik sesi ini dan tombol atur ulang."""
    fb = bench.get_feedback()
    if not fb:
        return
    ch = _changes(live)
    lis = "".join(f"<li>{feedback.describe(x)}</li>" for x in ch[:8])
    st.markdown(
        f"""
        <div class="j-alert-teal" style="margin:0 0 14px;">
          <b>🔁 UMPAN BALIK VERIFIKATOR AKTIF</b>
          <span class="j-pill grey" style="margin-left:8px;">{len(fb)} keputusan · {len(ch)} klaster berubah</span>
          <ul style="margin:8px 0 0 18px;font-size:13px;">{lis}</ul>
          <div class="j-sub" style="margin-top:6px;">Skor diturunkan secara heuristik (dismiss ×{feedback.DISMISS_FACTOR:g};
            klaster serupa hingga −{feedback.SIMILAR_MAX_DROP:.0%}), tidak disembunyikan, dan bisa dibatalkan. Hanya berlaku pada sesi ini.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("↩ Atur ulang umpan balik", key="fb_reset"):
        bench.reset_feedback()
        st.rerun()


# ---------------------------------------------------------------- dokter dikeluarkan
def whatif_panel(live, cid: str) -> None:
    ranked = whatif.rank_doctors(live, cid)
    st.markdown(
        """
        <div class="j-h2" style="margin-top:18px;">🧩 Simulasi: bagaimana kalau dokter ini dikeluarkan?</div>
        <div class="j-sub" style="margin:4px 0 8px;">Klaim dokter dibuang dari klaster, lalu graf antar-faskes dihitung ulang.
          Menunjukkan siapa inti jaringan. Simulasi struktural, bukan penilaian peran hukum dokter.</div>
        """,
        unsafe_allow_html=True,
    )
    if not ranked:
        st.caption("Klaster ini tidak memiliki dokter terkait.")
        return
    by_doc = {r["doctor"]: r for r in ranked}
    pick = st.selectbox(
        "Dokter", list(by_doc), key=f"wi_{cid}", label_visibility="collapsed",
        format_func=lambda d: f"Dokter {d} · {by_doc[d]['role']} · {by_doc[d]['claims_share']:.0%} klaim",
    )
    r = by_doc[pick]
    tone = {"inti": "red", "pendukung": "dark", "periferal": "teal"}[r["role"]]
    cols = st.columns(4)
    for col, (lab, val, note) in zip(cols, [
        ("PERAN STRUKTUR", r["role"].capitalize(), f"{r['claims_removed']} dari {r['claims_total']} klaim terkait"),
        ("KLASTER", f"{r['components_before']} → {r['components_after']}", "bagian setelah dikeluarkan"),
        ("HUBUNGAN HILANG", f"{r['weight_lost_share']:.0%}", f"bobot {r['weight_before']} → {r['weight_after']}"),
        ("FASKES TERPUTUS", str(len(r["faskes_cut"]) + len(r["faskes_lost"])),
         ", ".join(r["faskes_lost"] + r["faskes_cut"]) or "tidak ada"),
    ]):
        with col:
            st.markdown(cards.metric_card(lab, val, note=note, value_tone=tone if lab == "PERAN STRUKTUR" else "dark",
                                          card_class="j-whatif-card"),
                        unsafe_allow_html=True)
    st.markdown(f'<div class="j-note" style="margin-top:10px;"><span>ⓘ</span><div>{r["verdict"]}</div></div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------- posisi modus
def modus_note(typology: str) -> None:
    """Catatan di layar: modus Healthkathon yang dituju dan batas pembuktiannya (JALA = prioritas pemeriksaan)."""
    m = modus.info(typology)
    if not m:
        return
    st.markdown(
        f"""
        <div class="j-note" style="margin-top:10px;"><span>ⓘ</span><div>
          <b>{modus.headline(typology)}</b><br>
          <span style="color:#475569;">{m['definisi']}</span><br>
          <b>Batas pembuktian:</b> {m['batas']}<br>
          <i>{modus.PRINSIP}</i>
        </div></div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- penanda ketidakpastian (false positive)
def benign_note(live, cid: str) -> None:
    """Kemungkinan penjelasan sah untuk klaster ini, dari kolom teramati saja.

    Menampilkan penanda ketidakpastian agar verifikator mengonfirmasi konteks klinis sebelum menindaklanjuti
    (mis. klaster dialisis terjadwal yang polanya mirip repeat billing). Bila tidak ada penanda spesifik,
    tidak menampilkan apa pun agar tidak menambah kebisingan; panduan generik sudah ada di modus_note.
    """
    items = live.benign(cid)
    if not items:
        return
    lis = "".join(f'<li style="margin-bottom:4px;">{i["icon"]} {escape(i["text"])}</li>' for i in items)
    st.markdown(
        f"""
        <div class="j-alert-teal" style="margin:10px 0;background:#FFFBEB;border-color:#FCD34D;">
          <b>⚖ Kemungkinan penjelasan sah — periksa sebelum menyimpulkan</b>
          <span class="j-pill grey" style="margin-left:8px;">Penanda ketidakpastian</span>
          <ul style="margin:8px 0 0 18px;font-size:13px;color:#475569;">{lis}</ul>
          <div class="j-sub" style="margin-top:6px;">Sinyal dihitung dari kolom teramati (kode diagnosis), bukan dari label.
            Konfirmasi konteks klinis dengan verifikator sebelum menindaklanjuti klaster ini.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

