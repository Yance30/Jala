# JALA — ringkasan untuk juri

## Masalah

Pemeriksaan satu klaim atau satu dokumen dapat melewatkan pola terkoordinasi lintas fasilitas, dokter, peserta, diagnosis, dan waktu.

## Pendekatan

JALA membangun fitur relasional, mengurutkan klaster berisiko, dan menyiapkan bukti agar verifikator dapat memeriksanya. Sistem hanya memberi prioritas; keputusan akhir tetap pada manusia.

## Bukti yang tersedia

Evaluasi kode membandingkan fitur graf + gradient boosting dengan aturan sederhana pada dunia sintetis berlabel. Pada replay seed 2026 dan kapasitas 35 klaim/minggu selama 14 minggu, JALA menangkap 436 klaim fraud sintetis, aturan 91. Namun pada waktu tangkap pertama, JALA lebih awal hanya pada 1 dari 8 cincin; aturan lebih awal pada 6 dan satu seri. Ini menunjukkan manfaat urutan antrean pada simulasi, tetapi tidak membuktikan JALA mendeteksi cincin lebih cepat. Halaman About juga menunjukkan false positive, sensitivitas salah dismiss, dan batasan.

## Batas

Belum ada data atau label klaim operasional BPJS, evaluasi oleh verifikator, bukti penghematan waktu/biaya, maupun integrasi pembayaran. Hasil saat ini adalah hasil simulasi sintetis, bukan klaim akurasi lapangan.

## Rencana pilot

1. Validasi kontrak dan kualitas data sintetis/pemetaan dengan pemilik data.
2. Jalankan mode bayangan berdampingan dengan proses saat ini, tanpa mengubah pembayaran.
3. Setelah tinjauan hasil, keamanan, privasi, dan persetujuan tata kelola, pertimbangkan integrasi terbatas dengan audit manusia.

**Keputusan yang diminta:** persetujuan untuk merancang pilot terkontrol dan menetapkan pemilik data, verifikator, serta ukuran keberhasilan.
