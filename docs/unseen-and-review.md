# Uji pola yang tidak dilatih dan tinjauan batch

## Protokol

`python -m core.unseen_evaluation` melatih baseline graf + gradient boosting pada generator skenario terpisah (seed 101/211), kemudian memprediksi batch dengan entitas berbeda (seed 1201/1213). Generator lama tidak digunakan karena keluarga fraud sejenis dapat muncul di sana. Model kontrol melihat semua keluarga; tiga model lain masing-masing mengeluarkan satu keluarga dari klaim latih **sebelum fitur dihitung**. Tabel referensi statis dan contoh sah, termasuk layanan awal pasangan repeat, dipertahankan.

Cutoff 1 Oktober 2026, batch uji mulai 5 Oktober. Parameter tidak dituning berdasarkan hasil. Kapasitas 50, 100, 300; skor seri menggunakan expected hits. Lihat [artefak lengkap](unseen-evaluation.json). Ini uji keluarga sintetis yang dikeluarkan dari pelatihan, bukan pembuktian kemampuan mendeteksi semua fraud baru.

## Hasil

Rata-rata recall keluarga yang diuji pada **300 klaim teratas**, dua seed:

| Keluarga | Kontrol: semua keluarga dilatih | Keluarga tersebut dikeluarkan |
| --- | ---: | ---: |
| Phantom distributed | 100% | 11,88% |
| Repeat delayed | 100% | sekitar 50,6% |
| Self-referral one-way | 100% | 1,25% |

Model bergantung pada pola pelatihan. Precision keseluruhan dapat tinggi saat satu keluarga terlewat; karena itu laporan memuat recall per keluarga. Angka tidak dibandingkan langsung dengan 99,33% eksperimen sebelumnya: komposisi data latih dan seed uji berbeda. Hasil sintetis belum menunjukkan kinerja BPJS atau kesesuaian klinis.

## Alur aplikasi

1. About → Dataset uji eksternal: unggah paket atau gunakan contoh, validasi, tentukan cutoff, jalankan prediksi.
2. Pilih **Simpan model terlatih ke basis data lokal** agar model dapat dipakai ulang tanpa pelatihan ulang.
3. Pilih **Kirim hasil ke antrean tinjauan** untuk membuka **Tinjauan batch**.
4. Pilih klaim pada antrean skor, baca atribut dan indikator, isi status serta catatan pemeriksaan.
5. Unduh antrean CSV dan riwayat JSON. Batch lama tetap tersedia setelah aplikasi ditutup; mengirim ulang hasil identik mempertahankan catatan yang sudah tersimpan.
6. Untuk batch berikutnya gunakan panel **Model tersimpan**: prediksi paket baru tanpa melatih ulang, lalu kirim ke antrean tinjauan.

Keputusan tidak mengubah skor, label, atau pembayaran. Selesai ditinjau bukan konfirmasi fraud. Skor adalah skala prioritas, bukan probabilitas terkalibrasi. Indikator mendeskripsikan pola teramati, bukan sebab-akibat.

Skor pada paket contoh ini jenuh di papan atas: 62 dari 448 klaim berada di atas 99,99 dan hanya berbeda pada desimal kelima, dari 169 nilai unik untuk 448 klaim. Urutan di dalam kelompok itu ditentukan oleh ID klaim, bukan oleh perbedaan risiko yang bermakna. Metrik evaluasi sudah menghitung skor seri dengan expected hits, tetapi nomor urut di antarmuka tampak lebih pasti daripada isinya. Karena itu Tinjauan batch dan lab eksternal kini menampilkan persentil peringkat (skor seri mendapat persentil sama) beserta jumlah nilai skor unik, agar kejenuhan itu terlihat, bukan tersirat.

## Penyimpanan lokal

Model terlatih, antrean batch, dan keputusan pemeriksa disimpan di `.jala/batch.sqlite3` (lokasi dapat diganti dengan `JALA_BATCH_DB`), sehingga tetap ada setelah aplikasi ditutup. Model disimpan sebagai pickle dengan kunci SHA-256 dari isinya. Pemuatan menolak blob yang tidak cocok, versi model/fitur yang berbeda, dan lingkungan Python atau library yang berbeda dari saat model dilatih. Prediksi batch baru juga menolak referensi tarif yang berbeda dari model asal, dan hanya menerima klaim setelah cutoff pelatihan.

Setiap keputusan menyimpan nama pemeriksa (kolom `actor`) beserta waktunya, dan halaman Status Sistem menampilkan path basis data, checksum serta versi runtime tiap model tersimpan, jumlah peristiwa per antrean, dan linimasa jejak audit yang dapat diunduh. Ini jejak audit satu pengguna, bukan kontrol akses: nama pemeriksa diisi sendiri dan tidak diverifikasi.

**Batasan yang tetap ada:** basis data ini milik satu pengguna pada satu mesin, bukan layanan audit. Belum ada autentikasi pemeriksa, pembatasan hak akses, atau jejak audit yang tahan perubahan. Jangan pernah membuka jalur unggah pickle dari sumber luar, karena berkas semacam itu dapat mengeksekusi kode sembarang. Untuk penggunaan multi-pengguna, format penyimpanan model harus diganti ke format aman (misalnya skops atau ONNX) dan penyimpanannya dipindahkan ke layanan dengan kontrol akses.
