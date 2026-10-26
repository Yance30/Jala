# Rencana pilot dan proposal JALA

Status 26 Oktober 2026: rancangan untuk dibahas, belum merupakan kesepakatan
dengan BPJS, hasil uji manusia, atau estimasi penghematan yang terbukti.

## Ruang lingkup produk

JALA membantu pemeriksa menyusun prioritas, membaca indikator dan klaim sumber,
lalu mencatat rekomendasi. Pemeriksa memutuskan tindak lanjut. Sistem tidak
menahan pembayaran atau membuktikan fraud secara otomatis.

- Demo sintetis: demonstrasi lengkap jaringan dan perjalanan pemeriksaan.
- Paket data: pelatihan/prediksi hanya untuk paket yang memenuhi kontrak model.
- Sampel FKRTL: audit kelayakan terpisah; belum menjadi mode impor/prediksi.
- Implementasi model: fitur graf + gradient boosting; HAN masih rencana.

## Pilot bertahap

1. Uji alur pada data sintetis dengan calon pemeriksa yang bersedia. Gunakan
   tugas dan rubrik di `review-pilot.md`; catat kegagalan serta kebutuhan bantuan.
2. Konfirmasi kebutuhan dan arti kolom bersama pemilik data. Hasil audit sampel
   tidak menggantikan izin, kontrak data operasional, atau validasi klinis.
3. Pilot terbatas pada lingkungan yang disetujui: akses per peran, penyimpanan,
   retensi, backup, pemulihan, dan penanggung jawab insiden harus ditetapkan dulu.
4. Perluasan hanya setelah manfaat, biaya, dan risiko pilot dievaluasi bersama.

## Peran yang harus dikonfirmasi

| Peran | Tanggung jawab rancangan |
|---|---|
| Pemilik proses pemeriksaan | Menentukan tugas, kapasitas, dan kriteria keberhasilan |
| Pemeriksa | Menelaah bukti dan mencatat rekomendasi beserta alasan |
| Pengelola data | Menyetujui sumber, pemetaan, kualitas, akses, dan retensi |
| Pengelola aplikasi | Deployment, dukungan, backup, pemulihan, dan pemantauan |
| Pengelola model | Versi model, evaluasi perubahan, pergeseran data, dan rollback |

Nama unit, personel, dan pembagian kewenangan belum disepakati.

## Pengukuran manfaat

Bandingkan tugas dengan berkas biasa dan dengan JALA, dengan urutan kondisi
diimbangi untuk mengurangi efek belajar. Gunakan timer tugas yang dihentikan
ketika peserta berhenti bekerja; lama tab terbuka bukan waktu kerja aktif.

| Ukuran | Cara melaporkan |
|---|---|
| Keberhasilan tugas | Jumlah selesai / seluruh tugas, termasuk yang gagal |
| Durasi | Median dan rentang per kondisi; jelaskan jumlah peserta dan kasus |
| Ketepatan pemeriksaan | Rubrik bukti, batas interpretasi, dan rekomendasi |
| Bantuan | Jumlah tugas yang memerlukan petunjuk fasilitator |
| Kesalahan interpretasi | Misalnya menganggap skor sebagai bukti fraud |

Target keberhasilan disepakati sebelum uji, bukan dipilih setelah hasil diketahui.
Tidak mengonversi jumlah kasus ditandai menjadi nilai rupiah fraud dicegah.

## Model operasional dan biaya

Usulan: alat bantu internal yang dikelola pemilik proses bersama tim TI dan data.
Pilihan hosting dan skala diputuskan setelah kebutuhan akses serta beban diketahui.

Anggaran tahun pertama = integrasi awal + pelatihan pengguna + 12 x biaya bulanan.
Biaya bulanan = komputasi + penyimpanan/backup + pemantauan + tenaga dukungan.
Setiap komponen harus dilengkapi volume, satuan, sumber harga, dan penanggung jawab.
Belum ada nominal terverifikasi; jangan mencantumkan ROI sebagai hasil.

## Susunan proposal dan video

1. Masalah dan pengguna: pekerjaan apa yang sulit, berdasarkan wawancara bila ada.
2. Solusi dan pembeda: prioritas, jaringan, bukti yang bisa ditelusuri, keputusan manusia.
3. Data dan metode: sumber sintetis, model aktual, pemisahan data dan batas evaluasi.
4. Bukti: hasil tes aplikasi, eksperimen pembanding, hasil uji manusia bila sudah ada.
5. Implementasi: arsitektur, pilot, peran, biaya dan integrasi yang dibutuhkan.
6. Risiko: kekurangan data, salah penandaan, kebocoran, gangguan layanan, mitigasi.
7. Status dan peta pengembangan: tersedia / diuji / direncanakan, tanpa mencampurkannya.

Demo utama: Dashboard → pilih kasus → baca indikator → telusuri klaim sumber →
catat tindak lanjut → unduh hasil. Alur paket data ditampilkan sebagai kemampuan
tambahan. Nyatakan data sintetis sejak awal dan akhiri dengan batas pembuktian.

## Gerbang kesiapan

- Tes unit/E2E lulus pada commit rilis dan identitas hosting cocok.
- Tidak ada kehilangan keputusan atau ekspor salah kasus pada uji perjalanan.
- Calon pengguna dapat menyelesaikan tugas; temuan yang menghambat sudah diperbaiki.
- Pemilik data dan proses menyetujui sumber serta skenario pilot.
- Akses, retensi, pemulihan dan penanganan insiden diuji sebelum penggunaan bersama.

Kesiapan kompetisi tidak sama dengan kesiapan operasional nasional.
