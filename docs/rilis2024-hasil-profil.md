# Rilis2024 — hasil profil seluruh tabel

Dihitung 26 Oktober 2026. Pendamping [laporan kelayakan](analisis-rilis2024-untuk-jala-2026-10-26.md).

SHA-256 arsip: `bac4fdf9de961d051c17e7fd7fe2a18cf882fe2951f6d375a803db7d787532af`.

Arsip: 284 entri termasuk direktori/metadata macOS. Berkas substantif: 115 (53 DTA, 43 DO, 19 XLSX), 2.629.941.235 byte sebelum kompresi. DTA terdiri dari 29 tabel data dan 24 kamus ICD. Seluruh tabel data memuat 20.803.484 baris fisik; ini **bukan jumlah klaim atau peserta unik**, karena unit tabel dan kohort berbeda.

Metode: pembacaan seluruh tabel DTA dengan pandas 3.0.6; kategori disimpan sebagai kode dan value labels diperiksa terpisah. String panjang dibaca sebelum mengambil metadata label agar tetap menjadi teks. Semua 19 XLSX diekstrak menggunakan XML ZIP; seluruh 43 DO dibaca sebagai teks. Tidak ada skrip sumber dieksekusi. ZIP dibaca lokal; pembacaan konten anggota memverifikasi CRC. Profil mencakup jumlah baris, kolom, tipe, nilai kosong, kardinalitas, duplikasi identik dan rentang tanggal. Relasi diuji dalam tiap paket, kemudian irisan ID antar-paket. Tidak mencakup pembuktian medis, metode anonimisasi, atau rekonsiliasi ke sistem penerbit.

## Jumlah baris per paket

| Paket | Peserta | FKRTL | FKTP kapitasi | Nonkapitasi | Diagnosis sekunder |
| --- | ---: | ---: | ---: | ---: | ---: |
| DM | 160.082 | 24.516 | 1.438.090 | 3.239 | 35.409 |
| KIA - Subset Anak | 292.060 | 195.953 | 527.434 | Tidak ada file | 165.487 |
| KIA - Subset Ibu | 468.922 | 102.907 | 1.409.379 | 216 | 131.280 |
| Kesehatan Mental | 54.820 | 2.074.277 | 1.743.537 | 2.486 | 2.240.698 |
| TB | 113.694 | 26.739 | 20.292 | 398 | 30.586 |
| Reguler | 2.501.251 | 1.488.080 | 3.707.596 | 201.297 | 1.642.759 |

Tidak ada tabel nonkapitasi pada subset anak. Paket mental mencakup riwayat 2015–2023; paket lain terutama layanan 2023 dengan beberapa tanggal datang/pulang melewati batas tahun. Tahun sampel kepesertaan berbeda dari tahun layanan.

## Hasil relasi dan unit baris

| Paket | FKRTL tanpa peserta | FKTP tanpa peserta | Dx sekunder tanpa kunjungan | Rujukan cocok ke FKTP | Peserta tidak cocok pada rujukan |
| --- | ---: | ---: | ---: | ---: | ---: |
| DM | 0 | 0 | 0 | 18.187 | 0 |
| KIA - Subset Anak | 0 | 0 | 0 | 80.104 | 0 |
| KIA - Subset Ibu | 0 | 0 | 0 | 36.048 | 0 |
| Kesehatan Mental | 0 | 0 | 0 | 1.285.959 | 2 |
| TB | 0 | 0 | 0 | 15.730 | 0 |
| Reguler | 0 | 0 | 0 | 873.671 | 3 |

Pencocokan rujukan di atas memakai `FKP02`; nomor kosong tidak dianggap cocok. Mismatch peserta harus dikarantina, bukan disambungkan otomatis. ID kunjungan FKRTL, ID FKTP kapitasi dan ID peserta unik di masing-masing tabel semua paket (diperiksa penuh). Diagnosis sekunder berelasi banyak-ke-satu ke FKRTL. Semua baris nonkapitasi juga memiliki peserta di tabel kepesertaan paketnya.

| Paket | Baris nonkapitasi | ID kunjungan unik | Baris tambahan pada ID sama | Baris identik tambahan |
| --- | ---: | ---: | ---: | ---: |
| DM | 3.239 | 1.581 | 1.658 | 0 |
| KIA - Subset Ibu | 216 | 138 | 78 | 0 |
| Kesehatan Mental | 2.486 | 1.428 | 1.058 | 27 |
| TB | 398 | 362 | 36 | 0 |
| Reguler | 201.297 | 102.984 | 98.313 | 0 |

Baris identik tambahan dihitung dengan `duplicated()` sesudah kemunculan pertama. Duplikasi identik maupun ID kunjungan berulang tidak membuktikan pembayaran ganda. Untuk nonkapitasi perlu mempertahankan tindakan/tanggal dan provenance baris sebelum deduplikasi.

## Biaya dan kandidat kualitas FKRTL

| Paket | Verifikasi < tagih | Verifikasi = tagih | Verifikasi > tagih | Verifikasi kosong | Komponen ≠ tagih | Peserta–tanggal–dx berulang* |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DM | 28 | 24.488 | 0 | 0 | 246 | 7 |
| KIA - Subset Anak | 208 | 195.745 | 0 | 0 | 1 | 212 |
| KIA - Subset Ibu | 269 | 102.638 | 0 | 0 | 50 | 65 |
| Kesehatan Mental | 660 | 2.073.615 | 0 | 2 | 2.715 | 768 |
| TB | 20 | 26.719 | 0 | 0 | 71 | 13 |
| Reguler | 1.430 | 1.486.649 | 1 | 0 | 35.387 | 670 |

*Baris tambahan setelah kemunculan pertama untuk kombinasi `PSTV01, FKL03, FKL18`; belum dikelompokkan menurut layanan/provider dan **bukan repeat billing terbukti**. Komponen = `FKL32 + FKL34 + FKL37 + FKL40 + FKL43 + FKL46`; ketidaksamaan dengan `FKL47` adalah temuan rekonsiliasi yang perlu dijelaskan, bukan otomatis kesalahan atau fraud. Semua hitungan tidak berbobot.

Tidak ditemukan pulang sebelum datang pada FKRTL/FKTP, atau tanggal tindakan/pulang nonkapitasi sebelum datang, di seluruh paket. Ini hanya pemeriksaan urutan tanggal, bukan kewajaran durasi atau kebenaran layanan.

## Rentang tanggal aktual

| Paket / tabel | Kolom | Minimum | Maksimum | Kosong | Ada jam selain 00:00 |
| --- | --- | --- | --- | ---: | ---: |
| KIA - Subset Anak / KIA2023anak_fkrtl.dta | FKL03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| KIA - Subset Anak / KIA2023anak_fkrtl.dta | FKL04 | 2023-01-01 | 2024-03-06 | 0 | 0 |
| KIA - Subset Anak / KIA2023anak_fktpkapitasi.dta | FKP03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| KIA - Subset Anak / KIA2023anak_fktpkapitasi.dta | FKP04 | 2023-01-01 | 2024-01-05 | 0 | 0 |
| Reguler / 202303_fkrtl.dta | FKL03 | 2022-07-18 | 2023-12-31 | 0 | 0 |
| Reguler / 202303_fkrtl.dta | FKL04 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| Reguler / 202304_nonkapitasi.dta | PNK03 | 2022-12-24 | 2023-12-31 | 0 | 0 |
| Reguler / 202304_nonkapitasi.dta | PNK04 | 2022-12-24 | 2023-12-31 | 0 | 0 |
| Reguler / 202304_nonkapitasi.dta | PNK05 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| Reguler / 202302_fktpkapitasi.dta | FKP03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| Reguler / 202302_fktpkapitasi.dta | FKP04 | 2023-01-01 | 2024-01-15 | 0 | 0 |
| Kesehatan Mental / KM20152023_fkrtl.dta | FKL03 | 2015-01-01 | 2023-12-31 | 0 | 0 |
| Kesehatan Mental / KM20152023_fkrtl.dta | FKL04 | 2015-01-01 | 2024-06-20 | 0 | 0 |
| Kesehatan Mental / KM20152023_fktpkapitasi.dta | FKP03 | 2015-01-01 | 2023-12-31 | 0 | 0 |
| Kesehatan Mental / KM20152023_fktpkapitasi.dta | FKP04 | 2015-01-01 | 2024-01-04 | 0 | 0 |
| Kesehatan Mental / KM20152023_fktpnonkapitasi.dta | PNK03 | 2015-01-21 | 2023-12-29 | 0 | 0 |
| Kesehatan Mental / KM20152023_fktpnonkapitasi.dta | PNK04 | 2015-01-21 | 2023-12-29 | 0 | 0 |
| Kesehatan Mental / KM20152023_fktpnonkapitasi.dta | PNK05 | 2015-01-21 | 2023-12-30 | 0 | 0 |
| TB / TB2023_fktpnonkapitasi.dta | PNK03 | 2023-01-10 | 2023-12-28 | 0 | 0 |
| TB / TB2023_fktpnonkapitasi.dta | PNK04 | 2023-01-10 | 2023-12-28 | 0 | 0 |
| TB / TB2023_fktpnonkapitasi.dta | PNK05 | 2023-01-11 | 2023-12-31 | 0 | 0 |
| TB / TB2023_fktpkapitasi.dta | FKP03 | 2023-01-03 | 2023-12-31 | 0 | 0 |
| TB / TB2023_fktpkapitasi.dta | FKP04 | 2023-01-03 | 2024-01-01 | 0 | 0 |
| TB / TB2023_fkrtl.dta | FKL03 | 2022-12-29 | 2023-12-31 | 0 | 0 |
| TB / TB2023_fkrtl.dta | FKL04 | 2023-01-03 | 2023-12-31 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fktpkapitasi.dta | FKP03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fktpkapitasi.dta | FKP04 | 2023-01-01 | 2024-03-22 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fktpnonkapitasi.dta | PNK03 | 2023-01-02 | 2023-12-19 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fktpnonkapitasi.dta | PNK04 | 2023-01-02 | 2023-12-19 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fktpnonkapitasi.dta | PNK05 | 2023-01-02 | 2023-12-19 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fkrtl.dta | FKL03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| KIA - Subset Ibu / KIA2023_fkrtl.dta | FKL04 | 2023-01-01 | 2024-01-10 | 0 | 0 |
| DM / DM2023_fktpnonkapitasi.dta | PNK03 | 2022-12-30 | 2023-12-31 | 0 | 0 |
| DM / DM2023_fktpnonkapitasi.dta | PNK04 | 2022-12-30 | 2023-12-31 | 0 | 0 |
| DM / DM2023_fktpnonkapitasi.dta | PNK05 | 2023-01-03 | 2023-12-31 | 0 | 0 |
| DM / DM2023_fkrtl.dta | FKL03 | 2023-01-03 | 2023-12-31 | 0 | 0 |
| DM / DM2023_fkrtl.dta | FKL04 | 2023-01-04 | 2024-01-15 | 0 | 0 |
| DM / DM2023_fktpkapitasi.dta | FKP03 | 2023-01-01 | 2023-12-31 | 0 | 0 |
| DM / DM2023_fktpkapitasi.dta | FKP04 | 2023-01-01 | 2024-01-04 | 0 | 0 |

Seluruh kolom tanggal layanan yang diperiksa hanya beresolusi hari. Contoh penting: kunjungan FKRTL reguler mulai 18 Juli 2022; tanggal pulang mental mencapai 20 Juni 2024. Jangan mengklaim seluruh arsip berisi layanan 2015–2023 secara merata.

## Irisan antar-paket

| Paket A | Paket B | ID peserta sama | ID FKRTL sama | ID FKTP sama | ID nonkapitasi sama |
| --- | --- | ---: | ---: | ---: | ---: |
| DM | KIA - Subset Anak | 0 | 0 | 0 | n/a |
| DM | KIA - Subset Ibu | 49 | 12 | 471 | 0 |
| DM | Kesehatan Mental | 137 | 51 | 2.019 | 1 |
| DM | TB | 860 | 274 | 253 | 0 |
| DM | Reguler | 2.217 | 639 | 19.503 | 29 |
| KIA - Subset Anak | KIA - Subset Ibu | 2 | 0 | 3 | n/a |
| KIA - Subset Anak | Kesehatan Mental | 115 | 1.922 | 725 | n/a |
| KIA - Subset Anak | TB | 130 | 8 | 5 | n/a |
| KIA - Subset Anak | Reguler | 1.986 | 1.559 | 3.868 | n/a |
| KIA - Subset Ibu | Kesehatan Mental | 127 | 63 | 845 | 0 |
| KIA - Subset Ibu | TB | 309 | 6 | 9 | 0 |
| KIA - Subset Ibu | Reguler | 5.883 | 1.153 | 14.179 | 0 |
| Kesehatan Mental | TB | 99 | 136 | 41 | 0 |
| Kesehatan Mental | Reguler | 581 | 5.600 | 3.775 | 2 |
| TB | Reguler | 2.097 | 859 | 684 | 21 |

Irisan di atas berarti kesamaan literal ID, belum bukti seluruh atribut episode sama. Sebelum menggabungkan paket harus membandingkan isi baris, asal sampel, periode dan bobot. Jangan menjumlah tabel kohort langsung.

## Inventaris semua berkas substantif

| Path relatif dari Data Sampel 2015-2023 | Byte | Baris DTA |
| --- | ---: | ---: |
| 2023 Metadata Data Sampel BPJS Kesehatan.xlsx | 64.880 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 88.872 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/icd10_info.dta | 11.805 | 1.994 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/icd10_info_dxprimer.dta | 9.705 | 1.574 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/icd10_info_dxmasuk.dta | 11.315 | 1.896 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 118.017 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/icd10_info_pnk.dta | 7.660 | 1.165 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 55.861 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/1_KIAkepesertaan.do | 80.805 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/4_KIAfktpnonkapitasi.do | 41.322 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/6_tables.do | 1.242 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/5_KIAdiagnosissekunder.do | 1.307 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/2_KIAfktpkapitasi.do | 85.719 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/dofiles/3_KIAfkrtl.do | 84.348 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/data/KIA2023anak_kepesertaan.dta | 9.676.810 | 292.060 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/data/KIA2023anak_fkrtl.dta | 78.195.224 | 195.953 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/data/KIA2023anak_fktpkapitasi.dta | 99.272.141 | 527.434 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Anak/data/KIA2023anak_fkrtldxsekunder.dta | 5.369.194 | 165.487 |
| Data Sampel Reguler Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 88.872 | n/a |
| Data Sampel Reguler Edisi 2024/icd10/icd10_info.dta | 11.805 | 1.994 |
| Data Sampel Reguler Edisi 2024/icd10/icd10_info_dxprimer.dta | 9.705 | 1.574 |
| Data Sampel Reguler Edisi 2024/icd10/icd10_info_dxmasuk.dta | 11.315 | 1.896 |
| Data Sampel Reguler Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 118.017 | n/a |
| Data Sampel Reguler Edisi 2024/icd10/icd10_info_pnk.dta | 7.660 | 1.165 |
| Data Sampel Reguler Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 55.861 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/3_FKRTL.do | 84.182 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/2_FKTP_KAPITASI.do | 85.761 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/7_RSE.do | 6.394 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/1_KEPESERTAAN.do | 80.731 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/5_DIAGNOSIS_SEKUNDER.do | 2.293 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/4_FKTP_NONKAPITASI.do | 40.890 | n/a |
| Data Sampel Reguler Edisi 2024/dofiles/6_TABLES.do | 1.983 | n/a |
| Data Sampel Reguler Edisi 2024/data/202303_fkrtl.dta | 548.067.889 | 1.488.080 |
| Data Sampel Reguler Edisi 2024/data/202305_diagnosissekunder.dta | 52.682.955 | 1.642.759 |
| Data Sampel Reguler Edisi 2024/data/202304_nonkapitasi.dta | 39.314.106 | 201.297 |
| Data Sampel Reguler Edisi 2024/data/2015202301_kepesertaan.dta | 82.580.164 | 2.501.251 |
| Data Sampel Reguler Edisi 2024/data/202302_fktpkapitasi.dta | 256.515.937 | 3.707.596 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 89.088 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/icd10_info.dta | 11.855 | 2.004 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/icd10_info_dxprimer.dta | 9.735 | 1.580 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/icd10_info_dxmasuk.dta | 11.385 | 1.910 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 118.802 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/icd10_info_pnk.dta | 7.665 | 1.166 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 55.931 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/4_KMfktpnonkapitasi.do | 41.514 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/2_KMfktpkapitasi.do | 86.362 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/7_RSE.do | 3.891 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/5_KMdiagnosissekunder.do | 1.118 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/6_tables.do | 3.562 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/1_KMkepesertaan2023.do | 81.245 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/dofiles/3_KMfkrtl.do | 93.808 | n/a |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/data/KM20152023_fkrtl.dta | 708.787.133 | 2.074.277 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/data/KM20152023_fkrtldxsekunder.dta | 71.814.490 | 2.240.698 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/data/KM20152023_fktpkapitasi.dta | 120.952.899 | 1.743.537 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/data/KM20152023_fktpnonkapitasi.dta | 609.348 | 2.486 |
| Data Sampel Kontekstual Kesehatan Mental Edisi 2024/data/KM2023_kepesertaan.dta | 1.847.972 | 54.820 |
| Data Sampel Kontekstual TB Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 87.456 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/icd10/icd10_info.dta | 11.750 | 1.983 |
| Data Sampel Kontekstual TB Edisi 2024/icd10/icd10_info_dxprimer.dta | 9.590 | 1.551 |
| Data Sampel Kontekstual TB Edisi 2024/icd10/icd10_info_dxmasuk.dta | 11.175 | 1.868 |
| Data Sampel Kontekstual TB Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 119.647 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/icd10/icd10_info_pnk.dta | 7.145 | 1.062 |
| Data Sampel Kontekstual TB Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 54.444 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/1_TBkepesertaan2023.do | 81.170 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/7_RSE.do | 3.863 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/3_TBfkrtl.do | 93.520 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/5_TBdiagnosissekunder.do | 1.091 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/6_tables.do | 3.844 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/4_TBfktpnonkapitasi.do | 41.481 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/dofiles/2_TBfktpkapitasi.do | 86.252 | n/a |
| Data Sampel Kontekstual TB Edisi 2024/data/TB2023_fktpnonkapitasi.dta | 125.941 | 398 |
| Data Sampel Kontekstual TB Edisi 2024/data/TB2023_fkrtldxsekunder.dta | 1.031.829 | 30.586 |
| Data Sampel Kontekstual TB Edisi 2024/data/TB2023_fktpkapitasi.dta | 3.857.056 | 20.292 |
| Data Sampel Kontekstual TB Edisi 2024/data/TB2023_fkrtl.dta | 13.862.955 | 26.739 |
| Data Sampel Kontekstual TB Edisi 2024/data/TB2023_kepesertaan.dta | 3.790.814 | 113.694 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 88.093 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/icd10_info.dta | 13.817 | 1.997 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/icd10_info_dxprimer.dta | 9.645 | 1.562 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/icd10_info_dxmasuk.dta | 11.265 | 1.886 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 120.491 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/icd10_info_pnk.dta | 7.330 | 1.099 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 54.211 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/7_RSE.do | 3.877 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/7_merge.do | 991 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/4_KIAfktpnonkapitasi.do | 41.352 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/6_tables.do | 1.922 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/5_KIAdiagnosissekunder.do | 1.385 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/1_KIAkepesertaan_1.do | 80.922 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/2_KIAfktpkapitasi.do | 85.605 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/dofiles/3_KIAfkrtl.do | 84.108 | n/a |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/data/KIA2023_fkrtldxsekunder.dta | 4.249.839 | 131.280 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/data/KIA2023_fktpkapitasi.dta | 97.700.398 | 1.409.379 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/data/KIA2023_fktpnonkapitasi.dta | 76.594 | 216 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/data/KIA2023_fkrtl.dta | 34.781.688 | 102.907 |
| Data Sampel Kontekstual KIA Edisi 2024 - Subset Ibu/data/KIA2023_kepesertaan.dta | 15.513.203 | 468.922 |
| Data Sampel Kontekstual DM Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Kapitasi.xlsx | 87.625 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/icd10/icd10_info.dta | 11.765 | 1.986 |
| Data Sampel Kontekstual DM Edisi 2024/icd10/icd10_info_dxprimer.dta | 9.605 | 1.554 |
| Data Sampel Kontekstual DM Edisi 2024/icd10/icd10_info_dxmasuk.dta | 11.220 | 1.877 |
| Data Sampel Kontekstual DM Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKRTL.xlsx | 119.991 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/icd10/icd10_info_pnk.dta | 7.315 | 1.096 |
| Data Sampel Kontekstual DM Edisi 2024/icd10/2023 Kode ICD10 untuk diagnosis FKTP Non Kapitasi.xlsx | 54.154 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/2_DMfktpkapitasi.do | 86.033 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/3_DMfkrtl.do | 84.009 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/7_RSE.do | 3.851 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/5_DMdiagnosissekunder.do | 1.346 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/7_merge.do | 991 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/6_tables.do | 1.917 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/4_DMfktpnonkapitasi.do | 41.361 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/dofiles/1_DMkepesertaan.do | 81.173 | n/a |
| Data Sampel Kontekstual DM Edisi 2024/data/DM2023_fktpnonkapitasi.dta | 771.430 | 3.239 |
| Data Sampel Kontekstual DM Edisi 2024/data/DM2023_fkrtl.dta | 13.918.971 | 24.516 |
| Data Sampel Kontekstual DM Edisi 2024/data/DM2023_fkrtldxsekunder.dta | 1.172.888 | 35.409 |
| Data Sampel Kontekstual DM Edisi 2024/data/DM2023_kepesertaan.dta | 5.803.419 | 160.082 |
| Data Sampel Kontekstual DM Edisi 2024/data/DM2023_fktpkapitasi.dta | 353.893.862 | 1.438.090 |
