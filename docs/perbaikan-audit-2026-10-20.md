# Serah terima perbaikan JALA

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

