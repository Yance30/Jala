# Dataset uji eksternal dan skenario independen

## Mencoba melalui aplikasi

Buka **Data & Prediksi**.

1. Tekan **Gunakan data contoh** untuk mencoba tanpa menyiapkan file; atau unduh ZIP contoh, ekstrak, lalu unggah file CSV/JSON-nya bersama-sama.
2. Tekan **Validasi paket unggahan**. Dataset tidak valid diblokir seluruhnya; tidak ada klaim yang dibuang atau diperbaiki diam-diam. Pesan kegagalan menyebut jenis masalah dan jumlah record, bukan contoh identitas peserta.
3. Pilih cutoff dan kapasitas, lalu tekan **Latih historis dan prediksi periode berikutnya**.
4. Unduh laporan JSON. Label data uji tidak dibutuhkan untuk prediksi. Bila label uji tidak lengkap, metrik evaluasi tidak diterbitkan.

Fitur ini menerima **dataset sintetis/uji dengan referensi sendiri**, bukan koneksi ke BPJS. Contoh bawaan dibangun oleh `core/independent_scenarios.py`, tanpa memanggil generator lama. Model awal berada dalam sesi; tombol simpan model menyimpan estimator **beserta riwayat klaim dan referensi**. Membuka antrean juga menyimpan salinan data. Lihat [mode, retensi dan penghapusan](deployment-and-data.md).

Prediksi dengan model tersimpan menyertakan observasi dari batch sebelumnya tanpa melatih ulang bobot model. Batch yang lebih lama dari snapshot terakhir atau mengubah klaim lama ditolak; gunakan model/snapshot terpisah untuk koreksi dan replay. Data hanya tanggal ditolak sebagai **belum cukup untuk dinilai**, bukan diberi skor rendah. Model batch v3 menggantikan v2; model lama harus dilatih ulang.

Untuk demo yang dapat diulang dan uji dengan calon pemeriksa, lihat [paket dan protokol](review-pilot.md). Panel hasil menampilkan kualitas antrean pada kapasitas 20/50/100; hasil tinjauan manusia tetap terpisah dari label evaluasi.

## Kontrak paket

Setiap file maksimal 5 MB, UTF-8; CSV memakai koma sebagai separator. Nama file harus tepat. ID dibaca sebagai teks sehingga nol di depan tidak hilang. Nilai numerik memakai titik desimal dan tanpa pemisah ribuan.

| File | Kolom wajib |
|---|---|
| claims.csv | claim_id, faskes_id, doctor_id, patient_id, icd, tarif, visit_ts, submit_ts, referral_from_faskes, referral_from_doctor |
| faskes.csv | faskes_id, type, region, capacity |
| affiliations.csv | doctor_id, faskes_id |
| patients.csv | patient_id, home_region |
| labels.csv (opsional saat validasi; diperlukan untuk pelatihan) | claim_id, is_fraud |
| tariff_caps.json | Objek kode diagnosis → referensi tarif positif |
| mapping.json (opsional) | Objek tabel → pemetaan nama kolom sumber ke nama kontrak |

Kolom harus tepat sesuai kontrak setelah mapping. Kolom tambahan ditolak agar atribut yang tidak didukung tidak diabaikan diam-diam. Referensi rujukan boleh kosong; kunci dan atribut wajib tidak boleh kosong. Label harus berupa 0/1, unik, dan terkait claim_id dalam paket. Kolom label dilarang masuk ke tabel observasi, termasuk sebelum pemetaan nama.

Gunakan waktu ISO 8601. Contoh: `2026-09-01T07:00:00+07:00` dinormalisasi menjadi `2026-09-01T00:00:00` UTC. Waktu tanpa offset **dianggap UTC**; tanggal seperti `01/09/2026` tidak diterima karena ambigu. Cutoff mengikuti UTC. Adapter tidak menebak zona waktu sumber.

Contoh `tariff_caps.json` (nilai uji, **bukan tarif resmi**):

```json
{"I10": 250000, "E11.9": 300000, "N18.6": 1200000}
```

Referensi tarif wajib mencakup semua diagnosis. Referensi dipakai oleh fitur rasio tarif dan baseline aturan, disalin ke model, serta memiliki fingerprint dalam metadata. Kode diagnosis baru dapat digunakan bila pemetaannya disediakan sebelum pelatihan; tidak ada fallback diam-diam ke tarif sintetis bawaan.

Contoh `mapping.json`:

```json
{
  "claims": {"nomor_klaim": "claim_id", "nilai_klaim": "tarif"},
  "patients": {"kode_peserta": "patient_id"}
}
```

Pemetaan hanya mengubah nama kolom, bukan arti atau satuan. Kolom yang tidak disebut tetap memakai nama kontrak. Mapping yang menghasilkan nama duplikat ditolak.

## CLI dan API

Dengan paket di folder `.jala/example-external`:

```powershell
.\.venv\Scripts\python.exe -m core.import_data --input .jala/example-external --cutoff 2026-09-30 --capacity 100 --json docs/external-example-evaluation.json
.\.venv\Scripts\python.exe -m core.external_evaluation --json docs/independent-evaluation.json
```

API `load({filename: bytes})` memvalidasi paket dan menghasilkan `Dataset`; `run_holdout(dataset, cutoff=..., capacity=...)` menghasilkan model, prediksi dan laporan. Seluruh klaim historis memerlukan label; label uji boleh tidak ada. Laporan mencatat hash file sumber, jumlah record, versi adapter, cutoff, versi model, dan fingerprint tarif.

`batch.predict(model, claims, as_of=..., references=...)` juga menerima referensi tambahan untuk entitas baru. `references` harus memuat faskes, affiliations, patients. Record referensi yang sama boleh diulang, tetapi perubahan atribut ID yang sudah ada ditolak. Model dan snapshot latih tidak diubah. Perubahan referensi historis memerlukan eksperimen/pelatihan terpisah; belum ada referensi dengan masa berlaku.

## Evaluasi tanpa pelatihan ulang pada skenario terpisah

`core.external_evaluation` melatih satu GBM pada 11.465 klaim historis dari generator lama dengan kronologi v2, kemudian menilai skenario seed **31, 47, 59**. Seluruh entitas skenario baru; kode pembangkit tidak mengimpor `core.synthetic`, fitur detektor, atau label training. Algoritma deteksi tidak dituning menggunakan hasil uji ini.

Setiap skenario berisi 2.955 klaim, termasuk 200 fraud sintetis. Kapasitas 100 klaim, dengan expected hits bila skor seri. Rata-rata hasil tersimpan:

| Metrik JALA | Hasil |
|---|---:|
| ROC-AUC | 0,8242 |
| Average precision | 0,6130 |
| Precision@100 | 71,11% |
| Recall@100 | 35,56% |

Pada seed 31, 73 dari 80 phantom masuk top-100; tidak ada repeat tertunda maupun self-referral satu arah dalam top-100. Sisanya 27 klaim rutin sah. Ini menunjukkan titik lemah penting yang tertutup oleh angka hampir sempurna pada generator lama. Detail per-seed dan per-skenario ada di `docs/independent-evaluation.json` dan panel About **Uji ketahanan pada skenario independen**.

Angka bukan perbandingan apples-to-apples dengan holdout sebelumnya: ukuran batch, prevalensi, pola, entitas dan kapasitas berbeda. Jangan mengklaim kenaikan atau penurunan kausal dari satu perubahan tertentu. Pembangkit terpisah tetap disusun oleh proyek yang sama; ini belum validasi pakar eksternal atau data lapangan. Kedua jalur memakai batch lengkap saat ditutup, tabel referensi statis, dan asumsi label historis tersedia pada cutoff.

Tindak lanjut: bangun skenario pengembangan terpisah untuk memperbaiki klaim ulang tertunda dan rujukan satu arah; bekukan skenario evaluasi ini. Pengujian lanjutan harus memakai holdout baru setelah pemilihan fitur/model agar hasilnya tidak optimistis karena tuning pada data uji.

## Validasi implementasi

Suite non-browser menghasilkan **203 passed, 10 deselected** (286,51 detik). Cakupan tambahan meliputi paket dengan mapping dan diagnosis/tarif baru, ID berawalan nol, konversi offset waktu, CSV rusak, label uji opsional, konflik referensi, serta interaksi Streamlit AppTest. Pemeriksaan tambahan model versi lama dan header CSV rusak juga lolos. Browser E2E tidak dijalankan.

CLI impor dijalankan pada paket contoh: 507 klaim historis digunakan untuk pelatihan, 448 klaim berikutnya diprediksi. Hasilnya ada di `docs/external-example-evaluation.json`. Eksperimen transfer tiga seed dijalankan terpisah untuk membuat `docs/independent-evaluation.json`. Seluruh perubahan tetap lokal dan belum di-commit/push.
