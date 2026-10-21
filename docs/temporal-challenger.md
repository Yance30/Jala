# Kandidat machine learning temporal

Model utama tetap **fitur graf + HistGradientBoostingClassifier**. Louvain mengelompokkan graf kasus; tidak ada GNN/HAN pada perubahan ini.

Kandidat `batch-gbm-temporal-v1` menambah fitur episode peserta–diagnosis selama 7 dan 30 hari, kunjungan lintas faskes, kemiripan nilai klaim, jeda/cadence layanan, proporsi tujuan rujukan, jumlah peserta rujukan, volume perujuk, dan konsentrasi tujuan. Indikator ini membantu triase, tetapi tidak membuktikan pembayaran ganda atau ketidaktepatan klinis rujukan.

Fitur episode hanya membaca layanan yang waktunya lebih awal. Fitur rujukan membaca snapshot batch yang telah ditutup, seperti baseline. Ini belum prediksi streaming. Penjelasan tambahan berupa indikator terukur, bukan atribusi model atau sebab-akibat.

## Protokol sebelum melihat hasil

- Cutoff pelatihan: hari ke-45, 60, dan 75 sejak 1 Juli 2026.
- Data pengembangan tambahan: generator skenario terpisah, seed 101 dan 211, dimulai 1 Juli, dengan entitas berbeda.
- Holdout baru: seed 809 dan 811, dimulai 5 Oktober. Seed evaluasi lama 31/47/59 tidak dipakai untuk tuning atau pengujian kandidat.
- Tiga model: `original` (data latih lama, fitur dasar), `expanded_base` (data latih diperluas, fitur dasar), dan `temporal` (data latih diperluas, fitur tambahan). Model kedua memisahkan manfaat tambahan data dari manfaat tambahan fitur.
- Parameter GBM tetap: depth 4, learning rate 0,08, 150 iterasi, balanced class weight. Tidak dilakukan pencarian parameter pada holdout.
- Kapasitas tinjauan 100 dan 300 klaim, dengan expected hits untuk skor seri. Laporan menyertakan hasil per skenario dan klaim sah yang ikut masuk antrean.
- Gerbang eksperimen: rata-rata precision@100 kandidat harus lebih tinggi dari `expanded_base`, tanpa penurunan pada pasangan cutoff/seed mana pun, dan tanpa kenaikan salah tinjau@300 pada pasangan mana pun. Lolos gerbang tidak otomatis mengganti default.

Pengembangan dan holdout menggunakan **template skenario yang sama dengan seed dan entitas berbeda**, sehingga belum membuktikan generalisasi ke keluarga fraud yang benar-benar baru. Tabel referensi dianggap statis; label historis diasumsikan tersedia saat cutoff. Jangan menyebut hasil sebagai validasi operasional atau klinis.

## Hasil eksperimen 19 Oktober 2026

Artefak lengkap: [model-comparison.json](model-comparison.json). Angka berikut adalah rata-rata enam pasangan cutoff/seed, bukan hasil data operasional.

| Model | ROC-AUC | Average precision | Precision@100 | Recall@100 | Klaim sah dalam 300 teratas |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline, data latih awal | 0,9001 | 0,6679 | 81,21% | 40,60% | 139,67 |
| Baseline, data latih diperluas | 0,9879 | 0,9140 | 99,33% | 49,67% | 117,89 |
| Kandidat temporal, data latih diperluas | 0,9920 | 0,9310 | 99,17% | 49,58% | 111,80 |

Kandidat **belum lolos gerbang eksperimen**: precision@100 rata-rata tidak mengungguli baseline dengan data latih yang sama. AUC/AP yang lebih tinggi dan berkurangnya klaim sah dalam antrean 300 teratas tidak cukup untuk menyatakan kandidat unggul pada semua kapasitas. Default tetap baseline; kandidat tersedia untuk eksperimen. Peningkatan terbesar pada protokol ini berasal dari tambahan data pengembangan. Data tambahan mengenalkan template skenario yang juga ada pada holdout, sehingga peningkatan tidak boleh disebut generalisasi ke pola fraud yang belum pernah dikenal.

Validasi perubahan: 12 tes fitur temporal dan batch serta 39 tes impor dan halaman lulus. Panel laporan juga diperiksa dengan Streamlit AppTest. Tidak ada pencarian parameter atau pengulangan tuning berdasarkan hasil holdout ini.

## Penggunaan aplikasi dan CLI

Di **About → Dataset uji eksternal: impor dan evaluasi**, pilih **Kandidat temporal: episode dan arah rujukan** pada pilihan model. Cutoff, sumber data dan kapasitas tetap dapat ditentukan. Default masih baseline.

```powershell
.\.venv\Scripts\python.exe -m core.model_comparison
```

Hasil tersimpan di `docs/model-comparison.json`. API: `batch.train(..., feature_set="temporal")` atau `run_holdout(dataset, ..., feature_set="temporal")`. Model mencatat versi dan daftar fitur; prediksi menolak model/skema yang tidak sesuai.
