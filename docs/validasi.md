# Status dan roadmap validasi JALA

Dokumen ini menjawab satu pertanyaan secara jujur: **seberapa kuat bukti di balik angka JALA, dan apa yang
belum terbukti.** Seluruh angka di bawah berasal dari artefak yang dapat direproduksi
(`docs/benchmark.json`, `docs/robustness.json`, `docs/temporal_impact.json`) pada **data 100% sintetis**.
Tidak ada data klaim atau identitas peserta nyata (sesuai guidebook Healthkathon butir 5o dan UU PDP).

Ide JALA tidak berubah di dokumen ini: analisis jaringan multi-aktor (faskes–dokter–peserta–diagnosis–waktu)
untuk **mengurutkan prioritas pemeriksaan**, dengan keputusan akhir tetap pada verifikator.

## 1. Apa yang sudah divalidasi

| Jenis validasi | Status | Di mana |
|---|---|---|
| Dunia sintetis berlabel, seed tetap, dapat direproduksi | ✅ Ada | `core/synthetic.py`, `docs/benchmark.json` |
| Validasi silang **per kelompok faskes** (cincin yang sama tidak melatih sekaligus menguji) | ✅ Ada | `core/evaluate.py` |
| Pembanding: aturan lama, Isolation Forest, acak | ✅ Ada | tabel utama README |
| Ablasi fitur (membuktikan relasi multi-entitas menambah nilai) | ✅ Ada | `docs/robustness.json`, README §Uji ketahanan |
| Transfer ke dunia bergeser (latih di A, uji di B tanpa latih ulang) | ✅ Ada | `docs/robustness.json` |
| Fraud yang sengaja menghindar (uji penurunan kinerja) | ✅ Ada | `docs/robustness.json` |
| Analisis false positive (klaim sah yang ikut tertandai) | ✅ Ada | `docs/robustness.json`, layar About |
| Replay temporal ketat (model hanya dilatih dari minggu yang sudah lewat) | ✅ Ada | `core/temporal_impact.py`, `docs/temporal_impact.json` |
| Penanda "kemungkinan penjelasan sah" per klaster (tekan false positive) | ✅ Ada | `core/live.benign_explanations`, layar Claim Details & Audit Action |

## 2. Apa yang belum ada — dan mengapa

- **Data klaim BPJS nyata.** Dilarang oleh guidebook (butir 5o: wajib data dummy/anonim). Angka JALA mengukur
  apakah logika deteksi bekerja pada pola yang **didefinisikan generator**, bukan akurasi di lapangan.
- **Skenario dari keluarga generator independen.** Dunia utama, dunia bergeser (transfer), dan skenario
  "fraud menghindar" masih dibuat oleh keluarga pembangkit yang sama. Yang diuji adalah pergeseran
  **parameter**, bukan pola fraud yang benar-benar baru.
- **Evaluasi pakar domain / verifikator nyata.** Belum ada; penilaian false positive saat ini terhadap label
  sintetis, bukan pertimbangan klinis manusia.
- **Model HAN/GNN.** Arsitektur target, **belum diimplementasikan**. Mesin yang diukur sekarang:
  fitur graf + gradient boosting. Jangan menyajikan metrik saat ini sebagai hasil HAN.

## 3. Contoh cerita dampak operasional (untuk juri)

Skenario: verifikator hanya punya kapasitas memeriksa **500 klaim** dari 17.431 klaim sintetis
(753 fraud, prevalensi 4,3%). Berapa yang tertangkap, dan berapa klaim sah yang ikut terperiksa?

| Pemberi skor | Fraud tertangkap di 500 teratas | Klaim sah yang ikut terperiksa |
|---|---|---|
| Acak | ~22 (2,9%) | ~478 |
| Aturan lama (asumsi proyek) | ~95 (12,5%) | ~405 |
| Isolation Forest | ~331 (44,0%) | ~169 |
| **JALA (fitur graf + GBM)** | **~490 (65,1%)** | **~10 (presisi 98%)** |

Artinya pada simulasi ini JALA menangkap ~5× lebih banyak fraud daripada aturan lama pada kapasitas yang sama,
dengan hampir tidak membebani faskes sah. **Baca batasnya:** prevalensi 4,3% ditentukan generator, dan
precision@k bergantung padanya (recall@k lebih tahan). Ini **bukan** penghematan rupiah/waktu yang terukur;
ROI hanya boleh disajikan sebagai skenario asumsi sampai ada pengukuran operasional pada pilot yang disetujui.

Catatan kejujuran temporal (dari `docs/temporal_impact.json`): pada replay 14 minggu dengan kapasitas
35 klaim/minggu, JALA menangkap lebih banyak fraud sintetis daripada aturan (436 vs 91). Namun pada **waktu
tangkap pertama**, JALA lebih awal hanya pada 1 dari 8 cincin. Jadi manfaat yang klaim-able adalah **urutan
antrean**, bukan "mendeteksi cincin lebih cepat".

## 4. Roadmap memperkuat validasi eksternal

Sejalan dengan `docs/pilot-plan.md` (tiga fase, semua butuh persetujuan tata kelola):

1. **Skenario independen.** Bangun pembangkit fraud kedua yang tidak berbagi mekanisme dengan pembangkit utama
   (pola kiriman, afiliasi dokter, dan cadence klaim ulang yang berbeda), lalu uji model tanpa latih ulang.
   Ukur seberapa jauh metrik turun — ini batas kejujuran yang lebih kuat daripada transfer-parameter.
2. **Validasi temporal ketat sebagai gerbang.** Jadikan replay temporal (`core/temporal_impact.py`) evaluasi
   utama, bukan pelengkap: latih hanya dari minggu lampau, uji di minggu depan, laporkan interval
   ketidakpastian per kelompok.
3. **Tinjauan pakar domain.** Minta verifikator/klinisi menilai contoh klaster sulit (dialisis terjadwal,
   kontrol UGD, batch malam RS) dan menilai apakah penanda "kemungkinan sah" mengurangi false positive tanpa
   menyembunyikan fraud nyata.
4. **Data sah bila kelak diizinkan.** Mode bayangan pada data ter-anonimisasi yang disetujui pemilik data,
   berdampingan dengan proses resmi, tanpa mengubah pembayaran — hanya setelah gerbang privasi, keamanan,
   dan hukum terpenuhi.

## 5. Prinsip penyajian angka

- Sebut sumber tiap angka (benchmark.json vs robustness.json) dan bahwa semuanya sintetis.
- Sajikan JALA sebagai **alat prioritas pemeriksaan**, bukan pembuktian kecurangan.
- Publikasikan false positive dan hasil negatif bersama metrik deteksi.
- Jangan menyematkan hasil model saat ini pada HAN/GNN.
