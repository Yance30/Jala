# Laboratorium prediksi batch

Tinjauan kini menyediakan [graf hubungan, ringkasan kasus, dan linimasa dari batch tersimpan](batch-case-context.md), berikut unduhan bahan pemeriksaan.

Lanjutan: [uji keluarga fraud yang tidak dilatih dan alur tinjauan batch](unseen-and-review.md). Hasil prediksi kini dapat dikirim ke menu **Tinjauan batch** untuk pemeriksaan, catatan sesi, dan ekspor.

**Model utama tetap machine learning graf + gradient boosting.** Pilihan kandidat fitur temporal dan protokol perbandingan beberapa cutoff dijelaskan di [panduan kandidat temporal](temporal-challenger.md). Ini bukan implementasi GNN/HAN dan tidak mengganti default secara otomatis.

Pembaruan lanjutan: tersedia panel **Dataset uji eksternal: impor dan evaluasi** dengan tabel referensi dan tarif sendiri, serta laporan **Uji ketahanan pada skenario independen**. Lihat [panduan paket eksternal](external-datasets.md). Panel batch sintetis di bawah tetap tersedia untuk eksperimen awal. Model baru menggunakan `batch-gbm-v2`, dengan referensi tarif tersalin dan fingerprint tarif.

Buka **About → Eksperimen prediksi batch baru**, pilih periode latih dan kapasitas, lalu tekan **Latih dan evaluasi batch sintetis**. Hasil dan model berada di sesi pengguna. Unduh contoh CSV, lalu unggah melalui **Batch klaim sintetis** untuk mencoba prediksi tanpa label atau pelatihan ulang. CSV harus memakai referensi faskes, dokter, peserta, dan diagnosis yang dikenali model eksperimen; ini belum merupakan adapter skema BPJS.

Jalankan ulang eksperimen dan simpan laporan:

```powershell
.\.venv\Scripts\python.exe -m core.batch --training-days 60 --capacity 500 --json docs/batch-evaluation.json
```

Pemeriksaan dunia lama (exit code 1 bila ada temuan):

```powershell
.\.venv\Scripts\python.exe -m core.data_quality
```

API Python:

```python
from core.batch import train, predict, evaluate

# claims_history: hanya klaim yang tersedia sampai cutoff.
# labels_history: tabel terpisah, claim_id unik dan is_fraud 0/1.
model = train(claims_history, faskes, affiliations, patients,
              labels_history, cutoff="2026-08-30")
scores = predict(model, claims_new, as_of="2026-10-03")
# Outcome baru digunakan setelah prediksi, bila tersedia:
metrics = evaluate(scores, labels_new, capacity=500)
```

`predict` menolak kolom label, ID yang pernah dilatih, klaim sebelum/saat cutoff, klaim setelah `as_of`, serta input tidak valid. Referensi model disalin saat pelatihan. Pengguna API perlu mengonversi kolom waktu ke datetime; inspector tidak memperbaiki data secara diam-diam. API mendukung diagnosis dalam referensi tarif model, yang dapat diberikan melalui `train(..., tariff_caps=...)`. Tanpa parameter tersebut, eksperimen demo memakai referensi sintetis bawaan.

Batch dinilai terhadap seluruh riwayat latih dan batch saat ini. Prediksi tidak memasukkan batch ke riwayat secara otomatis; ia tidak bersifat streaming dan tidak menyimpan model ke disk. Jika ingin konteks beberapa batch setelah cutoff, kirim kumpulan klaim tersebut sebagai satu snapshot batch yang ditutup. Semua label historis diasumsikan telah tersedia pada cutoff; keterlambatan hasil audit belum disimulasikan.

Data `synthetic-chronology-v2` menggunakan opsi kronologi pengajuan yang konsisten. Benchmark dashboard lama tetap memakai dunia default lama agar artefaknya dapat direproduksi. Jangan mencampur angka kedua eksperimen. Skor 0–100 merupakan sinyal pemeringkatan, bukan probabilitas terkalibrasi; indikator dari `explain()` bukan atribusi prediksi model.
