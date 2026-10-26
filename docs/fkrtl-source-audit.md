# Audit sumber FKRTL - 27 Oktober 2026

Pemindaian seluruh baris pada tiga berkas Reguler dalam Rilis2025.zip.
Hasil agregat: `fkrtl-source-audit.json`; jalankan ulang dengan
`python scripts/audit_fkrtl_source.py <zip> --output <laporan.json>`.
Data mentah dan identitas peserta tidak termasuk laporan/repositori.

- FKRTL: 1.699.219 baris, ID kunjungan unik, 306.710 peserta unik.
- Diagnosis sekunder: 1.967.670 baris untuk 1.367.299 kunjungan; semua ID cocok dengan FKRTL.
  Pengulangan ID kunjungan adalah relasi satu-ke-banyak, bukan otomatis kesalahan data.
- Kepesertaan: 2.590.751 baris dan ID unik; seluruh peserta FKRTL ditemukan.
- Kolom yang dipindai tidak memiliki nilai kosong; bukan jaminan kelengkapan seluruh variabel.
- Tidak ada biaya negatif atau tanggal pulang sebelum datang pada baris yang diperiksa.
- Tanggal datang 15 Juli 2023 sampai 31 Desember 2024; tanggal pulang sepanjang 2024.
- 1.631 kunjungan memiliki biaya tagih berbeda dari biaya verifikasi; selisih ini bukan label fraud.

Kelayakan: kunci mendukung penggabungan untuk analisis kunjungan dan biaya, dengan
agregasi diagnosis sekunder agar biaya tidak terhitung berulang. Audit ini belum
memeriksa validitas klinis, arti kode sentinel, bobot/desain sampel, maupun kelayakan
model fraud. Model JALA tetap memerlukan data dokter, faskes, afiliasi dan waktu
terperinci yang belum tersedia dalam skema sampel ini. Tidak dilakukan pelatihan
atau impor ke aplikasi atas data sampel tersebut.
