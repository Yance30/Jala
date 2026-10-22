"""Import and evaluate a complete external test package in the current session."""
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

from core import batch_store
from core.contract import MINIMAL
from core.data_quality import feature_readiness
from core.evaluate import percentile_rank
from core.import_data import MAX_FILE_BYTES, load, predict_saved, run_holdout
from core.review_queue import prepare


def example_files():
    from core.independent_scenarios import generate
    case = generate(31, n_routine=500)
    files = {f"{name}.csv": getattr(case, name)[columns].to_csv(index=False).encode()
             for name, columns in MINIMAL.items()}
    files["labels.csv"] = case.labels[["claim_id", "is_fraud"]].to_csv(index=False).encode()
    files["tariff_caps.json"] = json.dumps(
        {"I10": 250000, "E11.9": 300000, "N18.6": 1200000, "I50": 2400000}).encode()
    return files


@st.cache_data(show_spinner=False)
def example_zip():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in example_files().items():
            archive.writestr(name, content)
    return output.getvalue()


def _show_scores(data, scores, report, key, note):
    st.caption(note)
    if report["evaluation_available"]:
        with st.expander("Evaluasi model pada label paket uji"):
            st.dataframe(pd.DataFrame([dict(model=name, **report[name]) for name in ("jala", "rules")]),
                     hide_index=True, width="stretch")
        from core.batch import evaluate
        outcomes = data.labels[data.labels.claim_id.isin(scores.claim_id)]
        st.write("**Kualitas antrean menurut kapasitas pemeriksaan**")
        capacity_rows = []
        for capacity in (20, 50, 100):
            metrics = evaluate(scores, outcomes, capacity=capacity)
            capacity_rows.append(dict(kapasitas=metrics["capacity"],
                fraud_ditemukan=metrics["expected_fraud_at_k"],
                kasus_sah_diperiksa=metrics["expected_false_reviews"],
                fraud_terlewat=metrics["expected_fraud_missed"],
                precision=metrics["precision_at_k"], recall=metrics["recall_at_k"]))
        st.dataframe(capacity_rows, hide_index=True)
        st.caption("Nilai harapan untuk skor seri; berlaku pada label paket uji ini, bukan hasil verifikasi lapangan.")
    else:
        st.info("Prediksi tersedia. Metrik evaluasi tidak dihitung karena label batch uji belum lengkap.")
    top = scores.head(100).copy()
    top.insert(1, "persentil", percentile_rank(scores.priority_score).round(1).head(100).to_numpy())
    columns = [c for c in ("claim_id", "priority_score", "persentil") if c in top]
    st.write("**Pratinjau prioritas · maksimal 100 klaim**")
    st.dataframe(top[columns], hide_index=True, width="stretch", column_config={
        "claim_id": "ID klaim", "priority_score": st.column_config.NumberColumn("Skor prioritas /100", format="%.1f"),
        "persentil": "Persentil"})
    st.caption(f"{scores.priority_score.nunique()} nilai skor unik dari {len(scores)} klaim; skor seri mendapat "
               "persentil sama, jadi urutan di antara klaim seri ditentukan stabil oleh claim_id, bukan kepastian.")
    if st.button("Buka antrean tinjauan", key=f"{key}_to_review", type="primary"):
        queue = prepare(data.tables["claims"], scores, dict(report["model"], dataset_provenance=data.provenance,
                        source=st.session_state.get("dataset_origin", "Paket pengguna; asal belum diverifikasi")))
        st.session_state["batch_review"] = batch_store.save_queue(queue)["id"]
        st.session_state.page = "batch_review"
        st.rerun()
    st.caption("Membuka antrean menyimpan klaim dan konteks sumber ke ruang penyimpanan Anda. "
               "Kelola atau hapus melalui Penyimpanan dan penghapusan data.")
    st.download_button("Unduh laporan", json.dumps(report, ensure_ascii=False, indent=2),
                       file_name=f"jala-{key}-evaluation.json", mime="application/json", key=f"{key}_report")


def _saved_model_panel(data, capacity):
    st.divider()
    st.write("**Model tersimpan: prediksi batch baru tanpa pelatihan ulang**")
    registry = batch_store.list_models()
    if not registry:
        st.info("Belum ada model tersimpan. Pilih Latih model baru, jalankan pelatihan, lalu simpan model.")
        return
    labels = {row["id"]: f"{row['id'][:10]} · {row['metadata']['version']} · "
                         f"cutoff {row['metadata']['cutoff'][:10]} · {row['created'][:16]}" for row in registry}
    choice = st.selectbox("Model tersimpan", list(labels), format_func=labels.get, key="saved_model_choice",
                          on_change=lambda: st.session_state.pop("saved_result", None))
    if st.button("Prediksi paket aktif dengan model tersimpan", key="saved_predict"):
        st.session_state.pop("saved_result", None)
        try:
            with st.spinner("Memprediksi tanpa pelatihan ulang…"):
                st.session_state["saved_result"] = batch_store.predict_and_remember(data, choice, capacity=capacity)
        except (ValueError, TypeError, KeyError) as error:
            st.error(f"Prediksi gagal: {error}")
    result = st.session_state.get("saved_result")
    if result is not None:
        _, scores, report = result
        _show_scores(data, scores, report, "saved",
                     f"Model {report['model']['version']} · cutoff {report['model']['cutoff'][:10]} · "
                     f"{len(scores)} klaim · tanpa pelatihan ulang.")
    st.caption("Prediksi model tersimpan menyimpan observasi batch untuk konteks batch berikutnya. "
               "Skor dapat berubah bila pembagian batch berubah; bobot model tidak dilatih ulang.")


def render(expanded=False):
    with st.expander("Data batch · unggah, validasi, dan prediksi", expanded=expanded):
        st.subheader("1. Siapkan paket data")
        st.write("Mulai dengan Gunakan data contoh, atau unggah paket CSV dan JSON Anda. "
                 "Setelah validasi, pilih melatih model baru atau memakai model tersimpan.")
        st.caption("File: claims.csv, faskes.csv, affiliations.csv, patients.csv, tariff_caps.json. "
                   "Tambahkan labels.csv untuk pelatihan, dan mapping.json bila nama kolom berbeda. "
                   "Waktu tanpa zona dianggap UTC; gunakan offset eksplisit untuk waktu lokal.")
        st.download_button("Unduh paket contoh ZIP", example_zip(), file_name="jala-external-example.zip",
                           mime="application/zip", key="external_sample_zip")
        uploads = st.file_uploader("Unggah file CSV dan JSON setelah ZIP diekstrak (maksimal 5 MB/file)",
                                   type=["csv", "json"], accept_multiple_files=True, key="external_files")
        use_example = st.button("Gunakan data contoh", key="external_example")
        st.subheader("2. Validasi paket")
        validate = st.button("Validasi paket unggahan", key="external_validate", disabled=not uploads)
        if use_example or validate:
            st.session_state.pop("external_dataset", None)
            st.session_state.pop("external_result", None)
            st.session_state.pop("saved_result", None)
            try:
                if use_example:
                    files = example_files()
                else:
                    if len({f.name for f in uploads}) != len(uploads):
                        raise ValueError("Nama file unggahan duplikat.")
                    if any(f.size > MAX_FILE_BYTES for f in uploads):
                        raise ValueError("Setiap file dibatasi 5 MB.")
                    files = {f.name: f.getvalue() for f in uploads}
                st.session_state["external_dataset"] = load(files)
                st.session_state["dataset_origin"] = ("Contoh sintetis bawaan" if use_example
                                                       else "Paket pengguna; asal belum diverifikasi")
            except (ValueError, TypeError, KeyError, UnicodeError) as error:
                st.error(f"Paket diblokir: {error}")
                st.info("Perbaiki berkas sesuai pesan di atas, unggah kembali, lalu pilih Validasi paket unggahan. Gunakan paket contoh untuk melihat struktur yang diterima.")
        data = st.session_state.get("external_dataset")
        if data is None:
            return
        st.success(f"Paket aktif lolos validasi struktur: {len(data.tables['claims'])} klaim. "
                   "Paket berada di sesi; model/antrean/observasi yang disimpan memiliki salinan persisten.")
        claims = data.tables["claims"]
        st.caption(f"Paket aktif: {data.provenance['files_sha256']['claims.csv'][:12]} · "
                   f"Pengajuan {claims.submit_ts.min():%d %b %Y} – {claims.submit_ts.max():%d %b %Y} (UTC)")
        with st.expander("Kecocokan struktur data dengan fitur JALA"):
            st.dataframe(pd.DataFrame(feature_readiness(claims, tariff_caps=data.tariff_caps)),
                         hide_index=True, width="stretch")
            st.caption("Ini pemeriksaan struktur kolom dan bentuk nilai waktu, bukan verifikasi arti variabel, "
                       "identitas entitas, atau kebenaran hubungan di sumber. Pastikan pemetaan kolom dan "
                       "ketelitian waktu cocok dengan kamus data sebelum menafsirkan indikator.")
        st.subheader("3. Jalankan prediksi")
        purpose = st.radio("Apa yang ingin Anda lakukan?",
                           ["Latih model baru", "Gunakan model tersimpan"], key="prediction_purpose")
        if purpose == "Gunakan model tersimpan":
            st.caption("Nilai batch baru memakai model yang sudah disimpan, tanpa melatih ulang.")
            capacity = st.number_input("Kapasitas pemeriksaan", min_value=1, max_value=2000,
                                       value=100, key="saved_capacity")
            _saved_model_panel(data, int(capacity))
            return
        st.caption("Model baru belajar dari klaim historis berlabel, lalu menilai klaim setelah batas waktu.")
        st.write("Model utama menggunakan fitur graf + gradient boosting. "
                 "Batas waktu memisahkan data pelatihan dari klaim yang akan diprediksi.")
        signature = data.provenance["files_sha256"]["claims.csv"][:12]
        default_cutoff = data.tables["claims"].submit_ts.median().isoformat()
        st.caption("Batas pelatihan: klaim sebelum waktu ini dipakai untuk belajar; klaim setelahnya dinilai. Untuk mulai, gunakan nilai yang sudah terisi.")
        cutoff = st.text_input("Cutoff pelatihan (UTC)", default_cutoff, key=f"external_cutoff_{signature}")
        capacity = st.number_input("Kapasitas pemeriksaan batch eksternal", min_value=1, max_value=2000,
                                   value=100, key="external_capacity")
        with st.expander("Pengaturan lanjutan · kandidat model"):
            mode = st.selectbox("Model eksperimen", ["base", "temporal", "upcoding"], key="external_feature_set",
                                format_func=lambda x: {"base": "Baseline graf + GBM (utama)",
                                                       "temporal": "Kandidat temporal",
                                                       "upcoding": "Kandidat upcoding"}[x])
        if st.button("Latih historis dan prediksi periode berikutnya", key="external_run", type="primary"):
            st.session_state.pop("external_result", None)
            try:
                with st.spinner("Melatih dan menilai batch uji…"):
                    st.session_state["external_result"] = run_holdout(data, cutoff=cutoff, capacity=int(capacity), feature_set=mode)
            except (ValueError, TypeError, KeyError) as error:
                st.error(f"Eksperimen belum dapat dijalankan: {error}")
        result = st.session_state.get("external_result")
        if result is not None:
            st.subheader("4. Buka tinjauan klaim")
            model, scores, report = result
            _show_scores(data, scores, report, "external",
                         f"Hasil terakhir: cutoff {report['model']['cutoff']}; {len(scores)} klaim uji. "
                         "Jalankan ulang untuk menerapkan parameter baru.")
            if st.button("Simpan model terlatih ke basis data lokal", key="external_save_model"):
                try:
                    st.success(f"Model tersimpan ({batch_store.save_model(model)[:12]}). "
                               "Tersedia untuk batch baru tanpa pelatihan ulang.")
                except ValueError as error:
                    st.error(str(error))
            st.caption("Simpan model mencakup riwayat klaim pelatihan dan tabel referensi, bukan parameter saja.")
            st.caption("Hasil berlaku pada paket uji ini; belum merupakan validasi operasional BPJS. "
                       "Referensi dianggap statis dan label historis dianggap tersedia pada cutoff.")


def render_independent_report():
    with st.expander("Uji ketahanan pada skenario independen"):
        path = Path(__file__).resolve().parents[1] / "docs" / "independent-evaluation.json"
        st.write("Model dilatih pada generator lama, lalu diuji tanpa pelatihan ulang pada pembangkit terpisah "
                 "dengan entitas baru, klaim berulang tertunda, rujukan satu arah, dan kasus sah yang sulit.")
        if not path.exists():
            st.caption("Jalankan python -m core.external_evaluation untuk membuat laporan.")
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        rows = [dict(seed=run["seed"], model=name, **run[name]) for run in report["runs"] for name in ("jala", "rules")]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Artefak evaluasi tersimpan; pembangkit terpisah tetap dibuat oleh tim yang sama. "
                   "Ini bukan validasi pakar independen atau hasil pada data operasional.")
        st.download_button("Unduh hasil skenario independen", json.dumps(report, indent=2),
                           file_name="jala-independent-evaluation.json", mime="application/json", key="independent_report")


def render_model_comparison():
    with st.expander("Perbandingan kandidat ML pada beberapa cutoff"):
        st.write("Bandingkan baseline, tambahan data pengembangan, dan tambahan fitur temporal pada holdout yang sama. "
                 "Model utama tetap graf + gradient boosting.")
        path = Path(__file__).resolve().parents[1] / "docs" / "model-comparison.json"
        if not path.exists():
            st.caption("Jalankan python -m core.model_comparison untuk menghasilkan laporan eksperimen.")
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame([dict(model=k, **v) for k, v in report["summary"].items()]),
                     hide_index=True, width="stretch")
        if report["promotion_gate_passed"]:
            st.success("Kandidat lolos gerbang eksperimen. Default tidak diganti otomatis.")
        else:
            st.info("Kandidat belum lolos seluruh gerbang eksperimen; baseline tetap menjadi default.")
        st.caption("Precision dan recall menggunakan 100 klaim teratas; false_reviews_at_300 menghitung klaim sah "
                   "dalam 300 teratas. Rata-rata dari tiga cutoff dan dua seed holdout; "
                   "template skenario pengembangan dan uji masih sama. "
                   "Belum validasi pakar atau bukti kinerja lapangan.")
        st.download_button("Unduh perbandingan model", json.dumps(report, indent=2),
                           file_name="jala-model-comparison.json", mime="application/json", key="model_comparison_report")


def render_upcoding_report():
    with st.expander("Uji kandidat upcoding: baseline vs fitur komposisi diagnosis"):
        path = Path(__file__).resolve().parents[1] / "docs" / "upcoding-evaluation.json"
        st.write("Baseline tidak punya sinyal untuk upcoding yang tariff-nya masih di bawah plafon. "
                 "Kandidat menambah dua fitur: simpangan komposisi diagnosis faskes terhadap faskes sejenis, "
                 "dan lonjakan tarif terhadap riwayat peserta itu sendiri.")
        if not path.exists():
            st.info("Laporan belum tersedia; jalankan python -m core.upcoding_evaluation.")
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        rows = [dict(seed=run["seed"], feature_set=run["feature_set"], keluarga=f["family"],
                     jenis="fraud" if f["labelled"] else "sah", n=f["n"],
                     **{f"recall@{k}": v for k, v in f["recall"].items()})
                for run in report["runs"] for f in run["families"]]
        st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.dataframe(pd.DataFrame([dict(seed=run["seed"], feature_set=run["feature_set"],
                                        **{k: v for k, v in run["metrics"]["300"].items()
                                           if k in ("auc", "average_precision", "precision_at_k", "recall_at_k")})
                                   for run in report["runs"]]), hide_index=True)
        st.caption("Keluarga upcoding dan kedua fitur kandidatnya dirancang oleh tim yang sama, jadi ini "
                   "menunjukkan lubang yang diketahui berhasil ditutup, bukan bukti generalisasi pada upcoding nyata. "
                   "Baris berjenis 'sah' adalah biaya tinjauan keliru, bukan deteksi. Data sintetis, "
                   "bukan validasi operasional BPJS atau kajian klinis.")
        st.download_button("Unduh hasil kandidat upcoding", json.dumps(report, indent=2),
                           file_name="jala-upcoding-evaluation.json", mime="application/json")


def render_unseen_report():
    with st.expander("Uji keluarga fraud yang tidak dilatih"):
        path = Path(__file__).resolve().parents[1] / "docs" / "unseen-evaluation.json"
        if not path.exists():
            st.info("Laporan belum tersedia; jalankan python -m core.unseen_evaluation.")
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        rows = []
        for run in report["runs"]:
            for family in run["families"]:
                rows.append(dict(dikeluarkan_dari_latih=run["excluded_family"] or "Tidak ada (kontrol)",
                                 seed=run["seed"], keluarga=family["family"],
                                 recall_at_100=family["recall"]["100"], recall_at_300=family["recall"]["300"]))
        st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.caption("Klaim keluarga yang diuji dikeluarkan sebelum fitur graf dihitung. "
                   "Pelatihan hanya menggunakan generator skenario terpisah; angka tidak langsung sebanding "
                   "dengan benchmark lama. Skenario sintetis, bukan validasi operasional.")
        st.download_button("Unduh uji keluarga yang tidak dilatih", json.dumps(report, indent=2),
                           file_name="jala-unseen-evaluation.json", mime="application/json")
