"""Review uploaded batch predictions; queues and decisions persist in local SQLite."""
import json
import sqlite3
import pandas as pd

import streamlit as st

from core import batch_store
from core.evaluate import percentile_rank
from core.review_queue import STATUSES, PRIORITIES, export, progress
from core.csv_export import safe_csv


def format_value(field, value):
    if field == "tarif":
        return "Rp " + f"{float(value):,.0f}".replace(",", ".")
    if field in ("visit_ts", "submit_ts"):
        return pd.to_datetime(value, utc=True).strftime("%d/%m/%Y %H:%M:%S UTC")
    return str(value)


def render():
    st.header("Tinjauan klaim")
    st.write("Pilih klaim, baca indikator, lalu simpan hasil pemeriksaan beserta catatan pendukung.")
    if st.session_state.pop("review_saved", False):
        st.success("Hasil pemeriksaan berhasil disimpan. Anda dapat melanjutkan ke klaim berikutnya.")
    st.caption("Skor prioritas 0–100, bukan probabilitas fraud. Menyimpan tinjauan tidak menahan pembayaran atau mengubah label pelatihan.")
    from core.access import mode
    storage_note = ("Data demo terpisah per sesi dan dapat kedaluwarsa." if mode() == "demo"
                    else "Keputusan tersimpan dalam ruang pengguna Anda." if mode() == "shared"
                    else "Keputusan tersimpan di komputer ini dan tetap ada setelah aplikasi ditutup.")
    st.caption(storage_note + " Kelola salinan tersimpan melalui Status Sistem.")
    registry = {row["id"]: row for row in batch_store.list_queues()}
    if not registry:
        st.info("Belum ada antrean. Mulai dengan data contoh atau unggah paket pada Data & Prediksi.")
        if st.button("Mulai dari Data & Prediksi", type="primary"):
            st.session_state.page = "data_prediction"
            st.rerun()
        return
    # Key doubles as the widget id so "send to review" from the lab selects the new batch.
    if st.session_state.get("batch_review") not in registry:
        st.session_state["batch_review"] = next(iter(registry))
    labels = {key: f"Batch {i} · {pd.to_datetime(row['created'], utc=True):%d/%m/%Y %H:%M} UTC"
              for i, (key, row) in enumerate(registry.items(), 1)}
    st.selectbox("Batch tersimpan", list(labels), key="batch_review", format_func=labels.get)
    queue = batch_store.load_queue(st.session_state["batch_review"])
    dates = pd.to_datetime(queue['claims'].submit_ts, utc=True)
    st.write(f"**{len(queue['claims'])} klaim · Pengajuan {dates.min():%d/%m/%Y}–{dates.max():%d/%m/%Y} (UTC)**")
    st.caption(f"Sumber: {queue['model'].get('source', 'Asal data belum tercatat')}")
    with st.expander("Rincian teknis batch"):
        st.caption(f"Model: {queue['model']['version']} · cutoff: {queue['model']['cutoff']} · "
                   f"{len(queue['decisions'])} keputusan tersimpan")
        st.code(queue['id'], language=None)
    data = export(queue)
    st.metric("Klaim dalam batch", len(data))
    counts = progress(queue)
    for column, (label, value) in zip(st.columns(3), counts.items()):
        column.metric(label, value)
    st.caption("Selesai mencakup Selesai ditinjau dan Penjelasan layanan wajar. Status lain tetap memerlukan pemeriksaan; menyimpan catatan saja tidak menyelesaikan klaim.")
    st.info("Langkah berikutnya: pilih klaim, cocokkan temuan dengan bukti, lalu simpan hasil tinjauan. Gunakan filter Belum ditinjau untuk memulai pekerjaan baru.")
    st.markdown('<nav aria-label="Pintasan tinjauan"><a href="#antrean-pemeriksaan" target="_self">Kembali ke antrean</a> · <a href="#detail-klaim" target="_self">Ke detail klaim</a> · <a href="#hasil-tinjauan" target="_self">Ke hasil tinjauan</a></nav>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1.4], gap="large")
    with left:
        st.subheader("Antrean pemeriksaan", anchor="antrean-pemeriksaan")
        status = st.selectbox("Filter status", ["Semua"] + list(STATUSES), key="review_status_filter")
        search = st.text_input("Cari ID klaim atau faskes", key="review_search")
        shown = data if status == "Semua" else data[data.review_status.eq(status)]
        if search.strip():
            query = search.strip()
            shown = shown[shown.claim_id.str.contains(query, case=False, regex=False) | shown.faskes_id.str.contains(query, case=False, regex=False)]
        shown = shown.assign(_work=shown.work_priority.map({"Dahulukan": 0, "Ikuti skor model": 1, "Tunda": 2})).sort_values(
            ["_work", "priority_score", "claim_id"], ascending=[True, False, True])
        table = shown[["claim_id", "priority_score", "work_priority", "faskes_id", "icd", "review_status"]].copy()
        table.insert(2, "persentil", percentile_rank(data.priority_score).round(1).loc[shown.index].to_numpy())
        claim_key = f"review_claim_{queue['id']}"
        pending = st.session_state.pop("review_next_claim", None)
        if pending in shown.claim_id.tolist():
            st.session_state[claim_key] = pending
        def select_row():
            rows = st.session_state[f"review_table_{queue['id']}"]["selection"]["rows"]
            if rows and rows[0] < len(shown):
                st.session_state[claim_key] = shown.iloc[rows[0]].claim_id
        st.dataframe(table, hide_index=True, width="stretch",
                     key=f"review_table_{queue['id']}", on_select=select_row,
                     selection_mode="single-row", column_config={
                         "claim_id": "ID klaim", "priority_score": st.column_config.NumberColumn("Skor prioritas /100", format="%.1f"),
                         "work_priority": "Prioritas kerja", "faskes_id": "Faskes",
                         "icd": "Diagnosis", "review_status": "Hasil tinjauan", "persentil": "Persentil"})
        st.caption("Klik satu baris untuk membuka klaim, atau gunakan pilihan klaim di panel detail.")
        st.caption(f"{data.priority_score.nunique()} nilai skor unik dari {len(data)} klaim; skor yang seri "
                   "mendapat persentil sama dan diurutkan stabil oleh claim_id, sehingga persentil bukan bukti "
                   "urutan kepastian di antara klaim seri.")
    with right:
        if not shown.empty:
            if st.session_state.get(claim_key) not in shown.claim_id.tolist():
                st.session_state[claim_key] = shown.iloc[0].claim_id
            cid = st.selectbox("Pilih klaim untuk diperiksa", shown.claim_id.tolist(),
                               key=f"review_claim_{queue['id']}")
            row = shown.set_index("claim_id").loc[cid]
            st.subheader(f"Detail pemeriksaan · {cid}", anchor="detail-klaim")
            st.markdown('[Ke hasil tinjauan](#hasil-tinjauan)')
            st.caption("Periksa temuan dan catatan pembanding sebelum menentukan hasil tinjauan.")
            st.metric("Skor prioritas", f"{row.priority_score:.1f} / 100")
            st.dataframe({"Informasi": ["Faskes", "Dokter", "Peserta", "Diagnosis", "Tarif", "Waktu layanan", "Waktu pengajuan"],
                          "Nilai": [format_value(k, row[k]) for k in ("faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_ts", "submit_ts")]}, hide_index=True)
            st.markdown("**Indikator untuk diperiksa**")
            for field in ("indicators", "temporal_indicators", "upcoding_indicators"):
                if field in row:
                    details = json.loads(row[field])
                    reasons = details.get("reasons", []) if isinstance(details, dict) else details
                    for reason in reasons:
                        st.write("• " + str(reason))
                    if not reasons and field == "indicators":
                        st.caption("Tidak ada indikator aturan yang menonjol. Skor model tetap perlu ditinjau bersama dokumen layanan.")
            prior = queue["decisions"].get(cid, {})
            if "comparison_evidence" in row:
                detail = json.loads(row["comparison_evidence"])
                with st.expander("Catatan sumber dan nilai indikator"):
                    st.caption(detail["scope"])
                    st.caption(detail["limitations"])
                    for label, group in detail["comparisons"].items():
                        st.write(f"**{label}** · {group['shown']} dari {group['total']} catatan")
                        st.dataframe(group["records"], hide_index=True)
                    if not detail["comparisons"]:
                        st.caption("Tidak ada catatan pembanding yang disertakan untuk klaim ini.")
                with st.expander("Rincian teknis · nilai fitur"):
                    st.json(detail["feature_values"])
            st.info("Yang perlu diverifikasi: cocokkan waktu, diagnosis, tarif, dan identitas layanan dengan dokumen sumber. Pola tidak biasa dapat memiliki penjelasan layanan yang sah.")
            from components.case_context import render as render_context
            render_context(queue, cid)
            st.subheader("Hasil tinjauan", anchor="hasil-tinjauan")
            st.markdown('[Kembali ke antrean](#antrean-pemeriksaan)')
            if prior:
                st.caption(f"Keputusan tersimpan: {prior['status']} oleh "
                           f"{prior.get('actor') or 'pemeriksa tidak tercatat'} pada {prior['timestamp'][:16]} UTC.")
            with st.form(f"decision_{queue['id']}_{cid}"):
                decision = st.selectbox("Hasil tinjauan", STATUSES, index=STATUSES.index(prior.get("status", STATUSES[0])))
                note = st.text_area("Catatan pemeriksa", value=prior.get("note", ""), max_chars=2000)
                actor = st.text_input("Nama pemeriksa", value=st.session_state.get("reviewer_name", prior.get("actor", "")), max_chars=120,
                                      help="Dicatat permanen di jejak audit agar keputusan dapat ditelusuri.")
                priority = st.selectbox("Prioritas kerja", PRIORITIES,
                                        index=PRIORITIES.index(prior.get("work_priority", PRIORITIES[0])))
                st.caption("Prioritas kerja mengubah urutan antrean, bukan skor model. Hasil tinjauan bukan label fraud otomatis.")
                ids = shown.claim_id.tolist()
                position = ids.index(cid)
                save = st.form_submit_button("Simpan tinjauan")
                advance = st.form_submit_button("Simpan & lanjut", type="primary",
                                               disabled=position == len(ids) - 1)
                if save or advance:
                    if not actor.strip():
                        st.error("Nama pemeriksa wajib diisi agar keputusan dapat ditelusuri.")
                    else:
                        try:
                            batch_store.save_decision(queue["id"], cid, decision, note, actor, priority)
                            st.session_state["reviewer_name"] = actor.strip()
                            if advance:
                                st.session_state["review_next_claim"] = ids[position + 1]
                            st.session_state["review_saved"] = True
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))
                        except sqlite3.Error:
                            st.error("Tinjauan belum tersimpan. Periksa isian dan ketersediaan penyimpanan, lalu coba lagi.")
            ids = shown.claim_id.tolist()
            position = ids.index(cid)
            def next_claim():
                st.session_state[f"review_claim_{queue['id']}"] = ids[position + 1]
            st.caption("Klaim berikutnya berpindah tanpa menyimpan. Gunakan Simpan & lanjut untuk menyimpan perubahan.")
            st.button("Klaim berikutnya", on_click=next_claim, disabled=position == len(ids) - 1)
        else:
            st.info("Tidak ada klaim sesuai filter. Ubah status atau kata pencarian.")
            def reset_filters():
                st.session_state["review_search"] = ""
                st.session_state["review_status_filter"] = "Semua"
            st.button("Reset filter", on_click=reset_filters)
    st.divider()
    st.subheader("5. Unduh hasil pemeriksaan")
    st.caption("CSV berisi antrean dan keputusan terbaru. Riwayat JSON mencatat perubahan tinjauan.")
    st.download_button("Unduh antrean dan hasil tinjauan", safe_csv(export(queue)).encode("utf-8-sig"),
                       file_name="jala-batch-review.csv", mime="text/csv")
    st.download_button("Unduh riwayat tinjauan", json.dumps(dict(batch_id=queue["id"], model=queue["model"],
                       events=queue["events"]), ensure_ascii=False, indent=2),
                       file_name="jala-review-history.json", mime="application/json")
