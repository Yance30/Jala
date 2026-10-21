"""Small lab for temporal training and prediction of new synthetic claim batches."""
import io
import json
from dataclasses import replace

import pandas as pd
import streamlit as st

from core import batch
from core.contract import MINIMAL
from core.synthetic import DEFAULT, generate_world


def render():
    with st.expander("Eksperimen prediksi batch baru"):
        st.write("Latih model pada periode awal, lalu uji klaim setelah batas waktu pelatihan. "
                 "Eksperimen ini memakai data sintetis versi kronologi v2 dan terpisah dari benchmark utama.")
        days = st.slider("Jumlah hari untuk data latih", 30, 80, 60, key="batch_training_days")
        capacity = st.number_input("Kapasitas pemeriksaan klaim", 1, 2000, 500, key="batch_capacity")
        if st.button("Latih dan evaluasi batch sintetis", key="batch_run"):
            with st.spinner("Melatih model historis dan memprediksi batch berikutnya…"):
                try:
                    model, scores, report = batch.demo(training_days=days, capacity=int(capacity))
                    st.session_state["batch_experiment"] = (model, scores, report)
                except ValueError as error:
                    st.error(str(error))
        stored = st.session_state.get("batch_experiment")
        if stored is None:
            return
        model, scores, report = stored
        st.caption(f"Hasil terakhir: cutoff {model.metadata['cutoff']}; "
                   f"kapasitas {report['jala']['capacity']}. Jalankan ulang untuk menerapkan pilihan baru.")
        st.dataframe(pd.DataFrame([dict(model=name, **report[name]) for name in ("jala", "rules")]),
                     hide_index=True, width="stretch")
        st.caption("Recall/precision di atas berlaku pada batch uji setelah cutoff, bukan seluruh dataset. "
                   "Seluruh batch terlihat saat ditutup; hasil ini bukan pengujian real-time atau data BPJS.")
        st.download_button("Unduh evaluasi batch", json.dumps(report, ensure_ascii=False, indent=2),
                           file_name="jala-batch-evaluation.json", mime="application/json", key="batch_report")
        st.dataframe(scores.head(50), hide_index=True, width="stretch")
        st.write("Coba batch CSV sintetis baru menggunakan ID faskes, dokter, dan peserta dari eksperimen ini. "
                 "Label fraud tidak diperlukan dan tidak boleh dimasukkan. Skor 0–100 adalah prioritas tinjauan.")
        sample = generate_world(model.metadata["seed"], cfg=replace(
            DEFAULT, chronological_submissions=True)).claims
        sample = sample[sample.submit_ts > pd.Timestamp(model.metadata["cutoff"])].head(50)
        st.download_button("Unduh contoh batch CSV", sample.to_csv(index=False),
                           file_name="jala-batch-synthetic.csv", mime="text/csv", key="batch_sample")
        upload = st.file_uploader("Batch klaim sintetis (CSV, maksimal 5 MB)", type=["csv"], key="batch_upload")
        if upload is not None and st.button("Prediksi batch CSV", key="batch_predict"):
            if upload.size > 5_000_000:
                st.error("Ukuran batch melebihi 5 MB.")
                return
            try:
                data = pd.read_csv(io.BytesIO(upload.getvalue()), dtype={
                    name: "string" for name in MINIMAL["claims"] if name not in ("tarif", "visit_ts", "submit_ts")})
                for column in ("visit_ts", "submit_ts"):
                    data[column] = pd.to_datetime(data[column], errors="raise")
                prediction = batch.predict(model, data, as_of=data.submit_ts.max())
                st.dataframe(prediction, hide_index=True, width="stretch")
                st.success(f"{len(prediction)} klaim diprediksi menggunakan model yang sudah dilatih, tanpa pelatihan ulang.")
            except (ValueError, KeyError, TypeError, pd.errors.ParserError) as error:
                st.error(f"Batch belum dapat diproses: {error}")
