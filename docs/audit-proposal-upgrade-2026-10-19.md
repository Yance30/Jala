# Audit proposal dan upgrade fondasi JALA — 19 Oktober 2026

## Sumber dan batas pemeriksaan

- [Google Docs yang diberikan tim](https://docs.google.com/document/d/10MHwpJiFHLhAT0zZQEK8blgHEZEOeCHUDu1G0kISMcQ/edit), dibaca melalui konektor Drive. Teks yang dikembalikan memuat proposal awal, susunan slide, Draft 1, bagian **Yang Diminta Sebelum Submit**, dan **Progress PJ01**. Jangan memperlakukan semuanya sebagai satu versi final.
- Tautan pendek Canva `https://canva.link/7hkox9wzoczxyqf` tidak dapat dibaca dengan alat web. Kesetaraan desain Canva dengan Docs belum diperiksa.
- Checkout lokal sebelum perubahan: `main`, `0418ce1`. Pemeriksaan GitHub pada sesi ini menunjukkan `main` pada `d2acd6d`; PR #1 `fix/prototype-claims-honesty` masih draft. Upgrade lokal ini belum menggabungkan PR tersebut.
- Audit mencakup keselarasan klaim dengan implementasi dan artefak evaluasi, bukan audit hukum atau verifikasi seluruh sumber statistik latar belakang. Tidak ada perubahan ke Google Docs, Canva, atau GitHub.

## Ketidaksesuaian dan redaksi pengganti

| Bagian proposal | Bukti/kesenjangan | Redaksi yang sesuai implementasi |
|---|---|---|
| Identitas; Model & Logika; Draft 1; Progress PJ01 menyebut GNN/HAN dipakai | `core/evaluate.py` memakai HistGradientBoostingClassifier. Bagian **Yang Diminta Sebelum Submit** justru sudah menyebut HAN sebagai target. | Prototipe menggunakan fitur graf dan gradient boosting; HAN/GNN merupakan eksperimen pengembangan berikutnya. |
| Draft 1 menyebut Neo4j dan ekstraksi database BPJS | Relasi dihitung dengan pandas/NetworkX; sumber dashboard `components/bench.py` adalah `generate_world()` dan `benchmark()`. | Data sintetis diolah menjadi fitur relasional dan graf; belum ada koneksi database BPJS atau Neo4j. |
| Urutan Louvain lalu classifier | `core/live.py` membentuk graf antar-faskes dari klaim yang sudah mendapat skor, kemudian menjalankan Louvain. | Skor klaim membentuk graf kasus prioritas, lalu Louvain mengelompokkan komunitas untuk ditinjau. |
| Faktor penyebab/kontribusi skor; Explainable GNN | `core/detect.explain()` memetakan indikator ke alasan dengan aturan; bukan atribusi model dan bukan sebab-akibat. | Indikator terukur dan relasi terkait membantu verifikator meninjau alasan penandaan. |
| Fitur → Masalah: 180 detik; skor 85–90% | Burst ±60 detik, konkurensi dokter ±30 menit, klaim ulang <48 jam. Skor klaster merupakan agregat prioritas. | Parameter prototipe: ±60 detik, ±30 menit, <48 jam; skor prioritas 0–100, bukan peluang fraud. |
| Manipulasi diagnosis/layanan sebagai modus yang ditangani | Generator/evaluasi mencakup phantom, repeat, self-referral; tidak ada benchmark khusus manipulasi layanan. | Analisis manipulasi diagnosis/layanan merupakan perluasan yang belum divalidasi. |
| Data sintetis **atau** anonim | Pipeline demo memakai data sintetis; tidak menunjukkan penggunaan data operasional yang dianonimkan. | Prototipe saat ini diuji pada data sintetis. |
| Pemetaan INA-CBG dan kemampuan faskes | `docs/pemetaan-data.md` menyebut INA-CBG, status pembayaran dan kapabilitas klinis belum tersedia. Nilai capacity pada generator bukan kapabilitas klinis. | Pemetaan skema resmi, tarif INA-CBG dan kapabilitas layanan memerlukan konfirmasi pemilik data. |
| Menahan pembayaran, near real-time, penghematan Rp1,5–3 triliun | Aksi hanya catatan demo. Replay sintetis tidak membuktikan manfaat waktu/uang operasional. | JALA menyusun prioritas tinjauan; dampak waktu, biaya, dan integrasi pembayaran belum diukur. |
| Seluruh akses/model/skor diaudit; RBAC/PDP | Peran UI simulatif; SQLite opsional untuk demo lokal. Masking bukan kontrol akses. | Demo memiliki riwayat tindakan; kontrol akses dan audit produksi masih perlu dikembangkan serta diuji. |
| Precision >85%, recall >80% untuk klaster | Angka klaim top-k berbeda dari ukuran klaster dan ambang 0,5. | Tetapkan unit analisis, cutoff, kapasitas, dan protokol label sebelum mengukur target pilot. |
| Seluruh model diuji berkala dan bebas bias kondisi darurat | Tersedia analisis false positive sintetis, bukan monitoring operasional atau bukti bebas bias. | Evaluasi sintetis tersedia; validasi pakar dan pemantauan operasional belum dilakukan. |

## Angka dan tata kelola

Benchmark lama `docs/benchmark.json`, seed 2026: 17.431 klaim, 753 fraud sintetis, 60 faskes. GBM: AUC **0,9965887738**, AP **0,9395760476**, precision@500 **98,0%**, recall@500 **65,073%**. AUC tiga desimal adalah **0,997**, bukan 0,996. Jangan gabungkan angka dari `robustness.json` tanpa menyebut pipeline.

Artefak benchmark yang diperiksa hanya berisi `main`, tanpa keluaran `multi_seed`; klaim stabilitas lima seed perlu artefak tersendiri. AP per-tipologi README juga perlu diselaraskan sumbernya. PR #1 memperjelas beberapa label UI, tetapi belum mengubah semua tampilan persen skor (`components/cards.py`, `core/feedback.py`) atau seluruh angka README.

Pada Progress PJ01, delapan bobot yang ditulis berjumlah 35%. Nilai tertimbang dari angka tabel adalah **1,331428…**, sehingga 1,33 konsisten secara aritmetika. Namun tabel bukti yang terbaca hanya merinci **13 baris**, sementara ringkasan mengklaim 27 parameter (12 parsial, 15 belum). Lengkapi matriks 27 butir dan metode pemberian skor. Kecocokan aritmetika tidak membuktikan status penilaian resmi. Bagian ruang lingkup sudah menyebut asesmen simulatif; pertahankan batas itu di ringkasan dan penutup. Pernyataan kerja sama yang solid perlu dibatasi karena tabel sendiri menyebut PKS belum ada.

Placeholder `[source]` dan rujukan berbentuk nomor percakapan masih ada pada draft lama. Pisahkan arsip draft dari versi pengumpulan, gunakan sumber langsung, dan jangan menyebut skenario perkalian persentase dana sebagai kerugian nasional yang terukur.

## Temuan teknis baru

1. **240 klaim pada dunia default lama diajukan sebelum waktu layanan.** Pemeriksaan `core.data_quality` menangkap ini. Untuk eksperimen baru, opsi `WorldConfig(chronological_submissions=True)` menggeser jadwal pengajuan yang tidak mungkin ke slot hari berikutnya dengan jam yang sama. Dunia lama dipertahankan agar benchmark tetap dapat direproduksi; panel kualitas menampilkan masalahnya secara terbuka.
2. **Dashboard lama adalah jalur evaluasi.** `_engine()` membangkitkan data dan memakai skor out-of-fold. Ia bukan layanan prediksi batch tanpa label. Upgrade menyediakan `train()` dan `predict()` terpisah.
3. **Benchmark utama bukan estimasi prospektif.** Fitur agregat dibangun dari seluruh dunia sebelum fold model dibagi. Ini dapat sesuai konteks analisis retrospektif, tetapi tidak mengukur apa yang tersedia pada waktu klaim baru masuk. Eksperimen baru membangun fitur pelatihan hanya dari periode historis. Pada prediksi, riwayat dan batch yang sudah ditutup merupakan snapshot teramati.
4. **Referensi tarif masih sintetis.** `ICD_CAP` adalah kamus generator, bukan tarif resmi. Prediksi baru menolak kode yang tidak memiliki referensi agar tidak diam-diam memberi skor berdasarkan nilai hilang.

## Upgrade yang diterapkan lokal

- `core/data_quality.py`: laporan kualitas berbasis hitungan, tanpa contoh ID peserta; skema, nilai kosong, kunci duplikat, referensi putus, nilai numerik, kronologi, zona waktu, dan label yang masuk ke input detektor.
- `core/batch.py`: pemisahan pelatihan historis, prediksi batch tanpa label/retraining, evaluasi terpisah; cutoff, versi model, versi scikit-learn, fingerprint data latih dan daftar fitur dicatat.
- `core/synthetic.py`: opsi kronologi v2 tanpa mengubah hasil default lama.
- About: panel kualitas, eksperimen temporal, laporan JSON, contoh CSV, dan prediksi CSV sintetis menggunakan referensi eksperimen.
- Tes mencakup penolakan kebocoran label/waktu, data invalid, CSV, prediksi tanpa fit, keselarasan label evaluasi, tie handling, serta interaksi UI laboratorium.

Eksperimen default baru tersimpan di `docs/batch-evaluation.json`: 11.465 klaim latih sampai cutoff **30 Agustus 2026 00:00**, kemudian 5.966 klaim uji termasuk 265 fraud sintetis. Pada kapasitas 500, recall **100%** dan precision **53%**; AUC sekitar **0,99973**. Ini satu holdout dari keluarga generator yang sama, dengan tabel referensi statis dan asumsi label historis sudah tersedia. Angka tidak menggantikan benchmark lama dan bukan bukti kinerja BPJS. Test batch ditutup pada pengajuan terakhir (2 Oktober); tanggal pengajuan dapat melewati periode layanan Q3.

## Urutan pengembangan berikutnya

**Pembaruan lanjutan pada hari yang sama:** adapter paket CSV/JSON, referensi tarif eksternal, pemetaan kolom, prediksi entitas baru dengan pemeriksaan konflik snapshot, dan evaluasi pembangkit terpisah sudah ditambahkan. Lihat [panduan dataset eksternal](external-datasets.md). Rata-rata AUC tiga seed pada skenario terpisah adalah 0,8242; recall@100 35,56% dan precision@100 71,11%. Karena dataset dan kapasitas berbeda, ini bukan perbandingan langsung dengan holdout v2 sebelumnya. Pembangkit terpisah bukan validasi pakar independen. Roadmap di bawah merekam rencana awal; poin adapter telah dikerjakan untuk paket uji, sementara multi-cutoff dan validasi pakar tetap diperlukan.

Validasi lokal setelah perubahan: `python -m pytest -q -m "not e2e"` menghasilkan **189 passed, 10 deselected** (252,88 detik). Tes UI memakai Streamlit AppTest; suite browser E2E tidak dijalankan. Eksperimen batch dijalankan ulang untuk menghasilkan artefak JSON, dan `git diff --check` tidak menemukan kesalahan whitespace. Perubahan belum di-commit atau di-push.

1. Adapter data uji eksternal dengan pemetaan skema, referensi tarif yang terversi dan karantina record gagal; UI saat ini hanya menerima batch yang cocok dengan referensi sintetis eksperimen.
2. Evaluasi multi-cutoff, generator independen, label dengan tanggal keputusan tersedia, interval ketidakpastian, dan ukuran per-klaster. Bandingkan biaya salah tinjau serta waktu kerja verifikator.
3. Simpan model dan snapshot referensi dalam registri tepercaya; ukur drift, latensi, throughput, dan strategi pembaruan model. Model laboratorium saat ini hanya berada dalam sesi.
4. Eksperimen atribusi model dan kalibrasi terpisah. Bedakan indikator, kontribusi prediksi, dan bukti sebab-akibat.
5. Autentikasi, otorisasi tindakan, isolasi pengguna dan audit persisten; uji sebelum menyebut siap pilot multi-pengguna.
6. HAN/GNN sebagai challenger terhadap GBM pada split, data, kapasitas dan biaya komputasi yang sama. Tidak ada jaminan model lebih kompleks akan lebih baik.

Rujukan teknis: [scikit-learn: kebocoran data](https://scikit-learn.org/stable/common_pitfalls.html), [kalibrasi](https://scikit-learn.org/stable/modules/calibration.html), [PyG HANConv](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.nn.conv.HANConv.html).
