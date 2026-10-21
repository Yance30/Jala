# Audit kesiapan tahap lanjutan JALA — 20 Oktober 2026

> Hasil di bawah adalah snapshot historis. Lihat [audit kode](audit-kode-menyeluruh-2026-10-20.md)
> dan [tindak lanjut perbaikan](perbaikan-audit-2026-10-20.md) untuk keadaan lebih baru.

Konteks: tim sudah lolos tahap awal. Rubrik resmi tahap berikutnya dan tenggat belum diberikan. Rekomendasi berikut merupakan penilaian teknis terhadap checkout lokal, bukan prediksi peringkat lomba.

## Ruang lingkup

Pemeriksaan struktur aplikasi, jalur fitur dan evaluasi, prediksi batch, impor, penyimpanan, tinjauan, privasi, dokumentasi demo, CI, serta pengujian otomatis. Semua 96 berkas Python pada aplikasi, modul, skrip dan tes lolos parsing sintaks. Pembacaan mendalam difokuskan pada jalur kritis; ini bukan audit keamanan menyeluruh setiap baris atau verifikasi deployment publik. Banyak perubahan lokal sudah ada sebelum audit dan tidak ditimpa.

## Temuan menurut prioritas

### 1. Tinggi untuk deployment publik: antrean batch tidak terisolasi per pengguna

`core/batch_store.py:database_path` memakai satu `.jala/batch.sqlite3` secara default. `list_models`, `list_queues`, dan `save_decision` tidak mempunyai parameter pemilik maupun pemeriksaan izin. `views/batch_review.py` menampilkan seluruh antrean dari database tersebut, menerima nama pemeriksa sebagai teks, dan mengizinkan penyimpanan keputusan. `views/system_status.py` menampilkan jejak audit bersama.

Pada instance server bersama, pengguna lain dapat membuka antrean dan mengubah keputusan yang sama. Ini sesuai keterbatasan penyimpanan lokal satu pengguna yang tertulis pada modul, tetapi bukan isolasi sesi untuk demo publik. Data detail batch dan ekspor juga memuat `patient_id` langsung.

Tindakan: pilih mode demo publik dengan penyimpanan per sesi, atau implementasikan identitas pengguna dan pembatasan akses pada lapisan penyimpanan untuk mode bersama. Tambahkan pengujian dua sesi yang membuktikan pengguna B tidak bisa membaca atau mengubah antrean pengguna A.

### 2. Tinggi untuk kekuatan bukti: pisahkan evaluasi retrospektif dari prediksi baru

`components/bench.py:_engine` memakai `benchmark()` untuk mengisi dashboard. `core/evaluate.py:benchmark` membangun fitur seluruh dunia sebelum membagi fold classifier. Ini mendukung eksperimen retrospektif, bukan bukti prediksi prospektif saat klaim masuk.

`core/batch.py` sudah memiliki jalur train/predict terpisah, menolak label pada input fitur, serta memeriksa cutoff dan snapshot batch tertutup. Jadikan jalur ini demonstrasi prediksi utama. Jangan menyebut streaming atau real-time; seluruh batch uji tersedia saat penilaian.

### 3. Tinggi untuk penilaian ilmiah: hasil generalisasi harus dibahas per protokol

Artefak `docs/independent-evaluation.json` melaporkan rata-rata AUC 0,8242, precision@100 71,11%, recall@100 35,56%. Generator terpisah masih dibuat oleh tim yang sama; ini bukan validasi pakar independen.

Ada kemajuan lebih baru: pada protokol yang sama di `docs/model-comparison.json`, model original mempunyai AP 0,6679, sedangkan expanded_base 0,9140. Kandidat temporal mempunyai AP 0,9310 tetapi precision@100 sedikit lebih rendah daripada expanded_base (0,9917 vs 0,9933); `promotion_gate_passed` bernilai false.

Implikasi: perluasan skenario pelatihan layak diprioritaskan. Jangan mengganti model hanya karena AUC naik. Jangan membandingkan angka lintas artefak seolah memakai dataset, kapasitas dan split yang identik. Angka artefak ini dibaca dalam audit, bukan seluruhnya diregenerasi.

Tindakan: bekukan protokol pengujian sebelum iterasi berikutnya; laporkan precision/recall pada kapasitas yang sama, hasil per modus, biaya salah tinjau, variasi antar seed/cutoff, dan pengujian pola yang tidak masuk pelatihan.

### 4. Sedang: narasi demo belum konsisten dengan implementasi terbaru

- `DEMO.md` masih menyebut AUC 0,996, sedangkan README menjelaskan pembulatan benchmark 0,99659 menjadi 0,997.
- `DEMO.md` menyatakan riwayat klaster persisten secara default; `core/review_history.py` justru mematikannya kecuali `JALA_REVIEW_HISTORY_DB` diatur. Penyimpanan batch mempunyai default berbeda.
- Tabel triase aktif di `components/tables.py:triage_table_html` masih menampilkan skor dengan `%`, sementara layar lain menjelaskan skor prioritas 0–100 bukan probabilitas.
- README bagian navigasi belum mencakup seluruh sembilan route di `app.py`.
- Snapshot browser pengujian menampilkan KPI dugaan 295 / 252 / 102, sementara naskah demo masih 296 / 244 / 101. Ini ketidaksesuaian teramati; penyebab variasi perlu ditelusuri sebelum membekukan angka presentasi.

Tindakan: selaraskan naskah, layar, dan tabel metrik dengan sumber yang sama. Bedakan indikator aturan dari atribusi model, nilai klaim dari kerugian terbukti, serta keputusan simulasi dari aksi pembayaran.

### 5. Sedang: pembuktian manfaat pengguna belum tersedia

Alur bukti, konteks hubungan, tinjauan, dan audit sudah tersedia. Namun `DEMO.md` sendiri menyatakan belum ada uji waktu kerja verifikator.

Tindakan: uji tugas dengan beberapa calon pengguna yang relevan. Gunakan kasus sintetis yang sama dan acak urutan kondisi pemeriksaan biasa/JALA. Catat waktu menuju rekomendasi, ketepatan keputusan, kesalahan, dan alasan pengguna. Perlakukan hasil kecil sebagai temuan awal, bukan estimasi operasional nasional.

## Urutan pengerjaan yang disarankan

1. Perbaiki kegagalan tes yang terkonfirmasi, konsistensi demo, dan perilaku penyimpanan sesuai target deployment.
2. Pilih satu alur utama: paket data → validasi → prediksi model tetap → tinjau hubungan → catat keputusan → ekspor bukti.
3. Tampilkan dua kasus: dugaan terkoordinasi dan pola layanan sah yang memerlukan kehati-hatian. Keputusan manusia harus terlihat.
4. Perkuat evaluasi model dasar dengan skenario lebih beragam dan pengujian yang dibekukan; HAN/GNN hanya menjadi eksperimen bila ada hipotesis dan pembanding yang jelas.
5. Ukur manfaat penggunaan, lalu sesuaikan presentasi dengan rubrik resmi tahap lanjutan.

Ukuran selesai: demo dapat diulang, angka dapat ditelusuri, batas kemampuan jelas, pengujian relevan lulus, dan ada bukti awal bahwa pengguna terbantu.

## Validasi

- Parsing sintaks: 96 berkas Python valid.
- Pemeriksaan kedua dependency lock: lulus terhadap `requirements.txt`.
- `git diff --check`: lulus; terdapat peringatan normalisasi LF/CRLF.
- Tes terarah `tests/test_guide.py`: 4 lulus, 1 gagal. Regex penjaga angka metrik juga menangkap angka `100` dalam penjelasan skala skor. Ini ketidaksesuaian cakupan tes dengan teks panduan, bukan bukti mesin deteksi rusak.
- Suite non-E2E: **244 lulus, 1 gagal, 12 tidak dipilih**, selesai dalam 344,22 detik. Satu kegagalan adalah tes panduan di atas; tes render mencakup sembilan route.
- Suite browser: **11 lulus, 1 gagal, 245 tidak dipilih**, selesai dalam 302,54 detik. `test_tutorial_opens_navigates_and_reopens` mencari “Selamat datang di JALA”, sedangkan dialog yang benar-benar terbuka menampilkan “Welcome to JALA”. Ini ketidaksesuaian teks/locator; langkah lanjutan pada tes tersebut belum dijalankan karena assertion awal gagal. Snapshot juga memperlihatkan campuran bahasa Inggris/Indonesia pada navigasi dan panduan.

Audit ini menambahkan laporan saja; tidak mengubah logika aplikasi atau mengirim perubahan ke layanan eksternal.
