# Serah terima perbaikan JALA

## Validasi snapshot - 26 Oktober 2026

- Seluruh kode aplikasi lokal sama dengan `origin/main` pada `69eb8ee` setelah normalisasi akhir baris. Snapshot ini memperbarui README, catatan rilis, dan tiga dokumen kajian Rilis2024.
- Pengujian ulang lokal: **280 tes unit lulus** (289,28 detik), **18 tes browser lulus** (625,87 detik), kedua lock dependensi dan `python -m core.evaluate` lulus.
- Percobaan awal terhalang izin folder sementara lama. Pengulangan memakai folder terpisah dan selesai tanpa kegagalan. Hasil lokal tidak menggantikan status CI GitHub atau verifikasi deployment.
- Data mentah BPJS, hasil ekstraksi, database, kredensial, dan screenshot lokal tidak disertakan. Kajian Rilis2024 memuat skema dan agregat; integrasi data belum diimplementasikan.

## Pemeriksaan rilis - 26 Oktober 2026

- PR #3 sudah memiliki perbaikan tiga ekspektasi E2E lama pada commit `69e4aa6`; CI run `39838896735` lulus.
- Navigasi batch kini membawa pilihan tahap dari Tinjau ke bagian persiapan, validasi, atau prediksi. Data sesi tetap dipertahankan; prediksi tanpa paket aktif kembali ke persiapan.
- Label langkah kedua alur memakai angka dan titik, tanpa karakter tanda tanya.
- Tes browser diperluas untuk tujuan navigasi pada desktop dan mobile, serta kecocokan ID ekspor dengan kasus yang diperiksa.
- PR #3 telah digabung ke `main` pada commit `69eb8ee904159e7ce882b5c6554743c3ba06e89e`: https://github.com/Yance30/Jala/pull/3.
- CI PR commit `fac736c` lulus: 280 tes unit, 18 tes browser (termasuk navigasi batch desktop/mobile), lock, dan benchmark. Run: https://github.com/Yance30/Jala/actions/runs/40226359101.
- Hosting merespons HTTP 200 setelah merge. SHA deployment dan klik pada hosting belum terverifikasi: akses browser khusus JALA belum tersedia (persetujuan aplikasi timeout).
- Catatan hasil merge PR #3 diperbarui pada snapshot 26 Oktober 2026. Catatan lokal di bawah adalah riwayat tahap sebelumnya.

## Status terbaru — 22 Oktober 2026

### Lanjutan — 23 Oktober 2026

- Pengulangan petunjuk pada Data & Prediksi dan chip penjelasan skor pada detail klaim dikurangi. Petunjuk saat model tersimpan belum tersedia kini menunjuk pilihan Latih model baru.
- Tes alur AppTest data contoh → latih → simpan → pilih model tersimpan → prediksi klaim setelah periode pelatihan → buat antrean lulus. Tes memakai database terisolasi.
- Baris langkah 1–4 sudah berupa tombol navigasi kembali, dengan kasus terpilih dipertahankan; bukan tombol tambahan di luar baris langkah.
- Branch rilis `feat/clear-review-flow` dibuat dari `origin/main`. Penyalinan berkas ke worktree rilis tidak selesai dan telah dihentikan; belum ada commit/push baru pada tahap ini.
- Alat browser gagal diinisialisasi pada pemeriksaan ini. Pemeriksaan visual hosting/mobile belum dapat diselesaikan.

- Pengiriman UX telah digabung ke `main` melalui [PR #2](https://github.com/Yance30/Jala/pull/2), commit `efcaf752bddfec588b86f40804439ed569924dd5`.
- CI PR lulus: 263 tes unit dan 16 tes browser E2E, pemeriksaan lock, serta benchmark.
- [CI setelah merge](https://github.com/Yance30/Jala/actions/runs/39649911786) juga lulus pada job `test` dan `e2e`.
- Versi hosting publik belum terverifikasi. Kelulusan CI tidak membuktikan versi yang sedang berjalan di Streamlit Cloud.
- Pemeriksaan HTTP pada alamat publik mendapat status 200. Ini hanya memastikan halaman awal merespons; browser pemeriksaan tidak tersedia, sehingga tampilan dan SHA deployment belum dapat dicocokkan.
- Penanda versi ditambahkan pada halaman Tentang. Commit dibaca dari checkout yang berjalan; perubahan lokal ditandai. Jika metadata Git tidak tersedia, UI menyatakan commit tidak tersedia, bukan menebak versi hosting.
- Penambahan penanda versi dan pembaruan dokumen ini masih lokal; keduanya belum termasuk commit merge `efcaf75` maupun deployment publik.
- Untuk image tanpa `.git`, pengelola deployment dapat memasok `JALA_BUILD_COMMIT` berisi SHA sumber build. Nilai ini harus berasal dari proses build, bukan disalin dari commit terbaru secara manual.

## Riwayat implementasi dan validasi

### Penyederhanaan alur pemeriksaan — 22 Oktober 2026

- Risk Ranking menampilkan skor /100 tanpa paragraf berulang; kategori tabel memakai nama pendek. Penjelasan skor tetap ada pada pengantar halaman.
- Status membedakan belum ditinjau, pemeriksaan berjalan, dan hasil pola wajar yang telah dicatat pada demo. Rencana lapangan dan penangguhan simulasi tidak dianggap selesai. Pilihan urutan belum selesai lebih dahulu mempertahankan urutan skor dalam kelompok.
- Kartu utama Tindak Lanjut memuat status klaster; blok Ringkasan pola terukur dan pemberitahuan status duplikat dihapus. Bukti tetap dapat ditinjau melalui detail kasus dan paket pemeriksaan.
- Baris empat tahap menjadi tombol navigasi ke tahap sebelumnya; tahap aktif dan berikutnya tidak dapat diklik. Pilihan kasus tetap dibawa saat kembali ke bukti.
- Data & Prediction menjelaskan pilihan data contoh/unggahan, lalu memisahkan latihan model baru dan pemakaian model tersimpan.
- Perubahan ini masih lokal. Pemeriksaan menggunakan AppTest; tampilan browser hosting belum diverifikasi.

### Pemeriksaan navigasi lokal — 22 Oktober 2026

- Pemeriksaan awal: 59 tes halaman, tinjauan, panduan dan penanda versi lulus; 5 tes tambahan untuk seluruh tujuan sidebar, pintu masuk Data & Prediksi dan perjalanan kasus juga lulus.
- Ditemukan alamat `?page=` belum mengikuti perpindahan melalui tombol. Navigasi kini menyelaraskan alamat dengan halaman aktif; state halaman tidak dikenal kembali ke dashboard.
- Setelah koreksi, 8 tes navigasi dan alias halaman lulus dalam 44,28 detik, termasuk membuka tautan hasil navigasi pada sesi baru; `git diff --check` untuk `app.py` lulus.
- Pemeriksaan memakai Streamlit AppTest, bukan browser hosting. Ini memeriksa callback tombol, tujuan dan render halaman, tetapi tidak membuktikan klik sentuh, unduhan browser, tautan jangkar atau pemuatan JavaScript di hosting.
- Tombol login/logout OIDC belum diuji dengan penyedia nyata. Tombol yang memerlukan data, identitas pemeriksa atau konfirmasi tetap mengikuti prasyaratnya; tidak semua tombol harus berpindah halaman.
- Perubahan navigasi dan tes baru masih lokal, belum dikirim ke hosting.

Catatan di bawah merekam kondisi pada setiap tahap. Pernyataan belum commit/push
dan hasil tes bertahap merupakan riwayat, bukan status pengiriman terbaru di atas.

## Pembaruan pengiriman UX poin 2–5

Ringkasan batch kini mengutamakan periode, jumlah klaim dan sumber; metadata teknis
berada di expander. Pintasan jangkar menghubungkan antrean, detail dan formulir.
Progres menggunakan status terbaru, bukan banyaknya catatan: Belum ditinjau,
Dalam pemeriksaan, dan Selesai. Hanya Selesai ditinjau serta Penjelasan layanan wajar
termasuk selesai. Graf konteks tertutup awalnya agar tindakan berikutnya lebih jelas.

Pengiriman disiapkan pada branch `feat/review-ux-2-5` dari `origin/main` terbaru.
Modul batch pendukung yang sebelumnya hanya lokal disertakan, bersama tes,
dokumentasi, konfigurasi prototipe dan ZIP data sintetis. Database, log, screenshot,
serta direktori pengujian lokal tidak termasuk. Catatan tidak adanya commit/push
di bagian historis berikut merujuk tahap pekerjaan sebelumnya.

Pekerjaan dimulai 20 Oktober dan dilanjutkan 21 Oktober 2026. Dokumen ini menggantikan status sementara pada percakapan. Audit lama dipertahankan sebagai catatan historis.

## Perubahan yang telah diterapkan

| Temuan / saran | Implementasi |
|---|---|
| Isolasi penyimpanan | Default demo memakai identitas sesi acak buatan server. Mode bersama memerlukan OIDC dengan issuer dan subject yang valid; setiap pemilik memiliki database terpisah. Dialog juga membaca identitas sesi pada setiap akses. |
| Siklus hidup data | UI menjelaskan salinan klaim dalam model, observasi dan antrean. Tersedia pembersihan sesi, penghapusan model, antrean, atau seluruh ruang batch. Model lama tidak dihapus otomatis. |
| Tarif nol | Nol–nol memiliki selisih relatif nol; pembagi nol tidak menghasilkan NaN. Regresi mencakup nol–nol, nol–positif dan positif–nol. |
| Timestamp identik | Urutan pembanding memakai ID secara deterministik. Teks menyebut waktu identik dan tidak mengklaim urutan layanan. |
| Teks upcoding | Penyebut dijelaskan sebagai tarif saat ini; tidak lagi diklaim sebagai persentase kenaikan dari median. |
| CSV | Ekspor antrean dan bukti menetralkan karakter formula tanpa memodifikasi data sumber. |
| Environment | Devcontainer memakai Python 3.12 dan lock; proteksi CORS/XSRF default aktif. Docker memakai user non-root. Peluncur lokal Windows memperbarui dari lock dan mengikat localhost. |
| Evaluasi | Benchmark lama diberi batas retrospektif/transduktif. Protokol batch baru dibekukan; hasil mencakup enam kombinasi seed/cutoff, kapasitas 20/50/100 dan hasil per keluarga. |
| Riwayat antarbatch | Prediksi model tersimpan menyertakan observasi sebelumnya tanpa melatih ulang bobot. Konflik perubahan klaim dan replay mundur ditolak. Penyimpanan mempertahankan presisi float/waktu. |
| Beban komputasi | Batas snapshot, referensi, peserta, dan kepadatan dokter diperiksa sebelum fitur. Pencarian catatan pembanding memakai indeks waktu dan serialisasi satu kali. |
| Sumber layar | Halaman batch diberi identitas sumber yang berbeda dari dunia demo. Sidebar tidak membangun engine demo untuk halaman batch. |
| Cache | Fingerprint mencakup versi runtime dan kedua lock. |
| Tanggal replay | Tanggal hasil adalah penutupan minggu, dengan field available_at. |
| Dokumentasi | Petunjuk impor, penyimpanan, validasi dan model card diselaraskan; laporan historis ditandai. |
| Pengujian | Ditambahkan regresi kasus tepi, dua pemilik, dua sesi browser, riwayat observasi, backup, unggah→tinjau→reload→ekspor→hapus. Setiap tes browser mendapat server/database sendiri. |

## Tujuh saran pengembangan

1. **Konteks indikator:** catatan sumber, klaim pembanding dan nilai fitur tersedia pada detail tinjauan; maksimal delapan catatan per kelompok ditampilkan beserta jumlah keseluruhannya. Konteks bukan atribusi model atau bukti fraud.
2. **Skor, prioritas dan keputusan:** antrean batch menyimpan skor model tetap, prioritas kerja (dahulukan/ikuti model/tunda), dan hasil pemeriksa secara terpisah. Demo klaster mempertahankan skor dasar dalam umpan balik.
3. **Data belum cukup:** tanggal tanpa jam pada seluruh kolom waktu tidak diberi skor rendah; penilaian ditolak dengan alasan yang jelas. Ini pemeriksaan konservatif, bukan validasi semantik sumber.
4. **Hasil tinjauan:** penjelasan layanan wajar, kesalahan data dan data belum cukup ditambahkan. Keputusan tidak otomatis menjadi label pelatihan.
5. **Demo berulang:** `artifacts/jala-review-pack.zip` memuat paket data, hasil yang diharapkan, tiga tugas, kunci fasilitator, manifest hash dan lembar observasi kosong.
6. **Kualitas antrean:** kapasitas 20/50/100 menampilkan precision, recall, kasus sah yang ikut diperiksa dan fraud terlewat. Evaluasi multi-run ada di `docs/evaluation-v2.json`; rentang antar-run bukan interval kepercayaan.
7. **Uji calon verifikator:** protokol, tugas, rubrik dan lembar observasi disiapkan di `docs/review-pilot.md`. Pelaksanaan dengan manusia belum dilakukan dan hasilnya tidak direka.

## Menjalankan dan melanjutkan

- Lokal Windows: `run_demo.bat` (mode satu pengguna, localhost).
- Demo per sesi: `streamlit run app.py` tanpa JALA_MODE=local.
- Mode bersama: ikuti `docs/deployment-and-data.md`; jangan membuka layanan sebelum konfigurasi login dan tes dua akun di hosting sebenarnya.
- Model batch utama sekarang v3; kandidat temporal/upcoding v2. Model dengan versi sebelumnya harus dilatih ulang. Database lama tetap tersedia melalui mode lokal.
- Paket dan evaluasi: `python scripts/build_review_pack.py --evaluate`.
- Tes: `python -m pytest -q`; lock: `python scripts/check_lock.py requirements-lock.txt requirements-lock-win.txt`.
- Backup tepercaya: `python scripts/storage_backup.py --database <asal> --output <file-baru>`; tidak menimpa file lama.

## Validasi dan batas yang masih memerlukan tindakan luar

- Sebelum perbaikan: 260 tes lulus, tetapi kasus tepi audit menunjukkan bug.
- Run pertama setelah perluasan: 275 tes, 273 lulus dan dua kegagalan browser. Penyebabnya identitas penyimpanan pada dialog serta locator checkbox. Setelah perbaikan, **16 tes terarah lulus dalam 164,96 detik**, mencakup kedua tes browser yang sebelumnya gagal, isolasi dua sesi, serta regresi numerik/penyimpanan/backup. Suite penuh belum diulang seluruhnya setelah koreksi terakhir; tidak ada kegagalan yang masih diketahui dari run tersebut.
- `compileall`, kedua dependency lock, dan `git diff --check` lulus. Peringatan Git hanya normalisasi LF/CRLF.
- Tambahan **14 tes replay temporal, konsistensi angka dokumentasi, dan riwayat pemeriksaan lulus** dalam 15,41 detik setelah regenerasi artefak.
- Tes integritas ZIP, manifest hash, versi model, tiga tugas dan lembar observasi kosong: **1 lulus**. Total tes yang ditemukan kini 276; jangan menyebut 276 lulus dalam satu run karena pengujian terakhir dilakukan bertahap seperti dicatat di atas.
- Evaluasi enam kombinasi seed/cutoff dan ZIP demonstrasi dibangun ulang dari kode terakhir. Replay kapasitas 35 klaim/minggu juga diregenerasi: delapan cincin sintetis selama 14 minggu, dengan tanggal ketersediaan hasil pada penutupan batch.
- OIDC nyata belum diuji karena penyedia login, kredensial dan hosting belum dikonfigurasi. Tambahan dependensi login opsional memakai ekstra Streamlit; bekukan lock deployment lengkap sebelum rilis bersama.
- Belum ada uji verifikator nyata, data operasional, validasi klinis, pengujian beban produksi, SLA atau worker asinkron. Batas beban prototipe tidak menggantikan hal tersebut.
- Database per pemilik belum mendukung pembagian satu antrean antarpegawai. Log tidak tahan perubahan administrator. Hapus model dan antrean untuk menghapus kedua salinan; backup/unduhan memerlukan pengelolaan terpisah.
- Tidak dilakukan commit, push atau deployment. Worktree sudah memiliki banyak perubahan sebelum pekerjaan ini; tinjau dan pilih file secara eksplisit sebelum commit.
# Pematangan antarmuka — 21 Oktober 2026

Alur operasional sekarang menampilkan lima tahap dari persiapan data sampai unduhan.
Tinjauan mendukung pemilihan baris, **Simpan & lanjut**, pengingatan nama pemeriksa
selama sesi, ID klaim aktif, dan reset filter. Label antrean memakai bahasa Indonesia;
tarif memakai rupiah dan waktu layanan/pengajuan menyebut UTC. Catatan pembanding
dipisahkan dari rincian fitur teknis. Sumber batch, perilaku penyimpanan sesuai mode,
dan fungsi kedua unduhan dijelaskan di UI. Latar halaman operasional disederhanakan.

Panduan penggunaan diperbarui dalam `docs/ux-flow.md`. Perubahan ini tidak mengubah
model, skor, atau format CSV ekspor. Uji browser mencakup simpan-lanjut, nama pemeriksa,
reset pencarian, muat ulang keputusan, ekspor, penghapusan, dan isolasi sesi demo.
Tampilan juga diperiksa pada lebar 390 piksel. Uji kegunaan bersama calon pemeriksa
tetap diperlukan untuk menilai apakah petunjuk dipahami tanpa bantuan.

Verifikasi pematangan UX:

- Putaran penuh: **275 lulus, 1 gagal**, 707,98 detik. Kegagalan merupakan asumsi
  posisi caption dalam tes antrean; isi keputusan tersimpan tetap benar. Assertion
  diperbarui untuk mencari isi caption tanpa bergantung pada urutan tampilan.
- Uji ulang `tests/test_review_queue.py` dan `tests/e2e/test_batch_journey.py`:
  **9 lulus**, 124,71 detik, termasuk kasus yang gagal. Seluruh kegagalan yang
  ditemukan pada putaran ini sudah terselesaikan; suite penuh tidak diulang lagi.
- `compileall`, kedua pemeriksaan lock dependensi, dan `git diff --check`: lulus.
- Tangkapan browser desktop dan ponsel diperiksa; tes layar 390 piksel memastikan
  halaman tidak melebar secara horizontal. Ini bukan audit aksesibilitas lengkap.
- Hasil mesin tersimpan di `.jala/ux-final-tests.xml` dan
  `.jala/ux-recheck-tests.xml` (diabaikan Git). Tidak ada commit atau deployment.

