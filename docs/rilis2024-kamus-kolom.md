# Rilis2024 — kamus kolom terukur

Pendamping [laporan kelayakan](analisis-rilis2024-untuk-jala-2026-10-26.md). Semua 29 tabel data diperiksa penuh. Kosong = null/NaN atau string kosong; kode kategori missing seperti 99 tidak dihitung otomatis. Unik mengikuti nilai non-null dan dapat mencakup string kosong. Tidak memuat ID atau baris peserta.

## KIA2023anak_kepesertaan.dta

KIA - Subset Anak. 292.060 baris; 19 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 292.060 |
| PSTV01_a | Nomor peserta ibu | int32 | 0 | 236.415 |
| PSTV02 | Nomor keluarga | int32 | 0 | 236.415 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 3.284 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 2 |
| PSTV06 | Status perkawinan | int8 | 0 | 1 |
| PSTV07 | Kelas rawat | int8 | 0 | 4 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 5 |
| PSTV09 | Provinsi Tempat Tinggal Peserta | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 515 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 10 |
| PSTV12 | Jenis faskes | int8 | 0 | 4 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | float64 | 2 | 34 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | float64 | 2 | 514 |
| PSTV16 | Tahun Sampel | int16 | 0 | 6 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 3 |
| PSTV18 | Tahun Meninggal | float64 | 285.773 | 9 |

## KIA2023anak_fkrtl.dta

KIA - Subset Anak. 195.953 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 53.756 |
| PSTV01_a | Nomor peserta ibu | int32 | 0 | 48.673 |
| PSTV02 | Nomor keluarga | int32 | 0 | 48.672 |
| FKP02 | No Asal Rujukan (ID Kunjungan FKTP) | str | 115.849 | 28.368 |
| FKL02 | ID Kunjungan | str | 0 | 195.953 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 365 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 386 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 490 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 24 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 37 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat saat peserta mengakses pelayanan kesehatan di FKRTL | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 5 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 1.156 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 1 | 1.156 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 1 | 3.463 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 1 | 3.463 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | int16 | 0 | 869 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 0 | 869 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 0 | 2.317 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 0 | 2.317 |
| FKL19 | Kode INACBGs | str | 0 | 527 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 525 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 21 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 7 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 51 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | int8 | 0 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | int16 | 0 | 506 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 9 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 7 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 32 |
| FKL30 | Jenis prosedur | str | 91.938 | 8.674 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | int32 | 0 | 7.899 |
| FKL33 | Kode special sub-acute groups (SA) | str | 0 | 1 |
| FKL34 | Tarif special sub-acute groups (SA) | int8 | 0 | 1 |
| FKL35 | Kode special procedures (SP) | str | 0 | 4 |
| FKL36 | Deskripsi special procedures (SP) | str | 195.914 | 4 |
| FKL37 | Tarif special procedures (SP) | int32 | 0 | 14 |
| FKL38 | Kode special prosthesis (RR) | str | 0 | 1 |
| FKL39 | Deskripsi special prosthesis (RR) | float64 | 195.953 | 0 |
| FKL40 | Tarif special prosthesis (RR) | int8 | 0 | 1 |
| FKL41 | Kode special investigation(SI) | str | 0 | 3 |
| FKL42 | Deskripsi special investigation(SI) | str | 195.929 | 3 |
| FKL43 | Tarif special investigation(SI) | int32 | 0 | 11 |
| FKL44 | Kode special drugs (SD) | str | 0 | 8 |
| FKL45 | Deskripsi special drugs (SD) | str | 195.573 | 8 |
| FKL46 | Tarif special drugs (SD) | int32 | 0 | 19 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 7.934 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | int32 | 0 | 8.059 |

## KIA2023anak_fktpkapitasi.dta

KIA - Subset Anak. 527.434 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 115.460 |
| PSTV01_a | Nomor peserta ibu | int32 | 0 | 95.607 |
| PSTV02 | Nomor keluarga | int32 | 0 | 95.604 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 527.434 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 365 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 370 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 501 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 5 |
| FKP09 | Tipe FKTP | int8 | 0 | 8 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 11 | 22 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 7 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 1.245 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 145.092 | 1.245 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 3.801 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 3.800 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 482 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 3 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 26 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 54 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |

## KIA2023anak_fkrtldxsekunder.dta

KIA - Subset Anak. 165.487 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 | ID kunjungan FKRTL | str | 0 | 132.779 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 0 | 3.118 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 0 | 1.118 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 0 | 1.118 |

## 202303_fkrtl.dta

Reguler. 1.488.080 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 268.771 |
| PSTV02 | Nomor keluarga | int32 | 0 | 222.314 |
| PSTV15 | Bobot | float32 | 0 | 41.520 |
| FKP02 | No Asal Rujukan (ID Kunjungan FKTP) | str | 614.409 | 300.178 |
| FKL02 | ID Kunjungan | str | 0 | 1.488.080 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 410 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 365 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 494 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 24 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 43 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat saat peserta mengakses pelayanan kesehatan di FKRTL | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 5 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 1.680 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 10 | 1.680 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 10 | 8.386 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 10 | 8.380 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | int16 | 0 | 1.393 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 0 | 1.393 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 0 | 6.045 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 0 | 6.045 |
| FKL19 | Kode INACBGs | str | 0 | 894 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 887 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 23 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 9 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 58 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | int8 | 0 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | int16 | 0 | 514 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 9 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 7 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 32 |
| FKL30 | Jenis prosedur | str | 638.405 | 51.708 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | int32 | 0 | 26.818 |
| FKL33 | Kode special sub-acute groups (SA) | str | 0 | 9 |
| FKL34 | Tarif special sub-acute groups (SA) | int32 | 0 | 44 |
| FKL35 | Kode special procedures (SP) | str | 0 | 14 |
| FKL36 | Deskripsi special procedures (SP) | str | 1.481.120 | 11 |
| FKL37 | Tarif special procedures (SP) | int32 | 0 | 218 |
| FKL38 | Kode special prosthesis (RR) | str | 0 | 6 |
| FKL39 | Deskripsi special prosthesis (RR) | str | 1.487.798 | 4 |
| FKL40 | Tarif special prosthesis (RR) | int32 | 0 | 21 |
| FKL41 | Kode special investigation(SI) | str | 0 | 4 |
| FKL42 | Deskripsi special investigation(SI) | str | 1.486.685 | 4 |
| FKL43 | Tarif special investigation(SI) | int32 | 0 | 40 |
| FKL44 | Kode special drugs (SD) | str | 0 | 11 |
| FKL45 | Deskripsi special drugs (SD) | str | 1.486.421 | 11 |
| FKL46 | Tarif special drugs (SD) | int32 | 0 | 66 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 27.314 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | int32 | 0 | 28.236 |

## 202305_diagnosissekunder.dta

Reguler. 1.642.759 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 |  | str | 0 | 1.178.325 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 0 | 8.063 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 0 | 1.720 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 4 | 1.719 |

## 202304_nonkapitasi.dta

Reguler. 201.297 baris; 21 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor Peserta | int32 | 0 | 50.335 |
| PSTV02 | Nomor keluarga | int32 | 0 | 47.012 |
| PSTV15 | Bobot | float32 | 0 | 14.798 |
| PNK02 | ID Kunjungan | str | 0 | 102.984 |
| PNK03 | Tanggal kunjungan | datetime64[s] | 0 | 371 |
| PNK04 | Tanggal tindakan | datetime64[s] | 0 | 371 |
| PNK05 | Tanggal pulang | datetime64[s] | 0 | 365 |
| PNK06 | Provinsi faskes | int8 | 0 | 34 |
| PNK07 | Kode Kab/Kota faskes | int16 | 0 | 494 |
| PNK08 | Kepemilikan faskes | int8 | 0 | 8 |
| PNK09 | Jenis faskes | int8 | 0 | 6 |
| PNK10 | Tipe faskes | int8 | 0 | 9 |
| PNK11 | Tingkat layanan | int8 | 0 | 3 |
| PNK12 | Segmen peserta | int8 | 0 | 5 |
| PNK13 | Kode dan Nama diagnosis berdasarkan ICD-10 (3 digit) | int16 | 0 | 621 |
| PNK13A | Kode diagnosis berdasarkan ICD-10 (3 digit) | str | 0 | 621 |
| PNK14 | Kode diagnosis (3-5 digit) | str | 0 | 1.399 |
| PNK15 | Nama Diagnosis | str | 0 | 1.399 |
| PNK16 | Nama Tindakan | int16 | 0 | 55 |
| PNK17 | Biaya tagih | int32 | 0 | 1.003 |
| PNK18 | Biaya verifikasi | int32 | 0 | 1.003 |

## 2015202301_kepesertaan.dta

Reguler. 2.501.251 baris; 19 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 2.501.251 |
| PSTV02 | Nomor keluarga | int32 | 0 | 1.004.631 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 36.340 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 2 |
| PSTV06 | Status perkawinan | int8 | 0 | 4 |
| PSTV07 | Kelas rawat | int8 | 0 | 4 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 6 |
| PSTV09 | Provinsi Tempat Tinggal Peserta | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 515 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 10 |
| PSTV12 | Jenis faskes | int8 | 0 | 4 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | int8 | 0 | 35 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | int16 | 0 | 515 |
| PSTV15 | Bobot | float32 | 0 | 153.517 |
| PSTV16 | Tahun Sampel | int16 | 0 | 8 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 4 |
| PSTV18 | Tahun Meninggal | float64 | 2.426.215 | 10 |

## 202302_fktpkapitasi.dta

Reguler. 3.707.596 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 785.472 |
| PSTV02 | Nomor keluarga | int32 | 0 | 469.552 |
| PSTV15 | Bobot | float32 | 0 | 77.570 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 3.707.596 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 365 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 371 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 505 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 6 |
| FKP09 | Tipe FKTP | int8 | 0 | 9 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 59.186 | 23 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 7 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 1.770 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 1.278.446 | 1.770 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 8.873 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 8.867 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 491 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 3 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 29 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 96 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |

## KM20152023_fkrtl.dta

Kesehatan Mental. 2.074.277 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 51.026 |
| PSTV02 | Nomor keluarga | int32 | 0 | 50.886 |
| PSTV15 | Bobot | float32 | 0 | 7.356 |
| FKP02 | ID kunjungan FKTP | str | 788.318 | 375.978 |
| FKL02 | ID Kunjungan FKRTL | str | 0 | 2.074.277 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 3.287 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 3.353 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 493 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 27 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 107 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat peserta | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 5 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 1.682 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 52.983 | 1.682 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 52.983 | 7.974 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 52.983 | 8.104 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | int16 | 0 | 1.400 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 47 | 1.400 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 47 | 5.706 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 47 | 6.345 |
| FKL19 | Kode INACBGs | str | 0 | 884 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 1.120 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 23 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 9 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 56 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | float64 | 8.603 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | float64 | 8.603 | 514 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 10 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 14 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 43 |
| FKL30 | Jenis prosedur | str | 1.004.380 | 47.233 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | float32 | 0 | 25.707 |
| FKL33 | Kode special sub-acute groups (SA) | str | 1.142.244 | 28 |
| FKL34 | Tarif special sub-acute groups (SA) | float64 | 74.341 | 771 |
| FKL35 | Kode special procedures (SP) | str | 1.142.070 | 18 |
| FKL36 | Deskripsi special procedures (SP) | str | 2.071.638 | 18 |
| FKL37 | Tarif special procedures (SP) | float64 | 74.341 | 231 |
| FKL38 | Kode special prosthesis (RR) | str | 1.143.488 | 9 |
| FKL39 | Deskripsi special prosthesis (RR) | str | 2.074.140 | 7 |
| FKL40 | Tarif special prosthesis (RR) | float64 | 74.341 | 36 |
| FKL41 | Kode special investigation(SI) | str | 1.142.946 | 5 |
| FKL42 | Deskripsi special investigation(SI) | str | 2.073.090 | 6 |
| FKL43 | Tarif special investigation(SI) | float64 | 74.341 | 55 |
| FKL44 | Kode special drugs (SD) | str | 1.143.381 | 12 |
| FKL45 | Deskripsi special drugs (SD) | str | 2.073.907 | 14 |
| FKL46 | Tarif special drugs (SD) | float64 | 74.341 | 49 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 27.624 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | float64 | 2 | 27.913 |

## KM20152023_fkrtldxsekunder.dta

Kesehatan Mental. 2.240.698 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 | ID Kunjungan | str | 0 | 1.751.814 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 11 | 7.754 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 11 | 1.689 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 2.644 | 1.686 |

## KM20152023_fktpkapitasi.dta

Kesehatan Mental. 1.743.537 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 53.751 |
| PSTV02 | Nomor keluarga | int32 | 0 | 53.606 |
| PSTV15 | Bobot | float32 | 0 | 7.466 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 1.743.537 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 3.287 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 3.290 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 508 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 7 |
| FKP09 | Tipe FKTP | float64 | 1 | 10 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 3.637 | 30 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 8 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 1.753 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 401.333 | 1.753 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 8.244 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 8.238 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 487 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 9 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 38 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 143 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |

## KM20152023_fktpnonkapitasi.dta

Kesehatan Mental. 2.486 baris; 23 kolom; 27 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor Peserta | int32 | 0 | 417 |
| PSTV02 | Nomor keluarga | int32 | 0 | 417 |
| PSTV15 | Bobot | float32 | 0 | 312 |
| PNK02 | ID Kunjungan | str | 0 | 1.428 |
| PNK03 | Tanggal kunjungan | datetime64[s] | 0 | 1.103 |
| PNK04 | Tanggal tindakan | datetime64[s] | 0 | 1.100 |
| PNK05 | Tanggal pulang | datetime64[s] | 0 | 1.095 |
| PNK06 | Provinsi faskes | int8 | 0 | 31 |
| PNK07 | Kode Kab/Kota faskes | int16 | 0 | 217 |
| PNK08 | Kepemilikan faskes | int8 | 0 | 5 |
| PNK09 | Jenis faskes | int8 | 0 | 6 |
| PNK10 | Tipe faskes | int8 | 0 | 8 |
| PNK11 | Tingkat layanan | int8 | 0 | 3 |
| PNK12 | Segmen peserta | int8 | 0 | 5 |
| PNK13 | Kode dan Nama diagnosis berdasarkan ICD-10 (3 digit) | int16 | 0 | 93 |
| PNK13A | Kode diagnosis berdasarkan ICD-10 (3 digit) | str | 0 | 93 |
| PNK14 | Kode diagnosis (3-5 digit) | str | 0 | 150 |
| PNK15 | Nama Diagnosis | str | 0 | 150 |
| PNK16 | Nama Tindakan | str | 0 | 48 |
| PNK17 | Biaya tagih | int32 | 0 | 94 |
| PNK18 | Biaya verifikasi | int32 | 0 | 94 |
| PNK19 | Hasil Pemeriksaan | float32 | 313 | 562 |
| PNK20 | Hasil Pemeriksaan | float64 | 681 | 29 |

## KM2023_kepesertaan.dta

Kesehatan Mental. 54.820 baris; 19 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 54.820 |
| PSTV02 | Nomor keluarga | int32 | 0 | 54.665 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 22.661 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 2 |
| PSTV06 | Status perkawinan | int8 | 0 | 3 |
| PSTV07 | Kelas rawat | int8 | 0 | 3 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 5 |
| PSTV09 | Provinsi Tempat Tinggal Peserta (34) | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 515 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 9 |
| PSTV12 | Jenis faskes | int8 | 0 | 3 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | int8 | 0 | 34 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | int16 | 0 | 514 |
| PSTV15 | Bobot | float32 | 0 | 7.507 |
| PSTV16 | Tahun Sampel | int16 | 0 | 1 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 3 |
| PSTV18 | Tahun Meninggal | float64 | 53.821 | 1 |

## TB2023_fktpnonkapitasi.dta

TB. 398 baris; 23 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor Peserta | int32 | 0 | 259 |
| PSTV02 | Nomor keluarga | int32 | 0 | 259 |
| PSTV15 | Bobot | float32 | 0 | 195 |
| PNK02 | ID Kunjungan | str | 0 | 362 |
| PNK03 | Tanggal kunjungan | datetime64[s] | 0 | 209 |
| PNK04 | Tanggal tindakan | datetime64[s] | 0 | 209 |
| PNK05 | Tanggal pulang | datetime64[s] | 0 | 198 |
| PNK06 | Provinsi faskes | int8 | 0 | 31 |
| PNK07 | Kode Kab/Kota faskes | int16 | 0 | 157 |
| PNK08 | Kepemilikan faskes | int8 | 0 | 2 |
| PNK09 | Jenis faskes | int8 | 0 | 4 |
| PNK10 | Tipe faskes | int8 | 0 | 7 |
| PNK11 | Tingkat layanan | int8 | 0 | 3 |
| PNK12 | Segmen peserta | int8 | 0 | 4 |
| PNK13 | Kode dan Nama diagnosis berdasarkan ICD-10 (3 digit) | int16 | 0 | 92 |
| PNK13A | Kode diagnosis berdasarkan ICD-10 (3 digit) | str | 0 | 92 |
| PNK14 | Kode diagnosis (3-5 digit) | str | 0 | 144 |
| PNK15 | Nama Diagnosis | str | 0 | 144 |
| PNK16 | Nama Tindakan | str | 0 | 27 |
| PNK17 | Biaya tagih | int32 | 0 | 115 |
| PNK18 | Biaya verifikasi | int32 | 0 | 115 |
| PNK19 | Hasil Pemeriksaan | float32 | 30 | 40 |
| PNK20 | Hasil Pemeriksaan | float64 | 264 | 1 |

## TB2023_fkrtldxsekunder.dta

TB. 30.586 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 | ID Kunjungan | str | 0 | 21.510 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 0 | 1.691 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 0 | 818 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 71 | 816 |

## TB2023_fktpkapitasi.dta

TB. 20.292 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 4.679 |
| PSTV02 | Nomor keluarga | int32 | 0 | 4.609 |
| PSTV15 | Bobot | float32 | 0 | 1.436 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 20.292 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 356 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 357 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 496 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 6 |
| FKP09 | Tipe FKTP | int8 | 0 | 9 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 39 | 21 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 6 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 637 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 2.051 | 637 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 1.316 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 1.316 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 469 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 3 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 21 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 41 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |

## TB2023_fkrtl.dta

TB. 26.739 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 4.423 |
| PSTV02 | Nomor keluarga | int32 | 0 | 4.368 |
| PSTV15 | Bobot | float32 | 0 | 1.321 |
| FKP02 | ID kunjungan FKTP | str | 11.009 | 5.762 |
| FKL02 | ID Kunjungan FKRTL | str | 0 | 26.739 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 367 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 362 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 485 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 23 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 33 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat peserta | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 5 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 657 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 0 | 658 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.383 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.382 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | float64 | 1 | 601 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 0 | 602 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 0 | 1.108 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 0 | 1.108 |
| FKL19 | Kode INACBGs | str | 0 | 465 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 462 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 22 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 8 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 46 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | int8 | 0 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | int16 | 0 | 507 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 9 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 6 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 29 |
| FKL30 | Jenis prosedur | str | 15.359 | 2.919 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | int32 | 0 | 2.648 |
| FKL33 | Kode special sub-acute groups (SA) | str | 0 | 1 |
| FKL34 | Tarif special sub-acute groups (SA) | int8 | 0 | 1 |
| FKL35 | Kode special procedures (SP) | str | 0 | 7 |
| FKL36 | Deskripsi special procedures (SP) | str | 26.711 | 7 |
| FKL37 | Tarif special procedures (SP) | int32 | 0 | 19 |
| FKL38 | Kode special prosthesis (RR) | str | 0 | 2 |
| FKL39 | Deskripsi special prosthesis (RR) | str | 26.738 | 2 |
| FKL40 | Tarif special prosthesis (RR) | int32 | 0 | 2 |
| FKL41 | Kode special investigation(SI) | str | 0 | 2 |
| FKL42 | Deskripsi special investigation(SI) | str | 26.682 | 2 |
| FKL43 | Tarif special investigation(SI) | int32 | 0 | 19 |
| FKL44 | Kode special drugs (SD) | str | 0 | 2 |
| FKL45 | Deskripsi special drugs (SD) | str | 26.738 | 2 |
| FKL46 | Tarif special drugs (SD) | int32 | 0 | 2 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 2.658 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | int32 | 0 | 2.668 |

## TB2023_kepesertaan.dta

TB. 113.694 baris; 19 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 113.694 |
| PSTV02 | Nomor keluarga | int32 | 0 | 109.972 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 28.236 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 2 |
| PSTV06 | Status perkawinan | int8 | 0 | 3 |
| PSTV07 | Kelas rawat | int8 | 0 | 4 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 5 |
| PSTV09 | Provinsi Tempat Tinggal Peserta (34) | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 515 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 9 |
| PSTV12 | Jenis faskes | int8 | 0 | 3 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | int8 | 0 | 34 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | int16 | 0 | 514 |
| PSTV15 | Bobot | float32 | 0 | 42.714 |
| PSTV16 | Tahun Sampel | int16 | 0 | 2 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 3 |
| PSTV18 | Tahun Meninggal | float64 | 100.432 | 5 |

## KIA2023_fkrtldxsekunder.dta

KIA - Subset Ibu. 131.280 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 | ID kunjungan FKRTL | str | 0 | 75.171 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 0 | 1.770 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 0 | 743 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 0 | 743 |

## KIA2023_fktpkapitasi.dta

KIA - Subset Ibu. 1.409.379 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 263.408 |
| PSTV02 | Nomor keluarga | int32 | 0 | 263.190 |
| PSTV15 | Bobot | float32 | 0 | 92.757 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 1.409.379 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 365 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 374 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 505 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 6 |
| FKP09 | Tipe FKTP | int8 | 0 | 9 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 3.599 | 24 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 7 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 1.461 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 571.543 | 1.461 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 5.433 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 5.430 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 490 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 3 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 28 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 65 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |

## KIA2023_fktpnonkapitasi.dta

KIA - Subset Ibu. 216 baris; 23 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor Peserta | int32 | 0 | 64 |
| PSTV02 | Nomor keluarga | int32 | 0 | 64 |
| PSTV15 | Bobot | float32 | 0 | 63 |
| PNK02 | ID Kunjungan | str | 0 | 138 |
| PNK03 | Tanggal kunjungan | datetime64[s] | 0 | 106 |
| PNK04 | Tanggal tindakan | datetime64[s] | 0 | 106 |
| PNK05 | Tanggal pulang | datetime64[s] | 0 | 107 |
| PNK06 | Provinsi faskes | int8 | 0 | 20 |
| PNK07 | Kode Kab/Kota faskes | int16 | 0 | 62 |
| PNK08 | Kepemilikan faskes | int8 | 0 | 3 |
| PNK09 | Jenis faskes | int8 | 0 | 5 |
| PNK10 | Tipe faskes | int8 | 0 | 7 |
| PNK11 | Tingkat layanan | int8 | 0 | 3 |
| PNK12 | Segmen peserta | int8 | 0 | 5 |
| PNK13 | Kode dan Nama diagnosis berdasarkan ICD-10 (3 digit) | int16 | 0 | 33 |
| PNK13A | Kode diagnosis berdasarkan ICD-10 (3 digit) | str | 0 | 33 |
| PNK14 | Kode diagnosis (3-5 digit) | str | 0 | 51 |
| PNK15 | Nama Diagnosis | str | 0 | 51 |
| PNK16 | Nama Tindakan | str | 0 | 35 |
| PNK17 | Biaya tagih | int32 | 0 | 43 |
| PNK18 | Biaya verifikasi | int32 | 0 | 43 |
| PNK19 | Hasil pemeriksaan tindakan | float32 | 62 | 108 |
| PNK20 | Hasil pemeriksaan tindakan | float64 | 87 | 1 |

## KIA2023_fkrtl.dta

KIA - Subset Ibu. 102.907 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 37.878 |
| PSTV02 | Nomor keluarga | int32 | 0 | 37.875 |
| PSTV15 | Bobot | float32 | 0 | 7.740 |
| FKP02 | No Asal Rujukan (ID Kunjungan FKTP) | str | 66.859 | 19.820 |
| FKL02 | ID Kunjungan | str | 0 | 102.907 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 365 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 372 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 490 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 23 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 33 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat saat peserta mengakses pelayanan kesehatan di FKRTL | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 5 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 744 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 0 | 744 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.941 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.941 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | int16 | 0 | 573 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 0 | 573 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 0 | 1.293 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 0 | 1.293 |
| FKL19 | Kode INACBGs | str | 0 | 348 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 347 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 20 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 6 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 42 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | int8 | 0 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | int16 | 0 | 510 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 9 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 7 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 29 |
| FKL30 | Jenis prosedur | str | 18.096 | 8.172 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | int32 | 0 | 3.855 |
| FKL33 | Kode special sub-acute groups (SA) | str | 0 | 1 |
| FKL34 | Tarif special sub-acute groups (SA) | int8 | 0 | 1 |
| FKL35 | Kode special procedures (SP) | str | 0 | 5 |
| FKL36 | Deskripsi special procedures (SP) | str | 102.899 | 4 |
| FKL37 | Tarif special procedures (SP) | int32 | 0 | 16 |
| FKL38 | Kode special prosthesis (RR) | str | 0 | 1 |
| FKL39 | Deskripsi special prosthesis (RR) | float64 | 102.907 | 0 |
| FKL40 | Tarif special prosthesis (RR) | int8 | 0 | 1 |
| FKL41 | Kode special investigation(SI) | str | 0 | 2 |
| FKL42 | Deskripsi special investigation(SI) | str | 102.901 | 2 |
| FKL43 | Tarif special investigation(SI) | int32 | 0 | 6 |
| FKL44 | Kode special drugs (SD) | str | 0 | 3 |
| FKL45 | Deskripsi special drugs (SD) | str | 102.901 | 3 |
| FKL46 | Tarif special drugs (SD) | int32 | 0 | 3 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 3.870 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | int32 | 0 | 3.999 |

## KIA2023_kepesertaan.dta

KIA - Subset Ibu. 468.922 baris; 19 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 468.922 |
| PSTV02 | Nomor keluarga | int32 | 0 | 468.375 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 12.809 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 1 |
| PSTV06 | Status perkawinan | int8 | 0 | 3 |
| PSTV07 | Kelas rawat | int8 | 0 | 4 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 6 |
| PSTV09 | Provinsi Tempat Tinggal Peserta (34) | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 515 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 9 |
| PSTV12 | Jenis faskes | int8 | 0 | 3 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | int8 | 0 | 34 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | int16 | 0 | 514 |
| PSTV15 | Bobot | float32 | 0 | 126.063 |
| PSTV16 | Tahun Sampel | int16 | 0 | 6 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 3 |
| PSTV18 | Tahun Meninggal | float64 | 467.213 | 6 |

## DM2023_fktpnonkapitasi.dta

DM. 3.239 baris; 23 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor Peserta | int32 | 0 | 712 |
| PSTV02 | Nomor keluarga | int32 | 0 | 712 |
| PSTV15 | Bobot | float32 | 0 | 675 |
| PNK02 | ID Kunjungan | str | 0 | 1.581 |
| PNK03 | Tanggal kunjungan | datetime64[s] | 0 | 351 |
| PNK04 | Tanggal tindakan | datetime64[s] | 0 | 350 |
| PNK05 | Tanggal pulang | datetime64[s] | 0 | 349 |
| PNK06 | Provinsi faskes | int8 | 0 | 34 |
| PNK07 | Kode Kab/Kota faskes | int16 | 0 | 255 |
| PNK08 | Kepemilikan faskes | int8 | 0 | 5 |
| PNK09 | Jenis faskes | int8 | 0 | 6 |
| PNK10 | Tipe faskes | int8 | 0 | 9 |
| PNK11 | Tingkat layanan | int8 | 0 | 3 |
| PNK12 | Segmen peserta | int8 | 0 | 5 |
| PNK13 | Kode dan Nama diagnosis berdasarkan ICD-10 (3 digit) | int16 | 0 | 98 |
| PNK13A | Kode diagnosis berdasarkan ICD-10 (3 digit) | str | 0 | 98 |
| PNK14 | Kode diagnosis (3-5 digit) | str | 0 | 161 |
| PNK15 | Nama Diagnosis | str | 0 | 161 |
| PNK16 | Nama Tindakan | str | 0 | 48 |
| PNK17 | Biaya tagih | int32 | 0 | 97 |
| PNK18 | Biaya verifikasi | int32 | 0 | 97 |
| PNK19 | Hasil pemeriksaan tindakan | float32 | 757 | 690 |
| PNK20 | Hasil pemeriksaan tindakan | float64 | 906 | 1 |

## DM2023_fkrtl.dta

DM. 24.516 baris; 55 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 3.090 |
| PSTV02 | Nomor keluarga | int32 | 0 | 3.087 |
| PSTV15 | Bobot | float32 | 0 | 1.243 |
| FKP02 | No Asal Rujukan (ID Kunjungan FKTP) | str | 6.329 | 5.355 |
| FKL02 | ID Kunjungan | str | 0 | 24.516 |
| FKL03 | Tanggal datang kunjungan FKRTL | datetime64[s] | 0 | 358 |
| FKL04 | Tanggal pulang kunjungan FKRTL | datetime64[s] | 0 | 361 |
| FKL05 | Provinsi FKRTL | int8 | 0 | 34 |
| FKL06 | Kabupaten/Kota FKRTL | int16 | 0 | 370 |
| FKL07 | Kepemilikan FKRTL | int8 | 0 | 9 |
| FKL08 | Jenis FKRTL | int8 | 0 | 2 |
| FKL09 | Tipe FKRTL | int8 | 0 | 21 |
| FKL10 | Tingkat Pelayanan FKRTL | int8 | 0 | 2 |
| FKL11 | Jenis Poli FKRTL | int16 | 0 | 32 |
| FKL12 | Segmen Peserta saat akses layanan FKRTL | int8 | 0 | 5 |
| FKL13 | Kelas rawat saat peserta mengakses pelayanan kesehatan di FKRTL | int8 | 0 | 3 |
| FKL14 | Status pulang dari FKRTL | int8 | 0 | 4 |
| FKL15 | Kode dan nama diagnosis masuk ICD 10 (3 digit) | int16 | 0 | 476 |
| FKL15A | Kode diagnosis masuk ICD 10 (3 digit) | str | 0 | 476 |
| FKL16 | Kode ICD 10 diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.062 |
| FKL16A | Nama diagnosis masuk FKRTL (3-6digit) | str | 0 | 1.062 |
| FKL17 | Kode dan nama diagnosis primer ICD 10 (3 digit) | int16 | 0 | 434 |
| FKL17A | Kode diagnosis primer ICD 10 (3 digit) | str | 0 | 434 |
| FKL18 | Kode ICD 10 diagnosis primer FKRTL (3-6digit) | str | 0 | 800 |
| FKL18A | Nama diagnosis primer FKRTL (3-6digit) | str | 0 | 800 |
| FKL19 | Kode INACBGs | str | 0 | 346 |
| FKL19A | Deskripsi kode INACBGs | str | 0 | 346 |
| FKL20 | INACBGs - Kode Casemix main groups (Digit ke-1) | int8 | 0 | 22 |
| FKL21 | INACBGs - Tipe kelompok kasus atau case groups (Digit ke-2) | int8 | 0 | 7 |
| FKL22 | INACBGs - Spesifikasi kelompok kasus (Digit ke-3) | int8 | 0 | 42 |
| FKL23 | INACBGs - Tingkat keparahan kelompok kasus(Digit ke-4) | int8 | 0 | 4 |
| FKL25 | Provinsi faskes perujuk | int8 | 0 | 34 |
| FKL26 | Kabupaten/Kota faskes perujuk | int16 | 0 | 372 |
| FKL27 | Kepemilikan faskes perujuk | int8 | 0 | 9 |
| FKL28 | Jenis faskes perujuk | int8 | 0 | 6 |
| FKL29 | Tipe faskes perujuk | int8 | 0 | 28 |
| FKL30 | Jenis prosedur | str | 11.074 | 1.988 |
| FKL31 | Tarif regional INACBGs | int8 | 0 | 5 |
| FKL32 | Group Tarif INACBGs | int32 | 0 | 1.837 |
| FKL33 | Kode special sub-acute groups (SA) | str | 0 | 1 |
| FKL34 | Tarif special sub-acute groups (SA) | int8 | 0 | 1 |
| FKL35 | Kode special procedures (SP) | str | 0 | 8 |
| FKL36 | Deskripsi special procedures (SP) | str | 24.268 | 8 |
| FKL37 | Tarif special procedures (SP) | int32 | 0 | 45 |
| FKL38 | Kode special prosthesis (RR) | str | 0 | 3 |
| FKL39 | Deskripsi special prosthesis (RR) | str | 24.512 | 2 |
| FKL40 | Tarif special prosthesis (RR) | int32 | 0 | 4 |
| FKL41 | Kode special investigation(SI) | str | 0 | 2 |
| FKL42 | Deskripsi special investigation(SI) | str | 24.501 | 2 |
| FKL43 | Tarif special investigation(SI) | int32 | 0 | 10 |
| FKL44 | Kode special drugs (SD) | str | 0 | 2 |
| FKL45 | Deskripsi special drugs (SD) | str | 24.515 | 2 |
| FKL46 | Tarif special drugs (SD) | int32 | 0 | 2 |
| FKL47 | Biaya Tagih - oleh fasilitas kesehatan (provider) | int32 | 0 | 1.859 |
| FKL48 | Biaya Verifikasi - BPJS Kesehatan setelah dilakukan verifikasi | int32 | 0 | 1.872 |

## DM2023_fkrtldxsekunder.dta

DM. 35.409 baris; 4 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| FKL02 |  | str | 0 | 21.464 |
| FKL24 | Kode diagnosis ICD 10 (beragam 3-5 digit) | str | 0 | 1.297 |
| FKL24A | Kode diagnosis ICD 10 (3 digit) | str | 0 | 606 |
| FKL24B | Kode dan nama diagnosis ICD 10 (3 digit) | str | 0 | 606 |

## DM2023_kepesertaan.dta

DM. 160.082 baris; 21 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 160.082 |
| PSTV02 | Nomor keluarga | int32 | 0 | 159.468 |
| PSTV03 | Tanggal lahir peserta | datetime64[s] | 0 | 19.156 |
| PSTV04 | Hubungan Keluarga | int8 | 0 | 5 |
| PSTV05 | Jenis Kelamin | int8 | 0 | 2 |
| PSTV06 | Status perkawinan | int8 | 0 | 3 |
| PSTV07 | Kelas rawat | int8 | 0 | 4 |
| PSTV08 | Segmentasi peserta | int8 | 0 | 5 |
| PSTV09 | Provinsi Tempat Tinggal Peserta (34) | int8 | 0 | 35 |
| PSTV09_NEW | Provinsi Tempat Tinggal Peserta (38) | int8 | 0 | 39 |
| PSTV10 | Kabupaten/Kota Tempat Tinggal Peserta | int16 | 0 | 492 |
| PSTV11 | Kepemilikan faskes | int8 | 0 | 9 |
| PSTV12 | Jenis faskes | int8 | 0 | 3 |
| PSTV13 | Provinsi Fasilitas Kesehatan Peserta Terdaftar | int8 | 0 | 34 |
| PSTV14 | Kabupaten/Kota Fasilitas Kesehatan Peserta Terdaftar | int16 | 0 | 490 |
| PSTV15 | Bobot | float32 | 0 | 67.448 |
| PSTV16 | Tahun Sampel | int16 | 0 | 2 |
| PSTV17 | Status Kepesertaan | int8 | 0 | 3 |
| PSTV18 | Tahun Meninggal | float64 | 128.350 | 5 |
| PSTV19 | Umur peserta | int16 | 0 | 105 |
| PSTV20 | Range umur peserta | int8 | 0 | 10 |

## DM2023_fktpkapitasi.dta

DM. 1.438.090 baris; 26 kolom; 0 baris identik tambahan.

| Kolom | Label DTA | Tipe | Kosong | Unik |
| --- | --- | --- | ---: | ---: |
| PSTV01 | Nomor peserta | int32 | 0 | 106.848 |
| PSTV02 | Nomor keluarga | int32 | 0 | 106.476 |
| PSTV15 | Bobot | float32 | 0 | 52.271 |
| FKP02 | ID Kunjungan FKTP | str | 0 | 1.438.090 |
| FKP03 | Tanggal datang kunjungan FKTP | datetime64[s] | 0 | 365 |
| FKP04 | Tanggal pulang kunjungan FKTP | datetime64[s] | 0 | 369 |
| FKP05 | Provinsi FKTP | int8 | 0 | 34 |
| FKP06 | Kabupaten/Kota FKTP | int16 | 0 | 490 |
| FKP07 | Kepemilikan FKTP | int8 | 0 | 9 |
| FKP08 | Jenis FKTP | int8 | 0 | 6 |
| FKP09 | Tipe FKTP | int8 | 0 | 9 |
| FKP10 | Tingkat Pelayanan FKTP | int8 | 0 | 3 |
| FKP11 | Jenis Poli FKTP | float64 | 119.407 | 23 |
| FKP12 | Segmen Peserta saat akses layanan FKTP | int8 | 0 | 5 |
| FKP13 | Status Pulang peserta | int8 | 0 | 7 |
| FKP14 | Kode dan nama diagnosis ICD 10 (3 digit) | int16 | 0 | 1.403 |
| FKP14A | Kode diagnosis ICD 10 (3 digit) | str | 401.557 | 1.403 |
| FKP15 | Kode diagnosis (beragam 3-5 digit) | str | 0 | 5.253 |
| FKP15A | Nama diagnosis berasal dari kode diagnosis FKP15 | str | 0 | 5.251 |
| FKP16 | Provinsi faskes tujuan rujukan | int8 | 0 | 35 |
| FKP17 | Kabupaten/Kota faskes tujuan rujukan | int16 | 0 | 478 |
| FKP18 | Kepemilikan faskes tujuan rujukan | int8 | 0 | 10 |
| FKP19 | Jenis faskes tujuan rujukan | int8 | 0 | 3 |
| FKP20 | Tipe faskes tujuan rujukan | int8 | 0 | 29 |
| FKP21 | Poli faskes tujuan rujukan | int16 | 0 | 76 |
| FKP22 | Jenis Kunjungan FKTP | int8 | 0 | 2 |
