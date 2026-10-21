# Pemetaan data: skema sintetis JALA ke data klaim nyata

Dokumen ini jujur tentang satu hal: **skema resmi data klaim BPJS Kesehatan tidak kami ketahui**, jadi kolom di kanan
bawah ini hanya *konsep padanan*, bukan nama kolom resmi, dan semuanya **belum dikonfirmasi ke panitia**.
Yang pasti hanya kolom sintetis (kolom 1) dan apa yang JALA lakukan dengannya (kolom 4); keduanya dijaga tes
(`tests/test_data_mapping.py`).

Aturan guidebook: data peserta JKN nyata dilarang tanpa izin tertulis (butir 5o, bagian 12), jadi seluruh data di
repo ini sintetis.

## 1. Skema sintetis dan padanan konsepnya

### Tabel `claims` (satu baris per klaim)

| Kolom sintetis | Arti | Padanan konsep di data nyata (belum dikonfirmasi) | Dipakai JALA untuk |
|---|---|---|---|
| `claim_id` | ID klaim (pseudonim) | ID klaim atau transaksi | kunci baris |
| `faskes_id` | faskes penagih | kode faskes | semua fitur per faskes |
| `doctor_id` | dokter yang menangani (pseudonim) | dokter penanggung jawab pelayanan, bila tersedia | konkurensi dokter lintas faskes, rujukan |
| `patient_id` | peserta (pseudonim) | ID peserta yang dianonimkan | klaim berulang, peserta lintas faskes |
| `icd` | kode diagnosis gaya ICD-10 | diagnosis (ICD-10) | klaim berulang, tarif terhadap plafon |
| `tarif` | nilai klaim (Rp) | nilai atau biaya klaim | tarif terhadap plafon |
| `visit_ts` | waktu pelayanan | tanggal dan jam pelayanan | konkurensi dokter, jarak antar klaim |
| `submit_ts` | waktu klaim dikirim | tanggal dan jam klaim diajukan | lonjakan pengiriman serentak |
| `referral_from_faskes` | faskes perujuk (kosong bila bukan rujukan) | data rujukan: faskes perujuk | rujukan dan siklus rujukan balik |
| `referral_from_doctor` | dokter perujuk (kosong bila bukan rujukan) | data rujukan: dokter perujuk | rujukan ke faskes terafiliasi |

### Tabel `faskes`

| Kolom sintetis | Arti | Padanan konsep di data nyata (belum dikonfirmasi) | Dipakai JALA untuk |
|---|---|---|---|
| `faskes_id` | kode faskes | kode faskes | kunci |
| `name` | nama faskes (hanya tampilan) | nama faskes | tampilan layar dan berkas bukti |
| `type` | `puskesmas`, `klinik`, `rs_c`, `rs_b` | jenis dan kelas faskes (FKTP/FKRTL) | normalisasi terhadap faskes sejenis |
| `region` | wilayah faskes | wilayah faskes | peserta luar wilayah |
| `capacity` | kapasitas relatif (sintetis) | belum diketahui; ukuran kapasitas atau volume layanan | klaim per kapasitas terhadap faskes sejenis |

### Tabel `affiliations`

| Kolom sintetis | Arti | Padanan konsep di data nyata (belum dikonfirmasi) | Dipakai JALA untuk |
|---|---|---|---|
| `doctor_id` | dokter | dokter yang sama dengan `claims.doctor_id` | rujukan ke faskes terafiliasi |
| `faskes_id` | faskes tempat dokter terdaftar praktik | data praktik atau SIP dokter | rujukan ke faskes terafiliasi |

### Tabel `patients`

| Kolom sintetis | Arti | Padanan konsep di data nyata (belum dikonfirmasi) | Dipakai JALA untuk |
|---|---|---|---|
| `patient_id` | peserta (pseudonim) | ID peserta yang dianonimkan | kunci |
| `home_region` | wilayah domisili peserta | wilayah domisili atau wilayah terdaftar | peserta luar wilayah |

Tabel `labels` (`is_fraud`, `typology`, `group`, `legit_kind`) hanya ada di data sintetis dan hanya dipakai untuk menilai;
detektor menolak kolom ini. Data nyata tidak akan punya label seperti ini.

## 2. Kontrak data minimal

Status setelah perbaikan audit: unggahan melalui **Data & Prediksi**. Data dengan cap waktu yang
seluruhnya tengah malam ditolak untuk penilaian sebagai **data belum cukup**, bukan diberi skor rendah.
Keberadaan jam saja tetap belum membuktikan ketelitian sumber. Model batch v3 memakai pembanding
timestamp identik dengan urutan ID deterministik dan menyatakan bahwa urutan itu bukan urutan layanan.
Lihat [panduan impor](external-datasets.md), [siklus hidup data](deployment-and-data.md), dan
[status perbaikan](perbaikan-audit-2026-10-20.md).

Pipeline hanya membutuhkan kolom di bawah (didefinisikan di `core/contract.py`, dicek otomatis oleh
`build_features`). Kolom di luar daftar ini, seperti `faskes.name`, tidak dibutuhkan.

| Tabel | Kolom wajib |
|---|---|
| `claims` | `claim_id`, `faskes_id`, `doctor_id`, `patient_id`, `icd`, `tarif`, `visit_ts`, `submit_ts`, `referral_from_faskes`, `referral_from_doctor` |
| `faskes` | `faskes_id`, `type`, `region`, `capacity` |
| `affiliations` | `doctor_id`, `faskes_id` |
| `patients` | `patient_id`, `home_region` |

Bila panitia menyediakan data simulasi, pekerjaannya adalah menulis adapter yang memetakan kolom mereka ke tabel di
atas. Bila ada kolom wajib yang hilang, `validate` menyebut kolom mana yang kurang.

### Pencocokan awal dengan variabel dalam rencana dataset

Matriks ini mencocokkan kontrak JALA dengan variabel yang telah disebut dalam percakapan: PSTV01, PSTV02,
PSTV15, FKP02, FKP03, FKL02, FKL24, PNK02, dan PNK03. Ini **belum verifikasi terhadap kamus data lengkap atau
file dataset**. Status "terindikasi" berarti variabel tampak tersedia pada cuplikan yang dibahas; arti, nilai,
relasi, dan konsistensinya tetap perlu diperiksa pada dokumentasi/data sumber.

| Fitur/relasi JALA | Data yang dibutuhkan JALA | Variabel rencana yang diketahui | Cara menghubungkan dan batasan | Keputusan awal |
|---|---|---|---|---|
| Identitas peserta dan relasi peserta–kunjungan | `patient_id` stabil dan ID kunjungan/klaim yang unik | PSTV01; FKP02, FKL02, PNK02 | PSTV01 berpotensi menjadi `patient_id` bila pseudonimnya konsisten lintas tabel/periode. FKP02, FKL02, dan PNK02 adalah ID kunjungan dari jenis dataset berbeda, bukan otomatis ID klaim yang saling unik. Gunakan kunci gabungan jenis sumber + ID sampai keunikan lintas sumber dibuktikan. | **Pertahankan konsep jaringan; sesuaikan adapter setelah semantik ID dikonfirmasi.** |
| Urutan/kunjungan berulang peserta | `patient_id`, diagnosis yang dapat dibandingkan, dan waktu kunjungan | PSTV01; FKP03, PNK03; FKL02/FKL24 | Tanggal mendukung urutan dan jarak pada tingkat hari bila makna kolomnya benar. FKL24 harus tetap terhubung ke kunjungan FKL02 sebagai diagnosis sekunder. Fitur berulang JALA saat ini bekerja pada baris klaim dan kode diagnosis; kunjungan bukan bukti klaim atau pembayaran berulang. | **Sesuaikan menjadi indikator kunjungan berulang; jangan menyebut repeat billing tanpa ID/status klaim dan pembayaran.** |
| Hubungan kunjungan–diagnosis | Kunci kunjungan dan kode diagnosis dengan kardinalitas yang jelas | FKL02, FKL24 | Pertahankan relasi satu kunjungan ke banyak diagnosis sekunder. Jangan langsung menggandakan baris kunjungan/klaim saat join; itu dapat menggandakan hitungan, nilai, dan skor. Pastikan peran diagnosis utama dan sekunder dibedakan. | **Dapat dipetakan setelah struktur tabel dan kunci dikonfirmasi; belum cocok langsung ke satu kolom `icd`.** |
| Hubungan peserta–keluarga | ID peserta dan ID keluarga yang valid | PSTV01, PSTV02 | PSTV02 dapat membentuk relasi keluarga bila satu nomor keluarga mengelompokkan peserta secara konsisten. JALA belum memakai hubungan keluarga. Hubungan keluarga sendiri bukan sinyal fraud dan tidak boleh menaikkan skor tanpa dasar lain yang tervalidasi. | **Tunda sebagai sinyal risiko; boleh dipertimbangkan sebagai konteks jaringan non-skoring.** |
| Bobot sampel | Bobot dan dokumentasi desain sampel | PSTV15 | Bobot sampel tidak sama dengan skor risiko. Jangan masukkan sebagai fitur fraud. Penggunaan untuk metrik populasi memerlukan kejelasan tentang rancangan sampel dan estimand. | **Pisahkan dari model; belum digunakan sampai tujuan statistiknya ditetapkan.** |
| Konkurensi dokter lintas faskes dan graf faskes–dokter | ID dokter, ID faskes pada tiap kunjungan, waktu layanan dengan ketelitian menit, afiliasi dokter–faskes | Belum terkonfirmasi pada variabel yang disebut | ID kunjungan bukan ID faskes atau dokter. Fitur JALA memerlukan pencocokan dokter yang stabil, waktu layanan, serta tabel afiliasi. | **Belum dapat dipastikan; jangan aktifkan pada dataset rencana sebelum kolom dan ketelitiannya dikonfirmasi.** |
| Lonjakan pengajuan serentak | ID faskes dan waktu pengajuan dengan ketelitian detik | Belum terkonfirmasi pada variabel yang disebut | Tanggal kunjungan bukan waktu pengajuan (`submit_ts`). Tanggal saja tidak mendukung jendela ±60 detik yang dipakai fitur JALA. | **Belum terkonfirmasi; jangan membuat jam buatan atau menyimpulkan pengajuan serentak.** |
| Rujukan internal/afiliasi dokter | Faskes dan dokter perujuk/tujuan serta tabel afiliasi | Belum terkonfirmasi pada variabel yang disebut | ID FKTP/FKRTL atau ID kunjungan saja belum membuktikan tersedia hubungan rujukan atau afiliasi praktik dokter. | **Belum terkonfirmasi; tunda fitur rujukan berbasis afiliasi.** |
| Anomali tarif dan normalisasi fasilitas | Nilai klaim, plafon tarif, ID faskes, jenis faskes, kapasitas/volume | Belum terkonfirmasi pada variabel yang disebut | JALA memerlukan `tarif`, referensi plafon, serta atribut faskes untuk fitur rasio tarif/volume. Bobot sampel PSTV15 bukan pengganti variabel tersebut. | **Belum terkonfirmasi; tidak dihitung dari variabel yang diketahui.** |
| Prioritas model dan evaluasi | Baris klaim/kunjungan yang bebas duplikasi, label evaluasi terpisah, cutoff dan protokol yang terdokumentasi | Variabel di atas; label terverifikasi belum disebut | Label sintetis JALA hanya untuk evaluasi generatornya. Tanpa label hasil verifikasi yang sah, data rencana dapat menguji alur/indikator, tetapi tidak membuktikan akurasi fraud. | **Pertahankan model JALA saat ini sebagai baseline; evaluasi ulang hanya setelah unit analisis dan label yang sesuai tersedia.** |

#### Keputusan yang bisa diambil sekarang

- Pertahankan JALA sebagai prototipe analisis jaringan dan alat pemeringkatan pemeriksaan. Matriks ini tidak mengubah model,
  graf, fitur, atau dashboard.
- Siapkan adapter hanya setelah unit setiap baris, kunci primer/asing, arti kode, dan ketelitian tanggal dikonfirmasi.
- Untuk data yang diketahui saat ini, relasi peserta–kunjungan–diagnosis adalah arah eksplorasi yang masuk akal, bukan bukti bahwa
  graf faskes–dokter JALA sudah didukung.
- Sebelum menghitung fitur, verifikasi keunikan ID, konsistensi ID peserta lintas tabel, relasi yang tidak cocok, dan efek join
  satu-ke-banyak agar jumlah kunjungan tidak membengkak.
- Pertahankan implementasi sintetis saat ini sebagai baseline yang tidak diubah. Bandingkan adapter/model baru pada data dan
  protokol evaluasi yang sama; jangan menyamakan hasil sintetis dengan validasi operasional.

### Status pelaksanaan tujuh langkah

| Langkah | Status pada versi kerja ini |
|---|---|
| 1. Pemetaan data–fitur | Matriks awal ditambahkan di atas. Pemetaan masih menunggu kamus data lengkap untuk konfirmasi semantik dan relasi. |
| 2. Adapter dan kontrak | Adapter CSV, `mapping.json`, kontrak kanonis, serta jalur prediksi batch sudah tersedia. Adapter khusus nama kolom sumber belum dapat dipastikan tanpa kamus lengkap. |
| 3. Validasi data | Pemeriksaan skema, nilai kosong, duplikasi kunci, referensi, tipe numerik, dan urutan waktu sudah tersedia. Layar Data & Prediksi kini juga menampilkan kecocokan struktur fitur beserta peringatan waktu dan batas tafsir. |
| 4. Penyesuaian fitur deteksi | Ditunda sampai kolom, unit baris, hubungan, dan ketelitian waktunya dikonfirmasi. Fitur/model sintetis tidak diubah berdasarkan asumsi. |
| 5. Pelatihan dan perbandingan | Jalur batch dengan cutoff dan evaluasi kapasitas tersedia; artefak perbandingan kandidat juga tersedia. Keduanya tetap eksperimen sintetis/paket uji, bukan validasi operasional. |
| 6. Alur tampilan | Halaman Data & Prediksi menampilkan status kecocokan struktur; prediksi dapat diteruskan ke antrean tinjauan dan ekspor bukti. |
| 7. Pengujian | Tes adapter, kualitas data, prediksi batch, penyimpanan, dan render halaman terkait dijalankan. Hasil validasi perubahan ini dicatat pada laporan tugas, bukan dianggap sebagai bukti akurasi lapangan. |

### Lembar kerja konfirmasi sumber — 21 Oktober 2026

Sumber awal: gambar kamus variabel yang diberikan pengguna dalam percakapan. Belum tersedia kamus lengkap,
versi/tahun publikasi sumber, atau file data untuk menguji nilai dan keunikannya. Definisi di bawah merupakan
transkripsi/ringkasan gambar, bukan konfirmasi skema operasional maupun hasil pemeriksaan dataset.

Gunakan empat status dukungan fitur:

- **Didukung:** seluruh kebutuhan fitur dikonfirmasi dalam dokumentasi sumber dan lolos pemeriksaan data.
- **Perlu penyesuaian:** konsep tersedia, tetapi unit, struktur, atau ketelitiannya berbeda.
- **Tidak tersedia:** ketidaktersediaan dikonfirmasi oleh sumber; fitur terkait tidak dijalankan.
- **Belum terkonfirmasi:** bukti belum cukup. Kolom yang tidak terlihat pada gambar masuk status ini, bukan otomatis tidak tersedia.

Keberadaan nama variabel pada gambar belum cukup untuk memberi status **didukung** pada fitur model.

#### Inventaris variabel yang terlihat

| Variabel | Tabel pada gambar | Arti yang terlihat | Konfirmasi yang diperlukan / keputusan sementara |
|---|---|---|---|
| PSTV01 | Peserta, FKTP, FKRTL, FKTP Non Kapitasi | Nomor peserta yang telah dideidentifikasi | Periksa stabilitas lintas tabel dan tahun; simpan sebagai teks agar nol awal tidak hilang. Kandidat penghubung peserta. |
| PSTV02 | Peserta, FKTP, FKRTL, FKTP Non Kapitasi | Nomor keluarga | Periksa apakah keanggotaan berubah menurut waktu. Konteks hubungan, bukan sinyal fraud tersendiri. |
| PSTV15 | Peserta, FKTP, FKRTL, FKTP Non Kapitasi | Bobot sampel | Perlu desain sampel dan unit pembobotan. Jangan menjumlahkan bobot peserta berulang pada setiap kunjungan untuk menghitung jumlah peserta. |
| PSTV16 | Peserta | Tahun sampel | Belum tentu tahun pelayanan; jangan langsung dijadikan cutoff prediksi. Periksa cakupan tiap ekstraksi. |
| PSTV17 | Peserta | Status kepesertaan per 31 Desember 2021 menurut gambar | Status snapshot bukan otomatis status pada tanggal kunjungan. Jangan menerapkannya ke seluruh periode tanpa riwayat status. |
| PSTV18 | Peserta | Tahun meninggal | Ketelitian tahun tidak menentukan urutan kematian dan layanan pada tahun yang sama. Makna kosong dan validitas pencatatan perlu dikonfirmasi. Tidak dipakai sebagai sinyal risiko baru pada tahap ini. |
| FKP02 | FKTP, FKRTL | ID kunjungan FKTP; pada FKRTL disebut sebagai penghubung ke FKTP | Kandidat kunci relasi, bukan ID faskes. Periksa keunikan pada tabel induk, nilai kosong, dan banyaknya FKRTL untuk satu FKP02. |
| FKP03 | FKTP | Tanggal datang kunjungan FKTP | Periksa format, ketelitian, rentang dan nilai kosong. Belum mendukung jendela menit/detik. |
| FKL02 | FKRTL, FKRTL Diagnosis Sekunder | ID kunjungan FKRTL | Kandidat kunci kunjungan; boleh muncul berulang pada diagnosis sekunder. Bukan otomatis ID klaim atau bukti pembayaran. |
| PNK02 | FKTP Non Kapitasi | ID kunjungan | Periksa cakupan keunikan per sumber/periode dan kemungkinan tumpang tindih dengan FKTP; jangan menganggap dua tabel pasti berisi layanan berbeda. |
| PNK03 | FKTP Non Kapitasi | Tanggal kunjungan | Ketelitian dan semantik perlu diperiksa seperti FKP03. |
| FKL24 | FKRTL Diagnosis Sekunder | Kode diagnosis ICD-10, 3–5 digit menurut gambar | Pertahankan peran sekunder; periksa format dan pengulangan pasangan kunjungan–diagnosis. Jangan mengganti diagnosis utama dengan kolom ini. |

#### Unit baris dan pemeriksaan relasi

Unit berikut masih merupakan hipotesis kerja dari gambar. Simpan tabel sumber terpisah sampai kardinalitas terbukti.

| Tabel / hubungan | Hipotesis unit atau kardinalitas | Pemeriksaan sebelum dipakai |
|---|---|---|
| Peserta | Satu peserta per snapshot/sampel; keunikan PSTV01 global belum terbukti | Hitung duplikasi PSTV01 dalam dan lintas PSTV16; jangan menetapkan kunci gabungan sebelum makna tahun/snapshot jelas. |
| FKTP | Satu kunjungan dengan FKP02 | Hitung baris, ID unik, duplikasi identik dan konflik atribut untuk ID yang sama. |
| FKRTL | Satu kunjungan dengan FKL02; dapat merujuk FKP02 | Ukur jumlah FKRTL per FKP02, relasi tidak cocok, dan konsistensi PSTV01 pada kedua sisi. Relasi ini belum membuktikan alasan klinis rujukan. |
| FKTP Non Kapitasi | Satu kunjungan dengan PNK02 | Periksa keunikan dan kemungkinan layanan yang sama tercatat juga pada FKTP sebelum menggabungkan hitungan. |
| FKRTL Diagnosis Sekunder | Satu catatan diagnosis sekunder per kunjungan; kunci pastinya belum diketahui | Ukur banyaknya diagnosis per FKL02 dan duplikasi pasangan FKL02–FKL24; jangan menghapus baris sebelum mengetahui alasan pengulangannya. |
| Peserta → pelayanan | Satu peserta dapat mempunyai banyak kunjungan | Hitung ID peserta tanpa pasangan dan konflik snapshot. Jangan memakai inner join yang diam-diam membuang kunjungan. |
| FKRTL → diagnosis sekunder | Satu kunjungan dapat memiliki banyak diagnosis | Simpan tabel anak atau agregasikan diagnosis sebagai himpunan terpisah; jumlah kunjungan unik dan total biaya, bila tersedia, harus tetap sama setelah pengayaan. |

Laporan pemeriksaan harus mencatat jumlah baris dan ID unik sebelum/sesudah join, tingkat kecocokan,
konflik atribut, serta jumlah record yang dikarantina beserta alasannya. Nol diagnosis sekunder tidak otomatis
berarti kunjungan invalid. Jangan menganggap ID kunjungan berulang di tabel diagnosis sebagai repeat billing.

#### Syarat melanjutkan ke adapter sumber

1. Cantumkan dokumen sumber, versi, cakupan periode, definisi unit baris, kode nilai kosong dan kunci tiap tabel.
2. Konfirmasi relasi FKP02/FKL02 serta konsistensi PSTV01, termasuk apakah diperlukan pembeda periode/sumber.
3. Konfirmasi tanggal layanan FKRTL, diagnosis utama, dokter, faskes, waktu pengajuan, tarif dan status pembayaran:
   tandai belum terkonfirmasi atau tidak tersedia sesuai bukti, bukan isi dengan nilai buatan.
4. Tetapkan unit keluaran adapter: kunjungan atau klaim. Adapter kunjungan tidak boleh diam-diam disebut adapter klaim.
5. Tulis contoh input/output sintetis berdasarkan skema yang sudah dikonfirmasi beserta ekspektasi join dan penolakan.
6. Rekam baseline kode, konfigurasi, versi dependensi dan hasil evaluasi sebelum perubahan model. Checkout yang memiliki
   perubahan lokal tidak dapat diidentifikasi hanya dengan commit HEAD; perlu snapshot kode atau manifest hash berkas.
7. Tetapkan pembanding, cutoff, kapasitas pemeriksaan, dan ukuran keberhasilan sebelum eksperimen. Tes adapter dan
   kualitas data dikerjakan bersama implementasinya, bukan ditunda sampai seluruh tahapan selesai.

**Status pekerjaan ini:** inventaris dan kriteria verifikasi diperluas dari gambar; belum ada pemetaan sumber
yang disahkan, adapter khusus baru, pelatihan ulang, atau perubahan dashboard dalam pembaruan dokumentasi ini.
Hasil tes dari audit 20 Oktober merupakan hasil historis, bukan hasil otomatis untuk checkout terbaru.

## 3. Yang tidak ada di data sintetis dan bisa ditanyakan juri

Kolom berikut **tidak ada** di data sintetis. Contoh nyata: layar JALA tidak menampilkan nomor SEP atau kode INA-CBG
karena datanya memang tidak punya kolom itu.

| Yang tidak ada | Akibatnya pada JALA |
|---|---|
| Nomor SEP, kode INA-CBG, jenis pelayanan (rawat jalan atau inap), tanggal masuk dan pulang, kelas rawat | Modus rawat inap (prolonged length of stay, readmisi, manipulasi kelas perawatan) belum bisa disentuh |
| Status verifikasi atau pembayaran klaim | Unsur "sudah dibayarkan" pada repeat billing (modus 11) belum dimodelkan |
| Kapabilitas atau kelengkapan faskes | Unsur "tanpa alasan keterbatasan fasilitas" pada self-referral (modus 10) tidak bisa dinilai; hanya afiliasi dokter yang dilihat |
| Kode tindakan, obat, dan alkes | Modus upcoding, unbundling, dan inflated bills belum bisa disentuh |
| Tabel plafon tarif resmi | JALA memakai plafon fiktif per ICD (`core/synthetic.py`); tarif terhadap plafon perlu tabel resmi |

## 4. Risiko terbesar: ketelitian waktu

Dua fitur inti bergantung pada cap waktu yang teliti:

- **Lonjakan pengiriman serentak** memakai `submit_ts` pada ketelitian detik (jendela ±60 detik).
- **Konkurensi dokter** memakai `visit_ts` pada ketelitian menit (jendela ±30 menit).

Bila data nyata hanya memuat tanggal tanpa jam, kedua fitur ini tidak bisa dihitung, dan deteksi Phantom Billing akan
bergantung pada sinyal lain (peserta luar wilayah, komponen faskes yang terhubung, dokter lintas faskes). Dampaknya belum
kami ukur; ini bisa diuji dengan menurunkan ketelitian waktu di data sintetis. Karena itu pertanyaan 3 di bawah penting.

## 5. Pertanyaan untuk panitia (saat coaching)

1. Apakah panitia menyediakan dataset simulasi atau skema klaim resmi untuk dipakai?
2. Kolom apa saja yang tersedia di data klaim, dan bagaimana ID peserta, dokter, dan faskes dianonimkan?
3. Seberapa teliti cap waktunya: hanya tanggal, atau sampai jam, menit, atau detik, baik untuk waktu pelayanan maupun waktu klaim dikirim?
4. Apakah ada data rujukan (faskes dan dokter perujuk) dan data praktik atau SIP dokter?
5. Apakah ada status verifikasi atau pembayaran klaim?
6. Apakah ada data kapabilitas atau kelengkapan faskes untuk menilai alasan rujukan?
7. Apakah ada tabel plafon tarif yang boleh dipakai?

### Template permintaan konfirmasi skema

Bagian ini siap disalin ke email atau pesan coaching. Minta kamus data dan skema resmi; jangan mengisi pemetaan
berdasarkan nama kolom saja.

> Yth. Panitia,
>
> Untuk memastikan prototipe JALA sesuai dengan dataset yang boleh digunakan, mohon konfirmasi apakah tersedia
> kamus data, skema tabel, atau dataset simulasi resmi. Jika tersedia, mohon informasikan untuk setiap tabel:
> unit satu barisnya, definisi kolom dan kode nilainya, kunci unik, relasi antar-tabel, serta aturan nilai kosong.
>
> Secara khusus, kami perlu memastikan:
>
> 1. Apakah baris mewakili peserta, kunjungan, klaim, atau pengajuan; dan ID apa yang menghubungkan tabel?
> 2. Apakah ID peserta, dokter, faskes, dan kunjungan dianonimkan secara konsisten lintas tabel dan periode?
> 3. Apakah tersedia diagnosis utama/sekunder, nilai klaim, status verifikasi/pembayaran, dan data rujukan?
> 4. Apakah tersedia waktu pelayanan dan waktu pengajuan; apa format, zona waktu, dan ketelitiannya?
> 5. Apakah tersedia data praktik/afiliasi dokter, jenis/kapasitas faskes, serta referensi plafon tarif?
> 6. Apakah penggunaan dataset untuk analisis/pengujian prototipe diizinkan, dan apa batas penyimpanan atau distribusinya?
>
> Kami tidak memerlukan data identitas langsung. Mohon gunakan skema, kamus data, atau contoh sintetis/anonim yang
> diizinkan; mohon jangan mengirim data peserta yang dapat diidentifikasi melalui kanal ini. Terima kasih.

Catat jawaban sebelum membuat adapter atau mengaktifkan fitur:

| Hal yang dikonfirmasi | Jawaban / rujukan dokumen | Status (belum diminta / menunggu / terkonfirmasi / tidak tersedia) | Dampak / keputusan JALA |
|---|---|---|---|
| Kamus data dan skema tabel resmi |  | Belum diminta | Jangan menetapkan arti kolom dari namanya saja. |
| Unit baris, kunci unik, dan relasi tabel |  | Belum diminta | Tentukan unit analisis dan cegah duplikasi akibat join. |
| Konsistensi ID anonim lintas tabel/periode |  | Belum diminta | Tanpa ID stabil, jangan membangun relasi lintas kunjungan. |
| Diagnosis utama/sekunder dan kode nilai |  | Belum diminta | Petakan diagnosis setelah kardinalitas dan maknanya jelas. |
| Nilai klaim, status verifikasi/pembayaran, dan plafon |  | Belum diminta | Jangan mengklaim repeat billing atau anomali tarif tanpa data pendukung. |
| Waktu pelayanan/pengajuan, zona waktu, dan presisi |  | Belum diminta | Nonaktifkan interpretasi fitur waktu yang melampaui presisi sumber. |
| Rujukan, afiliasi dokter, dan atribut faskes |  | Belum diminta | Jangan menyimpulkan jaringan rujukan/afiliasi dari ID kunjungan. |
| Izin penggunaan, retensi, dan distribusi data |  | Belum diminta | Gunakan hanya data serta cara pemrosesan yang secara eksplisit diizinkan. |

Setelah jawaban diterima, lampirkan sumber dan tanggal konfirmasi pada tabel ini. Tandai sebagai **terkonfirmasi**
hanya jika didukung kamus/skema atau jawaban tertulis; jika tidak tersedia, catat sebagai keterbatasan dan jangan
mengarang nilai pengganti. Data identitas langsung tetap tidak boleh dimasukkan ke repo.
