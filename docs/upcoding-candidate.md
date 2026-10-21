# Kandidat upcoding: komposisi diagnosis dan lonjakan tarif

## Masalah yang ditutup

Baseline graf + gradient boosting tidak punya sinyal untuk upcoding yang tarifnya **masih di bawah plafon**. `f_tarif_ratio` dan aturan `rule_over_cap` hanya menyala saat tarif melewati plafon, sedangkan upcoding yang sebenarnya menagih kode diagnosis yang lebih berat dengan tarif yang tampak wajar. Yang menyimpang bukan harganya, melainkan komposisi diagnosis faskes itu dibanding rekan sejenisnya, dan riwayat peserta itu sendiri.

Dua fitur kandidat ditambahkan di `core/upcoding_features.py`, diisolasi sebagai `feature_set="upcoding"` sehingga `FEATURES` utama dan seluruh artefak benchmark yang sudah terbit tidak berubah:

| Fitur | Definisi |
| --- | --- |
| `f_icd_mix_z` | Porsi satu kode diagnosis di sebuah faskes, dinormalisasi terhadap faskes **sejenis** yang menagih kode yang sama. Mengikuti idiom `_z_by_group` yang sudah ada, dipotong pada −6 sampai 12 |
| `f_pat_tarif_jump` | Selisih relatif tarif klaim terhadap median tarif klaim peserta itu sendiri yang **berwaktu layanan lebih awal**. Baris dengan stempel waktu identik dikecualikan agar tidak bergantung urutan baris |

## Protokol

`python -m core.upcoding_evaluation`. Data latih dari generator skenario terpisah seed 101/211 (1 Juli – 85 hari, flag `upcoding=True`), cutoff 1 September 2026. Batch uji seed 1201/1213 mulai 5 Oktober: 3.115 klaim, 260 berlabel fraud. Kedua model memakai hyperparameter baseline yang sama; tidak ada penalaan pada seed uji. Skor seri dihitung dengan expected hits.

Pola yang ditanam: satu klinik menagih I50 (gagal jantung) untuk peserta yang rekamannya sendiri berupa I10 (hipertensi) rutin, 10–20 hari sebelumnya, tarif di bawah plafon. Pembanding sahnya: RS tipe C yang memang wajar menangani I50.

## Hasil

Rata-rata dua seed uji:

| Ukuran | Baseline | Kandidat upcoding |
| --- | ---: | ---: |
| Recall keluarga upcoding @50 | 0,0% | 0,0% |
| Recall keluarga upcoding @100 | 0,0% | 0,0% |
| Recall keluarga upcoding @200 | 0,0% | **100,0%** |
| Recall keluarga upcoding @300 | 21,1% | **100,0%** |
| `legit_severe` ikut tertinjau @300 | 5,0% | **0,0%** |
| Klaim rutin ikut tertinjau @300 | 4,2% | **2,2%** |
| AUC | 0,9619 | 0,9924 |
| Average precision | 0,8170 | 0,9511 |
| Precision@300 | 0,6339 | 0,7783 |

Baseline buta total pada keluarga ini di tiga kapasitas pertama. Kandidat menutupnya, dan **tidak** menyeret RS yang sah menangani gagal jantung — justru tinjauan keliru pada kasus sah itu turun dari 5,0% ke 0,0%.

Perhatikan bahwa pada kapasitas 50 dan 100 keduanya sama-sama 0%. Peringkat teratas masih dikuasai keluarga fraud lain yang skornya lebih ekstrem, jadi keuntungan kandidat baru muncul pada kapasitas 200 ke atas. Untuk auditor yang hanya sanggup memeriksa 100 klaim, kandidat ini belum memberi apa-apa.

## Batasan

Keluarga upcoding dan kedua fitur yang mendeteksinya dirancang oleh tim yang sama. Angka 100% di atas menunjukkan **lubang yang diketahui berhasil ditutup**, bukan kemampuan mendeteksi upcoding sebagaimana terjadi di lapangan.

Pola yang ditanam sempit: satu klinik, satu pasangan kode (I10 → I50), satu dokter, selang 10–20 hari. Upcoding nyata bervariasi pada pasangan kode, jenis faskes, dan kelengkapan dokumen, dan sering tidak meninggalkan jejak pada riwayat peserta yang sama.

Semua data sintetis. Belum ada validasi operasional BPJS, kajian klinis, atau penilaian verifikator atas contoh kasus. Kandidat **tidak** dipromosikan menjadi default; baseline tetap model utama sampai ada bukti pada data yang tidak dibuat oleh tim ini.

Lihat [artefak lengkap](upcoding-evaluation.json).
