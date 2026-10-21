# Audit kode dan berkas JALA — 20 Oktober 2026

> Catatan historis sebelum perbaikan. Status tindak lanjut ada di
> [laporan perbaikan](perbaikan-audit-2026-10-20.md). Skrip reproduksi kini juga memeriksa perilaku yang telah diperbaiki.

## Kesimpulan

JALA memiliki fondasi prototipe yang nyata: fitur relasional, model terpisah dari label saat prediksi, impor ketat, evaluasi, konteks kasus, dan tinjauan manusia. Kekurangan terbesar ada pada kebenaran beberapa kasus tepi, pengelolaan data persisten, kesiapan penggunaan bersama, dan pembuktian generalisasi. Hasil sintetis belum membuktikan akurasi atau manfaat operasional.

Audit ini tidak mengganti model atau mengubah logika aplikasi. Perubahan audit hanya laporan ini dan `scripts/audit_edge_cases.py`. Banyak perubahan aplikasi sudah ada sebelum audit.

## Cakupan dan batas pemeriksaan

- Inventaris awal: 145 berkas proyek sebelum dua berkas audit ditambahkan; 96 Python, 18 Markdown, 10 JSON/JSONC, 9 PNG, serta konfigurasi, lock, dan skrip.
- Seluruh berkas proyek yang terdaftar Git atau belum dilacak dan tidak diabaikan diinventarisasi. Python diparsing melalui AST; JSON biasa diperiksa parsing. `devcontainer.json` memakai JSONC dengan komentar, sehingga tidak diperlakukan sebagai JSON biasa.
- Pembacaan mendalam difokuskan pada `core/`, jalur impor/prediksi, penyimpanan/tinjauan, penghubung UI, evaluasi, tes, dan konfigurasi deployment. CSS, aset, dan seluruh dokumen masuk peninjauan struktur/konsistensi; sembilan PNG tidak diaudit secara visual satu per satu.
- `.git`, virtual environment, cache, basis data lokal dan file sementara bukan sumber aplikasi; tidak dilakukan pembacaan isi data pengguna atau rahasia. Peringatan izin pada konfigurasi ignore global Git tidak menghalangi pembacaan proyek.
- Ini tinjauan kode lokal dan pengujian, bukan pentest deployment publik, audit dependensi CVE, penilaian klinis, atau audit regulasi. Tidak semua eksperimen metrik diregenerasi.

## Temuan yang perlu ditindaklanjuti

### 1. Tinggi bila dipakai bersama: model dan antrean tidak dibatasi per pengguna

**Lokasi:** `core/batch_store.py:23`, `:74`, `:123`, `:134`; `views/batch_review.py`; `views/system_status.py`.

Default database adalah `.jala/batch.sqlite3`. Daftar model, antrean, dan penyimpanan keputusan tidak memiliki pemilik, identitas terautentikasi, atau pemeriksaan izin. Nama pemeriksa adalah input teks. Semua sesi yang memakai database itu berbagi akses.

**Dampak:** pada satu instance bersama, orang lain dapat membaca antrean atau mencatat keputusan pada batch yang sama. Pilihan peran di sidebar hanya pratinjau tampilan dan tidak menyelesaikannya. Ini merupakan keterbatasan yang sudah diakui kode, tetapi tetap menjadi penghalang penggunaan bersama.

**Perbaikan:** tetapkan mode lokal satu pengguna secara eksplisit. Sebelum penggunaan bersama, implementasikan identitas, kepemilikan batch/model, pemeriksaan izin di lapisan penyimpanan, dan tes dua pengguna. Mode demo publik juga perlu data per sesi atau database contoh yang tidak dapat diubah.

### 2. Tinggi untuk siklus hidup data: menyimpan model juga menyimpan riwayat klaim

**Lokasi:** `core/batch.py:46`, `:111`; `core/batch_store.py:66`; `components/external_lab.py:52`, `:154`; `components/bench.py:175`.

`BatchModel` memuat `history`, `patients`, `faskes`, dan `affiliations`, bukan estimator saja. `save_model` melakukan pickle atas seluruh objek. Tombol “Buka antrean tinjauan” juga langsung menyimpan klaim ke SQLite. Reset demo tidak menghapus dataset unggahan, model, atau antrean batch; tidak ada API/UI penghapusan batch/model maupun kebijakan retensi.

**Dampak:** menutup halaman atau mengatur ulang demo bukan penghapusan data. Pengguna dapat salah memahami tombol simpan model sebagai penyimpanan parameter model saja.

**Perbaikan:** jelaskan persis apa yang disimpan sebelum aksi; bedakan bersihkan sesi, hapus antrean, hapus model beserta riwayat, dan reset demo. Tetapkan retensi, lokasi backup, dan prosedur penghapusan. Jangan menjanjikan penghapusan fisik hanya dengan menghapus satu baris SQLite.

### 3. Sedang — bug terbukti: tarif nol lolos validasi tetapi menghasilkan fitur NaN

**Lokasi:** `core/data_quality.py:62`; `core/detect.py:142–147`; `core/batch.py:_features`.

Validasi menerima `tarif >= 0`. Dua kunjungan peserta/diagnosis sama dengan tarif nol memicu pembagian `0 / 0` pada `f_tarif_match_prev`. Data lolos pemeriksaan struktur, tetapi batch kemudian ditolak karena fitur tidak terbatas.

**Reproduksi:** `scripts/audit_edge_cases.py` menghasilkan `ZERO_TARIFF_VALIDATION True`, kemudian `ZERO_TARIFF_FEATURE_ERROR`.

**Perbaikan:** sepakati semantik tarif nol. Jika valid, hitung kesamaan tarif dengan penyebut aman dan definisikan kasus nol–nol. Jika tidak valid, tolak pada validasi dengan pesan spesifik. Tambahkan uji nol–nol, nol–positif, dan positif–nol.

### 4. Sedang — bug terbukti: urutan baris mengubah fitur pada timestamp sama

**Lokasi:** `core/detect.py:127–155`.

Pengurutan klaim berulang hanya memakai peserta, diagnosis, dan waktu layanan. Tidak ada aturan eksplisit untuk klaim dengan waktu sama. Pada dua klaim lintas faskes dengan timestamp identik, membalik urutan input menukar klaim yang menerima `f_dup_cross=1` dan gap nol.

**Dampak:** indikator per klaim berubah walaupun isi dataset sama; skor model berpotensi berubah. Audit ini membuktikan perubahan fitur, bukan mengukur perubahan skor pada seluruh model.

**Perbaikan:** definisikan semantik klaim simultan. Gunakan aturan agregasi simultan atau aturan tie yang terdokumentasi; sekadar menambah ID sebagai urutan akan membuat hasil deterministik tetapi belum membuat makna “sebelumnya” benar. Uji invariansi terhadap pengacakan baris.

### 5. Sedang — bug terbukti: persentase pada penjelasan upcoding salah penyebut

**Lokasi:** `core/upcoding_features.py:37`, `:53`.

Fitur menghitung `(tarif sekarang - median sebelumnya) / tarif sekarang`, tetapi teks menyebut persentase kenaikan terhadap median sebelumnya.

**Reproduksi:** tarif 100 menjadi 300 sebenarnya naik 200%; indikator menampilkan “Tarif 67% di atas median …”.

**Perbaikan:** pertahankan fitur yang telah dilatih bila diperlukan, tetapi gunakan besaran yang benar untuk teks, atau jelaskan normalisasinya secara tepat. Jika rumus fitur diubah, naikkan versi fitur/model dan ulangi evaluasi. Dampak langsung terbatas pada kandidat upcoding, bukan baseline default.

### 6. Sedang — ekspor CSV mempertahankan input sebagai rumus spreadsheet

**Lokasi:** `core/review_queue.py:39–44`; `views/batch_review.py:101`; juga audit ekspor CSV lain yang memuat catatan bebas.

Catatan pemeriksa dan ID dari unggahan diteruskan ke CSV tanpa perlakuan khusus untuk nilai berawalan formula. Reproduksi dengan catatan benign `=1+1` menunjukkan nilainya tetap utuh dalam hasil ekspor.

**Dampak:** bila CSV dibuka oleh spreadsheet yang menafsirkan nilai tersebut sebagai formula, input teks dapat dievaluasi sebagai formula. Tidak ada eksploit eksternal yang dijalankan dalam audit.

**Perbaikan:** sediakan ekspor spreadsheet yang menulis sel teks secara eksplisit atau netralisasi karakter awal berbahaya pada ekspor CSV. Jangan mengubah ID/data sumber di penyimpanan. Uji catatan, nama pemeriksa, dan ID.

### 7. Sedang/tinggi sesuai deployment: devcontainer mematikan proteksi dan tidak mengikuti lock

**Lokasi:** `.devcontainer/devcontainer.json`; `Dockerfile`; `.github/workflows/ci.yml`; `run_demo.bat`.

Devcontainer memakai Python 3.11, memasang `requirements.txt` dengan rentang versi, kemudian menjalankan Streamlit dengan `--server.enableCORS false --server.enableXsrfProtection false`. CI/Docker memakai Python 3.12 dan lock. Script Windows hanya memasang dependensi saat executable Streamlit belum ada; perubahan lock pada environment lama tidak otomatis diselaraskan.

**Dampak:** hasil environment pengembangan dapat berbeda dari lingkungan teruji; proteksi yang dimatikan ikut terbawa bila port devcontainer dibagikan. Tidak dibuktikan ada deployment publik yang saat ini menggunakan konfigurasi tersebut.

**Perbaikan:** samakan Python dan lock; hidupkan kembali proteksi default kecuali ada alasan teruji yang spesifik. Tambahkan pemeriksaan environment saat menjalankan demo. Docker juga belum menetapkan user non-root; hardening ini relevan sebelum hosting bersama.

### 8. Tinggi untuk kekuatan klaim model: benchmark utama bersifat retrospektif

**Lokasi:** `core/evaluate.py:117–125`; `components/bench.py:_engine`; `core/batch.py`; `docs/independent-evaluation.json`; `docs/model-comparison.json`.

Benchmark menghitung fitur seluruh dunia sebelum membagi fold classifier. Isolasi fold pada classifier tidak menghilangkan informasi struktur/agregat dari keseluruhan snapshot. Ini evaluasi retrospektif/transduktif, bukan bukti prediksi klaim yang baru masuk.

Jalur batch sudah memisahkan latih/prediksi, menolak label pada input fitur, serta membatasi cutoff. Itu fondasi yang baik, tetapi masih menggunakan seluruh batch saat ditutup. Generator dan fitur tetap dikembangkan tim yang sama.

Artefak skenario terpisah melaporkan AUC rata-rata sekitar 0,8242 dan recall@100 sekitar 35,56%. Jangan menyamakannya langsung dengan AUC benchmark 0,997 karena protokol berbeda. Pada perbandingan satu protokol, expanded_base membaik dibanding original, sementara kandidat temporal belum lolos promotion gate.

**Perbaikan:** jadikan prediksi batch model tetap sebagai demonstrasi utama untuk data baru. Bekukan protokol sebelum iterasi, ukur per modus dan kapasitas, gunakan beberapa cutoff/seed dan laporkan ketidakpastian. Dapatkan tinjauan kasus dari verifikator independen. HAN/GNN bukan prasyarat untuk memperbaiki masalah ini.

### 9. Sedang: model tersimpan belum membangun riwayat lintas batch prediksi

**Lokasi:** `core/batch.py:146`; `core/import_data.py:predict_saved`.

Snapshot setiap prediksi adalah `model.history + claims saat ini`. Batch prediksi A tidak otomatis menjadi riwayat ketika model yang sama memprediksi batch B. Penyimpanan antrean tidak dibaca sebagai riwayat fitur.

**Dampak:** hubungan atau kunjungan berulang lintas A–B setelah cutoff tidak terlihat jika pengguna mengunggahnya terpisah. Mengubah pembagian batch juga dapat mengubah agregat dan skor. Ini sesuai implementasi snapshot tertutup sekarang, tetapi membatasi penggunaan rutin berkelanjutan.

**Perbaikan:** jelaskan kontrak snapshot kepada pengguna; jika penggunaan berulang menjadi target, bangun penyimpanan riwayat observasi dengan cutoff/as-of dan deduplikasi. Model tetap tidak perlu dilatih ulang untuk sekadar memperbarui riwayat observasi. Uji A lalu B, koreksi klaim, dan klaim terlambat.

### 10. Sedang: batas ukuran file belum merupakan batas beban komputasi

**Lokasi:** `core/import_data.py:24`; `core/detect.py:104–118`; `core/temporal_features.py:extend`; `core/upcoding_features.py:_tariff_jump`.

Batas 5 MB/file tidak membatasi jumlah klaim per dokter/peserta atau kepadatan timestamp. Konkurensi dokter membentuk set untuk setiap jendela; bila seluruh kunjungan berada dalam satu jendela, pekerjaan dapat mendekati kuadratik. Kandidat lain juga memindai riwayat berulang kali.

**Dampak:** file yang masih di bawah batas ukuran dapat memerlukan waktu lama. Pelatihan berjalan pada request UI tanpa job queue, pembatalan, atau kuota.

**Status bukti:** risiko kompleksitas dibaca dari algoritma; audit ini tidak melakukan stress test besar atau mengukur kapasitas produksi.

**Perbaikan:** tetapkan batas baris, kepadatan, dan waktu proses berdasarkan benchmark; optimalkan jendela bergerak dan gunakan worker terpisah bila skala membutuhkannya.

### 11. Sedang: dashboard demo dan analisis unggahan belum menyatu

**Lokasi:** `components/bench.py:_engine`; `components/sidebar.py:43`; `views/dashboard.py`; `components/external_lab.py`; `core/case_context.py`; `components/layout.py:render_demo_notice`.

Dashboard/klaster/jaringan utama memakai dunia sintetis bawaan. Data unggahan masuk jalur batch dan graf konteksnya sendiri. Label menu demo sudah membantu, tetapi berpindah menu bukan berpindah tampilan atas dataset unggahan yang sama. Sidebar juga memanggil engine demo bahkan saat pengguna membuka halaman batch.

Spanduk global menyebut “Data sintetis”, padahal parser unggahan tidak dapat membuktikan asal sintetis suatu file.

**Perbaikan:** tampilkan sumber dataset aktif di setiap layar dan bedakan “contoh bawaan” dengan “paket pengguna; asal belum diverifikasi”. Buat jalur batch utama yang jelas, dan bangun engine demo hanya ketika diperlukan. Integrasi semua layar harus memakai kontrak konteks data yang eksplisit.

### 12. Sedang: versi cache belum mencakup runtime dependensi

**Lokasi:** `components/bench.py:24–49`; bandingkan `core/batch_store.py:runtime`.

Cache engine menggunakan hash sumber `core/`, seed, dan versi cache. Versi Python/sklearn/numpy/pandas tidak menjadi bagian identitas cache, berbeda dari model batch tersimpan yang memeriksa runtime.

**Dampak:** setelah dependensi berubah, joblib lama yang masih dapat dibaca bisa dipakai kembali; provenance hasil kurang kuat. Tidak dibuktikan cache saat ini salah.

**Perbaikan:** sertakan runtime/lock fingerprint dalam cache key dan metadata, invalidasi cache secara eksplisit, serta simpan provenance build untuk artefak evaluasi.

### 13. Sedang: laporan tanggal deteksi memakai awal minggu meski batch dinilai saat ditutup

**Lokasi:** `core/temporal_impact.py:41`, `:78`, `:81`.

Fitur minggu berjalan dihitung dari snapshot sampai akhir minggu (`hi`), tetapi `jala_date` dan `rules_date` diisi awal minggu (`lo`).

**Dampak:** nama field tanggal dapat memberi kesan temuan sudah tersedia pada awal minggu. Perbandingan indeks minggu tidak otomatis salah, tetapi tanggal ketersediaan hasil tidak tepat.

**Perbaikan:** pisahkan awal jendela observasi dan waktu hasil tersedia. Isi `available_at` dengan penutupan batch; regenerasi artefak dan sesuaikan narasi bila tanggal dipakai.

### 14. Sedang: dokumentasi belum konsisten dengan keadaan implementasi

**Lokasi:** `docs/external-datasets.md:5–12`; `README.md:70`; `views/system_status.py:25`; `docs/validasi.md`; `docs/audit-kesiapan-lanjutan-2026-10-20.md`.

- Panduan impor masih menunjuk About dan nama tombol lama; jalur utama kini Data & Prediksi.
- Panduan eksternal menyebut model belum disimpan di registri, padahal penyimpanan model sudah ada.
- Dokumen validasi menyebut pembangkit terpisah belum ada, padahal modul dan artefaknya sudah tersedia. Pembangkit terpisah tetap bukan validasi pakar independen.
- Laporan audit terdahulu menyimpan hasil tes lama yang gagal. Pertahankan sebagai catatan historis, tetapi beri rujukan ke hasil terbaru.
- Beberapa teks inti masih menyajikan skor dengan `%`, walaupun layar lain memakai `/100`; contoh ada pada `core/live.py` dan `core/feedback.py:describe`.

**Perbaikan:** tetapkan satu sumber untuk kontrak impor, semantik skor, hasil evaluasi, dan status validasi; tandai laporan historis. `DEMO.md` sudah memperbaiki beberapa angka dan keterangan persistensi yang disebut audit lama.

### 15. Sedang: tes belum mencakup beberapa risiko utama yang ditemukan

**Lokasi:** `tests/e2e/`, `tests/test_import_data.py`, `tests/test_batch_store.py`, `tests/test_detect.py`, `tests/conftest.py`.

Ada tes render sembilan route dan AppTest alur contoh→prediksi→simpan→antrean. Tes browser masih berfokus pada demo klaster; belum ada perjalanan browser lengkap untuk unggahan file pengguna, prediksi model tersimpan, tinjauan, reload, dan ekspor. Tidak ada bukti tes isolasi dua pengguna, beban maksimum, penghapusan/retensi, dan kasus tepi yang direproduksi audit ini.

Fixture E2E memakai server berscope sesi, sedangkan variabel path database diubah per tes pada proses induk. Server yang sudah berjalan tidak otomatis menerima perubahan environment tersebut, sehingga klaim isolasi database per tes tidak sepenuhnya berlaku untuk proses E2E.

**Perbaikan:** tambah pengujian yang membuktikan perilaku penting ini; jangan mengandalkan jumlah tes sebagai ukuran cakupan. Pisahkan database server E2E dengan reset fixture yang eksplisit atau server per kelompok tes.

## Urutan pengerjaan

1. **Ketepatan hasil:** perbaiki tarif nol, urutan timestamp sama, dan teks persentase upcoding. Tambahkan tes regresi untuk masing-masing.
2. **Keamanan data lokal:** perjelas simpan model/antrean, sediakan pembersihan sesi dan penghapusan, amankan ekspor spreadsheet.
3. **Konsistensi demo:** perbaiki petunjuk impor, sumber dataset aktif, skor `/100`, dan environment devcontainer.
4. **Bukti deteksi:** bekukan evaluasi batch, ukur per modus dan kapasitas, tinjau kasus sulit dengan calon verifikator.
5. **Sebelum dipakai bersama:** autentikasi, otorisasi pemilik, isolasi penyimpanan, batas beban, backup/restore, dan uji dua pengguna.

Ukuran keberhasilan bukan menambah model atau layar sebanyak mungkin, melainkan hasil yang konsisten pada input yang sama, sumber data yang jelas, keputusan yang dapat ditelusuri, dan pengguna yang dapat menyelesaikan pemeriksaan dengan benar.

## Validasi audit

- Reproduksi kasus tepi: jalankan `.\.venv\Scripts\python.exe scripts/audit_edge_cases.py`. Skrip tidak menulis database atau mengubah data aplikasi.
- Parsing Python, pemeriksaan kedua dependency lock, dan `git diff --check`: lulus pada pemeriksaan audit. Git menampilkan peringatan normalisasi LF/CRLF.
- Suite lengkap: **260 lulus dalam 523,06 detik (8 menit 43 detik)**, termasuk 12 tes E2E. Perintah: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.audit-test-tmp`. Tidak ada tes gagal atau dilewati pada run ini.
- Kasus tepi audit tetap menunjukkan bug meskipun suite lulus: kasus tersebut belum dijaga oleh tes regresi yang ada. Skrip reproduksi sengaja mencetak perilaku aktual, bukan mengklaim perilakunya benar.
- Artefak evaluasi model dibaca, bukan seluruhnya diregenerasi. Tidak dilakukan commit, staging massal, push, atau deployment.
