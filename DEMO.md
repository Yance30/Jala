# Skrip Demo JALA (3 menit)

Semua angka di bawah berasal dari aplikasi pada data sintetis default (seed 2026) dan bisa dilihat di layar atau di
`docs/*.json`. Jangan mengucapkan angka yang tidak ada di sini.

**Klaim utama (satu kalimat):** *"Pemeriksaan berkas melihat satu klaim. JALA melihat jaringan yang membuat banyak klaim
tampak sah padahal terkoordinasi, dan hanya memprioritaskan; keputusan akhir tetap di verifikator."*

## Persiapan (10 menit sebelum tampil)

1. Buka aplikasi di tab sendiri dengan `?tour=0` di ujung alamat (mematikan panduan otomatis agar tidak menutupi layar).
2. Buka halaman **About** sekali sampai grafik muncul. Perhitungan awal (sekitar 10 detik) hanya terjadi pada kunjungan pertama.
3. Klik **Atur ulang umpan balik** di Risk Ranking bila sebelumnya sempat mencoba dismiss, atau muat ulang halaman.
4. Siapkan cadangan: rekaman layar alur ini, dan `streamlit run app.py` di laptop bila internet venue lemah.
5. Zoom browser 100%, tutup tab lain, mode jangan-ganggu menyala.
6. Bila perlu menunjukkan peran, pilih **Verifikator** atau **Supervisor** di sidebar. Ini hanya simulasi tampilan, bukan kontrol akses; Verifikator melihat ID peserta tersamar.

**Jika juri meminta bukti tambahan:** di **About**, geser kapasitas klaim per minggu untuk membandingkan fraud sintetis yang tertangkap JALA dan aturan. Bagian berikutnya menampilkan replay minggu deteksi cincin (setelah `python -m core.temporal_impact` dijalankan), skenario salah dismiss 10%/20%, dan tingkat false positive sintetis per tipe faskes serta wilayah. Semua angka adalah hasil simulasi, bukan bukti operasional.

**Hasil replay seed 2026 saat ini:** pada 500 klaim per minggu, JALA lebih awal pada 1 dari 8 cincin, seri pada 1, dan aturan sederhana lebih awal pada 6. Pada slider 35 klaim per minggu, jumlah fraud sintetis tertangkap sepanjang 14 minggu adalah 436 oleh JALA dan 91 oleh aturan. Artinya kapasitas antrean lebih banyak membantu menangkap klaim fraud dalam simulasi, tetapi tidak membuktikan JALA lebih cepat mendeteksi cincin.

**Bahan yang bisa ditinggalkan:** [one-pager](docs/one-pager.md), [model card](docs/model-card.md), [rencana pilot](docs/pilot-plan.md), dan [12 jawaban singkat untuk juri](docs/juri-faq.md).

**Riwayat pemeriksaan demo:** tindakan per klaster tersimpan lintas kunjungan di basis data SQLite lokal
`.jala/review_history.sqlite3`. Tombol **Reset demo** memulihkan status sesi tetapi mempertahankan audit trail.
Basis data ini dibagi oleh semua pengguna pada instance aplikasi yang sama; gunakan hanya ID dan catatan sintetis,
jangan masukkan data pribadi atau data klaim nyata. Ini penyimpanan prototipe, belum memiliki akun, pembatasan akses,
atau enkripsi untuk penggunaan operasional. Riwayat tindakan tersimpan secara persisten; umpan balik verifikator dan
perubahan skor hanya berlaku pada sesi aplikasi yang sedang berjalan.

## Alur 3 menit

| Waktu | Layar | Yang dilakukan | Yang diucapkan |
|---|---|---|---|
| 0:00-0:20 | Dashboard | Tunjuk kartu KPI | "Klaim BPJS diperiksa satu per satu. Kolusi antar-faskes tidak terlihat dari satu berkas. JALA membaca jaringan faskes, dokter, dan peserta." |
| 0:20-0:45 | Dashboard | Sorot tiga kartu dan grafik tren | "Pada data sintetis ini JALA menandai 296 klaim Phantom Billing, 244 Repeat Billing, dan 101 Self-Referral." |
| 0:45-1:05 | Risk Ranking | Klik *Risk Ranking* di sidebar, tunjuk baris teratas **Jejaring Klinik Pratama 31 (+2 faskes)** (JALA-F031) | "Klaster diurutkan menurut skor jaringan. Teratas: tiga klinik, 120 klaim, skor 100%." |
| 1:05-1:35 | Network Graph | Klik *Lihat Sub-Graph*, tunjuk dokter dan peserta | "Inilah yang tidak terlihat dari satu berkas: dokter yang sama menagih di tiga klinik dalam setengah jam, dan peserta dari luar wilayah." |
| 1:35-1:55 | Claim Details | Klik *Risk Ranking* di sidebar, lalu *Buka Claim Details*; baca tiga bukti terukur | "Alasannya bukan kotak hitam: 98% peserta luar wilayah, 77% dikirim serentak, 77% dokter lintas faskes." |
| 1:55-2:20 | Audit Action | Klik *Tindak lanjut: Audit Action*, gulir ke *Bagaimana kalau dokter ini dikeluarkan?* | "Kami simulasikan mengeluarkan dokter satu per satu. Tidak ada satu dokter pun yang jadi titik tunggal; yang terbesar hanya terkait 38% klaim. Cincin ini berlapis, jadi yang tepat adalah pemeriksaan lapangan ke tiga faskes, bukan satu orang." |
| 2:20-2:40 | Audit Action | Klik *Berkas Bukti Klaster (.zip)* | "Satu klik menghasilkan berkas untuk pemeriksa dokumen: klaim terkait, alasan, dan gambar jaringan. JALA menyaring di depan, pemeriksa dokumen memeriksa berkasnya." |
| 2:40-3:00 | About | Tunjuk kartu AUC dan grafik kapasitas audit, lalu kotak Batasan | "Pada data sintetis berlabel, AUC 0,996 dibanding 0,551 untuk aturan per klaim. Bila hanya 500 klaim yang bisa diperiksa, JALA menangkap 65% fraud, aturan lama 12,5%. Ini bukan akurasi di data BPJS nyata; batasannya tertulis di sini." |

## Tambahan jika ada waktu 30 detik: verifikator mengoreksi sistem

| Layar | Yang dilakukan | Yang diucapkan |
|---|---|---|
| Risk Ranking | Di kotak *Pilih klaster* (bawah tabel), klik kotaknya, ketik **RS Tipe C 50**, lalu klik pilihan *Jejaring RS Tipe C 50 (+1 faskes)* (JALA-F006) yang muncul, klik *Buka Claim Details*, lalu *Tindak lanjut: Audit Action* | "Klaster ini tertandai karena klaim berulang tiap sekitar 46 jam. Di berkas bukti, mayoritas klaimnya (57%) berdiagnosis hemodialisis (N18.6), yang memang berjadwal; ini pola wajar, bukan fraud." |
| Audit Action | Klik *Arsipkan & Turunkan Skor* | "Verifikator men-dismiss. Skor turun 99% menjadi 40%, dan klaster berpola dialisis serupa, *Jejaring Klinik Pratama 44* (JALA-F044), ikut turun dari 96% menjadi 73%. Ini kalibrasi ringan, belum melatih ulang model." |
| Risk Ranking | Tunjuk spanduk umpan balik | "Peringkat berubah di layar, dan bisa dibatalkan." |

Pada simulasi, bila verifikator meninjau antrean dari atas dan men-dismiss klaster yang sebenarnya tidak berisi fraud,
presisi antrean Auto-Flagged naik dari 73% menjadi 89% lalu 100%, tanpa satu pun klaster fraud sungguhan ikut turun
(`python -m core.feedback`).

## Skenario kerja dan dampak yang belum diukur

Gunakan kasus **Jejaring Klinik Pratama 31** sebagai contoh realistis, dengan seluruh identitas dan transaksi tetap
sintetis. Petugas mulai dari antrean, membuka hubungan dokter–faskes dan peserta lintas wilayah, lalu memeriksa alasan
per klaim dan mengunduh berkas sumber. Setelah itu petugas mencatat apakah pola perlu pemeriksaan lapangan atau dapat
dijelaskan sebagai layanan wajar. Kasus dialisis JALA-F006 menjadi pembanding penting: pola klaim berulang terlihat
mencurigakan secara statistik, tetapi jadwal terapi yang sah dapat menjelaskannya.

Demo ini menunjukkan **pengurutan dan pengumpulan konteks**, bukan penghematan waktu yang sudah terbukti. Belum ada
uji waktu dengan verifikator atau data operasional. Untuk mengukur dampak pada pilot, bandingkan waktu median dari
mulai membuka satu kasus sampai rekomendasi awal pada dua kondisi: pemeriksaan berkas biasa dan alur JALA. Gunakan
kasus yang sama, beberapa petugas, catat keputusan yang berubah setelah bukti dibuka, dan laporkan jumlah kasus,
median serta rentang waktu, dan tingkat kesepakatan. Jangan menyebut penghematan sebagai hasil sampai pengukuran itu
dilakukan.

## Jawaban untuk pertanyaan juri

**1. Data sintetis, bagaimana buktinya di dunia nyata?**
Belum terbukti, dan kami tidak mengklaimnya. Yang kami buktikan: logika deteksi bekerja pada pola yang didefinisikan, divalidasi
silang per kelompok faskes, dengan kasus sah yang sengaja mirip fraud (dialisis, bencana, batch RS). Fitur per-klaim saja AUC 0,80;
dengan agregat entitas 0,99, jadi jaringan memang menambah nilai. Model yang dilatih di satu dunia sintetis diuji di dunia lain
dengan AUC 0,995 (`docs/robustness.json`). Langkah berikutnya: pilot di data klaim nyata dengan persetujuan.

**2. Apa bedanya dengan pemeriksaan berkas seperti Pramana?**
Keduanya saling melengkapi. Pemeriksaan berkas menilai keaslian satu dokumen; JALA melihat hubungan antar-aktor yang tidak
terlihat dari satu dokumen. JALA menyaring di depan lalu menyerahkan berkas bukti ke pemeriksa dokumen.

**3. Bagaimana dengan RS besar yang otomatis jadi pusat jaringan?**
Fitur dinormalisasi terhadap faskes sejenis, dan data sengaja memuat RS dengan batch malam serta klinik dialisis. Dua klaster
dialisis dan satu klaster kunjungan ulang UGD memang tertandai salah; itu sebabnya ada alur dismiss.

**4. Kalau salah menandai, siapa yang bertanggung jawab?**
Verifikator. JALA hanya memberi prioritas, setiap klaster punya alasan terukur, dan keputusan tercatat di audit trail serta berkas bukti.

**5. Kenapa bukan GNN penuh?**
Fitur graf dan gradient boosting bisa diukur dan dijelaskan per klaim hari ini. HAN adalah arsitektur target; belum diimplementasikan.

**6. Datanya aslinya apa? Apakah ada nomor SEP atau kode INA-CBG?**
Tidak ada di data sintetis kami, dan layar tidak menampilkannya. Skema resmi data klaim tidak kami ketahui, jadi kami menulis
kontrak data minimal (`core/contract.py`) dan pemetaan konsep di `docs/pemetaan-data.md`, lengkap dengan kolom yang belum ada dan
tujuh pertanyaan untuk panitia. Risiko terbesarnya ketelitian waktu: dua fitur inti butuh jam, bukan hanya tanggal.

**7. Apakah JALA membekukan pembayaran atau terhubung ke sistem BPJS?**
Tidak. Freeze dan audit lapangan adalah simulasi alur, ditandai begitu di layar. JALA berposisi sebagai alat prioritas
pemeriksaan: setiap modus punya batas pembuktian yang tertulis (misalnya status pembayaran dan kapabilitas faskes tidak ada di data).

**8. Apakah umpan balik verifikator melatih ulang model?**
Belum. Dismiss menurunkan skor klaster dan klaster berpola serupa dengan aturan transparan (kalibrasi ringan), hanya pada sesi berjalan.
Bila dismiss keliru pada klaster fraud, klaster serupanya ikut turun tetapi tetap terlihat dan bisa dibatalkan.

## Jangan klaim

- "Mendeteksi fraud BPJS" tanpa embel-embel *pada data sintetis*.
- "Menggunakan GNN/HAN"; yang diukur adalah fitur graf + gradient boosting.
- "Sistem belajar dari verifikator" tanpa menyebut ini kalibrasi ringan.
- JALA "menangguhkan pembayaran", "memblokir klaim", atau "terhubung ke sistem BPJS": freeze adalah simulasi.
- Bahwa data punya nomor SEP, kode INA-CBG, atau status pembayaran: tidak ada.
- Angka penghematan rupiah: nilai klaim di data ini sintetis.
- Nomor pasal atau modus di regulasi, kecuali sudah dicek langsung dari dokumennya.

## Sebelum naik panggung

- [ ] URL dengan `?tour=0` terbuka, About sudah pernah dimuat.
- [ ] Umpan balik diatur ulang (tidak ada spanduk di Risk Ranking).
- [ ] Rekaman cadangan dan laptop lokal siap.
- [ ] Angka 296 / 244 / 101, AUC 0,996 vs 0,551, dan 65% vs 12,5% cocok dengan layar.
