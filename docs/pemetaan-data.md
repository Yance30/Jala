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
