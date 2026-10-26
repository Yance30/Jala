# Kelayakan Rilis2024 untuk JALA

Tanggal pemeriksaan: 26 Oktober 2026. Sumber: `C:\Users\yansg\Downloads\Rilis2024.zip`.

## Keputusan

**Data ini berguna untuk JALA, tetapi tidak bisa langsung dipakai menjalankan detektor JALA yang sekarang.** Pemakaian paling kuat adalah modul analisis episode peserta, diagnosis, INA-CBG, biaya, serta konteks pola layanan. Untuk jaringan fraud antar-dokter atau antar-faskes, unsur identitas dan waktu yang diperlukan tidak tersedia di tabel yang diperiksa.

Prioritas pertama: **paket reguler, khususnya FKRTL + diagnosis sekunder + kepesertaan**, kemudian FKTP untuk konteks rujukan yang berhasil ditautkan. Paket kontekstual dipakai sebagai kohort pembanding terpisah. Mesin skor perlu jalur baru yang memang bekerja pada resolusi tanggal dan tanpa identitas provider, bukan sekadar mengganti nama kolom.

Ini adalah audit kelayakan data dan kode lokal. Tidak ada perubahan mesin JALA, impor ke database aplikasi, pelatihan model, unggahan data, atau deployment. Perintah dalam berkas `.do` dibaca sebagai dokumentasi; tidak dijalankan.

## Ringkasan bukti dari isi arsip

Seluruh **115 berkas substantif** diperiksa: 29 tabel data Stata, 24 tabel kamus Stata, 19 Excel dan 43 skrip Stata. Tabel data berjumlah **20.803.484 baris fisik**, termasuk peserta, kunjungan dan diagnosis sekunder; bukan 20,8 juta klaim unik. Ukuran sebelum kompresi sekitar 2,63 GB.

| Paket | Nilai untuk JALA | Prioritas dan batas |
|---|---|---|
| Reguler | 1.488.080 kunjungan FKRTL, 3.707.596 FKTP, 2.501.251 peserta | Sumber utama eksplorasi episode/biaya dan acuan distribusi; tetap sampel |
| Kesehatan mental | 2.074.277 FKRTL pada 54.820 peserta, riwayat 2015–2023 | Berguna untuk riwayat panjang dan pola kunjungan berulang; jangan dicampur sebagai populasi umum |
| DM | 1.438.090 FKTP dan 24.516 FKRTL | Konteks layanan penyakit kronis; komposisi layanan berbeda jauh dari reguler |
| TB | 20.292 FKTP dan 26.739 FKRTL | Kohort khusus untuk konteks episode dan tindak lanjut, bukan label fraud |
| Ibu | 1.409.379 FKTP dan 102.907 FKRTL | Konteks pelayanan maternal; pisahkan pembanding klinis |
| Anak | 527.434 FKTP dan 195.953 FKRTL | Konteks pediatrik dan kolom penghubung ibu; tidak ada file nonkapitasi dan tidak ada bobot `PSTV15` |

Temuan kualitas yang mempengaruhi keputusan:

- Seluruh ID peserta dalam tabel layanan cocok dengan tabel peserta paketnya; seluruh diagnosis sekunder cocok dengan ID FKRTL. Ini mendukung analisis hubungan episode secara nyata.
- Dari 873.671 baris rujukan reguler yang ID kunjungannya cocok ke FKTP, **3 berbeda peserta**; pada mental ada **2** mismatch. Join harus memeriksa peserta juga, bukan ID kunjungan saja.
- Nonkapitasi reguler memiliki **201.297 baris tetapi hanya 102.984 ID kunjungan**. Menjadikan seluruh ID berulang sebagai repeat billing akan salah secara unit analisis.
- Nonkapitasi mental memiliki **27 baris identik tambahan**. FKRTL mental memiliki **47 diagnosis primer kosong**, **52.983 diagnosis masuk kosong**, dan **2 biaya verifikasi kosong**. Karantina atau tangani per fitur; jangan isi otomatis sebagai kondisi normal.
- FKRTL reguler memiliki **1.430** baris biaya verifikasi lebih rendah dari tagih, **1** lebih tinggi, dan **35.387** baris dengan jumlah komponen tarif berbeda dari biaya tagih. Ini bisa menjadi daftar rekonsiliasi; belum menjelaskan penyebab atau fraud.
- Ada **670 baris tambahan** dengan kombinasi peserta–tanggal datang–diagnosis primer sama pada FKRTL reguler. Ini dapat menjadi kandidat pemeriksaan episode, dengan konteks klinis; bukan 670 fraud.
- Paket memang bertumpang tindih: mental dan reguler memiliki **5.600 ID FKRTL sama**; DM dan reguler memiliki **19.503 ID FKTP sama**. Menggabungkan atau membagi latih/uji antar-paket tanpa pemeriksaan ID akan menghasilkan penghitungan ganda/kebocoran evaluasi.
- Semua tanggal layanan hanya menunjukkan tengah malam. Rentang aktual juga melampaui nama tahun: kedatangan FKRTL reguler mulai **18 Juli 2022**, kepulangan mental mencapai **20 Juni 2024**.

## Yang betul-betul dapat digunakan

| Sumber | Kolom inti | Pemakaian yang sah secara analitis | Batas |
|---|---|---|---|
| FKRTL | `PSTV01`, `FKL02`, `FKL03`, `FKL04` | Riwayat episode peserta, lama rawat, kunjungan berulang per hari, kandidat episode tumpang tindih | ID kunjungan bukan nomor transaksi pembayaran; tidak ada jam layanan |
| Diagnosis FKRTL | `FKL16`, `FKL18`, `FKL17A` | Diagnosis masuk vs primer, kelompok diagnosis, riwayat penyakit | Perubahan diagnosis tidak otomatis upcoding |
| Diagnosis sekunder | `FKL02`, `FKL24`, `FKL24A`, `FKL24B` | Konteks komorbiditas dan penjelasan sah untuk kompleksitas kasus | Hubungan satu kunjungan ke banyak diagnosis; agregasikan sebelum menjumlah biaya |
| INA-CBG | `FKL19`–`FKL23`, `FKL31`, `FKL32` | Pembandingan biaya pada kelompok kasus/layanan/kelas/wilayah tarif yang sebanding | Tarif per diagnosis saja, seperti kontrak JALA sekarang, terlalu menyederhanakan sumber ini |
| Biaya FKRTL | `FKL47`, `FKL48` | Selisih biaya tagih dan biaya verifikasi, pemeriksaan konsistensi nilai | Biaya verifikasi bukan status sudah dibayar; selisih bukan label fraud |
| Komponen khusus | `FKL33`–`FKL46` | Memeriksa komponen tambahan dan konteks biaya | `NONE`, kosong dan nol dapat berarti komponen tidak berlaku, bukan kesalahan |
| Prosedur | `FKL30` | Konteks tindakan dan pemeriksaan kesesuaian data | Teks dapat memuat beberapa tindakan; tidak lengkap pada seluruh kunjungan; belum validasi klinis |
| FKTP kapitasi | `FKP02`–`FKP04`, `FKP13`–`FKP22` | Frekuensi kunjungan, diagnosis, jenis kunjungan, status pulang, konteks rujukan | Tidak memuat biaya klaim per kunjungan; jangan mengarang tarif nol sebagai biaya nyata |
| FKTP nonkapitasi | `PNK02`–`PNK05`, `PNK14`, `PNK16`–`PNK18` | Analisis baris tindakan dan biaya, pengelompokan episode | `PNK02` tidak unik; baris berulang pada ID kunjungan belum berarti tagihan ganda |
| Kepesertaan | `PSTV01`, `PSTV03`–`PSTV10`, `PSTV16`–`PSTV18` | Konteks umur pada tanggal layanan, jenis kelamin, wilayah, segmen dan cohort | Status/kelas/wilayah kepesertaan tidak otomatis merupakan keadaan historis saat setiap layanan |
| Bobot | `PSTV15` jika tersedia | Ringkasan survei mengikuti desain sampel yang sesuai | Bukan bobot risiko fraud; jangan menggandakan baris untuk merepresentasikan populasi |
| Anak–ibu | `PSTV01_a` pada subset anak | Menghubungkan konteks ibu–anak dengan pemeriksaan cakupan ID | Hubungan keluarga bukan hubungan kolusi; jangan pakai sebagai sinyal fraud otomatis |
| Kamus ICD | Berkas `icd10/*.xlsx` dan `*.dta` | Dekode kategori diagnosis dan tampilan penjelasan | Bukan referensi tarif dan bukan keputusan klinis; kamus antar-paket tidak boleh diasumsikan identik |

Tambahan khusus: nonkapitasi kontekstual memiliki `PNK19`/`PNK20` berlabel hasil pemeriksaan, tetapi label itu sendiri belum menetapkan jenis pemeriksaan, satuan dan rentang interpretasi. Jangan jadikan nilainya fitur klinis lintas tindakan sebelum semantik itu dipastikan. `PNK20` pada DM, TB dan ibu hanya berisi nol atau missing sehingga tidak memberi variasi numerik hasil pemeriksaan. Kepesertaan DM juga memiliki `PSTV19` (umur) dan `PSTV20` (kelompok umur); umur tersimpan mencapai 124 tahun. Periksa acuan tanggal/perhitungan, dan jangan menyamakan umur snapshot dengan umur saat setiap layanan.

Kolom jenis, tipe, kepemilikan, kabupaten dan provinsi faskes dapat membentuk **kelompok pembanding fasilitas**, tetapi tidak mengidentifikasi satu fasilitas. Misalnya banyak RS swasta kelas C dapat berada pada kabupaten yang sama. Gabungan atribut itu tidak boleh diberi nama `faskes_id` lalu digunakan untuk mendeteksi cincin provider.

## Kecocokan dengan fitur JALA

| Fitur | Keputusan untuk arsip ini | Alasan / hasil yang masih masuk akal |
|---|---|---|
| Phantom billing melalui konkurensi dokter | Tidak tersedia | Tidak ada ID dokter, SIP/afiliasi, atau waktu menit |
| Pengajuan klaim serentak | Tidak tersedia | Tidak ada waktu pengajuan klaim |
| Self-referral dokter ke tempat praktiknya | Tidak tersedia | Tidak ada identitas dokter/perujuk maupun afiliasi dan identitas unik provider |
| Repeat billing seperti model sekarang | Tidak tersedia dengan makna yang sama | Tersedia kandidat kunjungan berulang per hari, tetapi tanpa pembayaran dan jam tidak dapat menilai ambang 48 jam secara tepat |
| Jaringan peserta–kunjungan–diagnosis–INA-CBG | Layak dikembangkan | Entitas dan hubungan memang ada; node wilayah/jenis layanan harus dinamai kelompok, bukan provider |
| Episode rawat inap dan kunjungan kembali | Layak dikembangkan | Tanggal datang/pulang dan tingkat layanan tersedia; pisahkan rawat jalan/rawat inap dan tangani batas periode |
| Kandidat upcoding / anomali kompleksitas | Eksplorasi terbatas | Diagnosis, komorbiditas dan tingkat keparahan tersedia; perlu penyesuaian case-mix serta tinjauan klinis sebelum kesimpulan |
| Anomali biaya relatif kelompok sebanding | Layak dikembangkan | Pembanding berdasarkan INA-CBG, tingkat layanan, kelas, tipe RS, regional dan komponen khusus; ukuran kelompok minimum harus ditetapkan |
| AUC/precision/recall fraud nyata | Tidak dapat dihitung | Tidak ada label fraud hasil pemeriksaan; tidak boleh menganggap semua baris non-fraud |
| Kalibrasi data sintetis | Layak | Distribusi umur/diagnosis/biaya/interval harian bisa menjadi acuan; dokter, jam dan label tambahan tetap dinyatakan sintetis |

Modul anomali tanpa label juga tetap memerlukan evaluasi: tinjauan manual terstruktur, stabilitas antarperiode, pemeriksaan pola sah yang ikut ditandai, serta pengukuran cakupan data. Skor anomali tidak dapat dipasarkan sebagai probabilitas fraud terkalibrasi.

## Mengapa tidak dapat langsung diunggah ke JALA

Kontrak aktual diperiksa di `core/contract.py`, `core/import_data.py`, `core/data_quality.py`, dan `core/workload.py`.

| Kontrak JALA | Padanan sumber | Keputusan |
|---|---|---|
| `patient_id` | `PSTV01` | Dapat dipetakan sebagai teks; pertahankan namespace dan provenance paket |
| `claim_id` | `FKL02` / `FKP02` / `PNK02` | ID episode/kunjungan; bukan padanan semantik penuh klaim. Nonkapitasi perlu ID baris dan ID episode terpisah |
| `icd` | `FKL18`, `FKP15`, `PNK14` | Bisa dipetakan setelah normalisasi kode; diagnosis sekunder harus tetap tersimpan terpisah |
| `tarif` | `FKL47` atau `PNK17` | Definisikan sebagai nilai ditagih; simpan nilai diverifikasi pada kolom lain. Kapitasi tidak punya padanan biaya per baris |
| `visit_ts` | `FKL03` / `FKP03` / `PNK03` | Hanya tanggal; cocok untuk kontrak baru `visit_date`, tidak cukup untuk model saat ini |
| `submit_ts` | Tidak ada | Tanggal pulang atau tindakan bukan tanggal pengajuan |
| `faskes_id` | Tidak ada identitas unik provider | Wilayah, jenis, tipe dan kepemilikan bukan pengganti |
| `doctor_id` | Tidak ada | Jenis faskes "Dokter Umum" bukan ID dokter |
| `referral_from_faskes` | Atribut perujuk dan `FKP02` | `FKP02` di FKRTL menunjuk kunjungan asal, bukan ID faskes |
| `referral_from_doctor` / `affiliations` | Tidak ada | Tidak dapat diisi dengan dokter dummy untuk model nyata |
| `patients.home_region` | `PSTV09`/`PSTV09_NEW`, `PSTV10` | Dapat dipetakan setelah menyelaraskan versi wilayah dan periode |
| `faskes.capacity` | Tidak ada | Jumlah kunjungan sampel bukan kapasitas fasilitas |
| `tariff_caps.json` | Tidak ada tabel plafon ICD seperti kontrak JALA | Nilai tarif yang teramati bukan plafon resmi per diagnosis |
| `labels.is_fraud` | Tidak ada | Selisih verifikasi, biaya tinggi, atau kunjungan ulang tidak boleh otomatis menjadi label fraud |

Hambatan teknis tambahan: importer hanya menerima paket CSV/JSON dengan nama dan kolom tertentu, maksimal 5.000.000 byte per file. Snapshot dibatasi 30.000 klaim, referensi 50.000 baris, serta 500 klaim per peserta. Kolom tambahan ditolak. Pelatihan memerlukan label historis. `require_time_resolution` menolak tanggal tanpa jam. Konversi DTA ke CSV saja tidak menyelesaikan hambatan ini.

## Keputusan pengolahan yang wajib dijaga

1. **Pisahkan unit baris.** FKRTL/FKTP adalah tabel kunjungan; diagnosis sekunder adalah tabel anak; nonkapitasi memiliki beberapa baris per kunjungan. Jangan melakukan join diagnosis lalu menjumlah kembali biaya kunjungan.
2. **Pisahkan arti tanggal.** Simpan tanggal datang, pulang dan tindakan masing-masing. Jangan membuat jam acak atau mengganti waktu pengajuan dengan tanggal pulang. Periksa cakupan tanggal aktual, bukan nama file saja.
3. **Dekode kategori.** `FKL23`: 1 = rawat jalan; 2 = ringan/keparahan rawat inap 1; 3 = sedang/keparahan 2; 4 = berat/keparahan 3. Jangan memperlakukan 4 sebagai severity level IV. Label tipe/jenis perujuk juga perlu mengikuti value labels aktual, karena metadata Excel memuat ketidaksesuaian penamaan kategori `FKL28`/`FKL29` terhadap label DTA.
4. **Pisahkan nol, kosong dan kode khusus.** Missing teknis dan kode seperti 9/99/999/9999 harus dibaca per kamus kolom, bukan diganti secara global. Deskripsi tambahan kosong saat kode `NONE` adalah kondisi berbeda dari diagnosis primer kosong.
5. **Pertahankan denominasi.** Setiap KPI menyebut jumlah peserta/kunjungan/baris tindakan, paket, periode dan bobot yang digunakan. Jumlah sampel tidak boleh disebut jumlah nasional atau volume operasional satu rumah sakit.
6. **Pertahankan provenance kohort.** Jangan langsung menggabungkan reguler, DM, TB, mental, ibu dan anak. ID yang bertumpang tindih harus diperiksa; bobot dan desain pemilihan paket berbeda.
7. **Cegah kebocoran waktu.** Biaya verifikasi adalah hasil proses kemudian, tetapi tanggal ketersediaannya tidak disediakan. Jangan menjadikannya fitur untuk model yang diklaim bekerja sebelum verifikasi. Label/status kepesertaan terkini juga belum tentu tersedia pada cutoff historis.
8. **Pertahankan hasil sebagai kandidat pemeriksaan.** Anomali administratif/episode perlu penjelasan sah dan peninjauan. Selisih biaya bukan kerugian fraud yang terbukti.

## Urutan pengembangan yang disarankan

**Tahap 1 — eksplorasi lokal:** reader Stata yang menjaga string panjang dan value labels; tabel terpisah untuk peserta, kunjungan FKRTL, diagnosis sekunder, FKTP, tindakan nonkapitasi, serta kamus. Simpan dalam format kolumnar/penyimpanan analitis dan proses bertahap. Jangan memuat seluruh arsip ke sesi Streamlit atau melewati batas beban aplikasi saat ini.

**Tahap 2 — panel yang dapat dipertanggungjawabkan:** kualitas sumber, distribusi INA-CBG/biaya, lama rawat, kunjungan berulang harian, episode tumpang tindih, selisih verifikasi dan konteks rujukan yang benar-benar cocok. Sediakan detail baris sumber lokal serta alasan kandidat ditandai. Mulai dengan FKRTL reguler dan agregasi diagnosis sekunder; perluas ke FKTP/nonkapitasi setelah unit baris benar.

**Tahap 3 — pembandingan terukur:** uji modul harian pada kohort terpisah, termasuk DM/TB/mental untuk mengevaluasi seberapa sering layanan berulang rutin terangkat sebagai kandidat. Data kohort sendiri tidak membuktikan semua layanannya sah; istilah "false positive" memerlukan hasil peninjauan atau label yang memadai. Pisahkan peserta dan waktu untuk evaluasi sesuai tujuan generalisasi; hindari peserta/episode yang sama masuk latih dan uji lewat paket berbeda.

**Tahap 4 — jaringan fraud provider:** membutuhkan tambahan ID provider stabil, ID dokter dan afiliasi beserta masa berlaku, asal/tujuan provider yang eksplisit, waktu layanan/pengajuan, status pembayaran, referensi tarif yang sesuai, serta label hasil pemeriksaan. Arsip ini sendiri tidak dapat memenuhi tahap itu.

Arsip memuat data sampel dengan ID dan riwayat kesehatan, bukan generator dummy milik JALA. Audit ini tidak membuktikan metode anonimisasi, hak redistribusi, atau izin demo publik. Tidak ditemukan dokumen izin/lisensi khusus di inventaris berkas. Untuk penggunaan publik atau kompetisi, cocokkan syarat perolehan data dan ketentuan penyelenggara yang berlaku; tidak dilakukan penilaian hukum dalam audit ini. Sampai kejelasan itu tersedia, hasil yang dibagikan cukup agregat dan seluruh baris tetap lokal.

## Bukti pemeriksaan menyeluruh

Angka lengkap, inventaris semua tabel, pemeriksaan relasi, dan cakupan tanggal terdapat pada [lampiran hasil hitung](rilis2024-hasil-profil.md). [Kamus kolom terukur](rilis2024-kamus-kolom.md) mencatat tipe data, label, jumlah kosong dan kardinalitas setiap kolom tabel data. Angka tersebut berasal dari pembacaan seluruh baris, bukan preview beberapa record.
