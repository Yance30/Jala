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

**Riwayat pemeriksaan demo:** secara default hidup hanya pada sesi aktif. Penyimpanan persisten bersifat opsional melalui
`JALA_REVIEW_HISTORY_DB`; bila dikonfigurasi pada instance bersama, penyimpanannya juga dapat dipakai bersama dan bukan
kontrol akses. Keputusan antrean batch memiliki penyimpanan lokal terpisah. Gunakan hanya ID dan catatan sintetis;
jangan masukkan data pribadi atau data klaim nyata. Prototipe ini belum memiliki autentikasi atau perlindungan setara
layanan operasional. Umpan balik dan perubahan skor berlaku pada sesi aplikasi.

## Alur 3 menit

| Waktu | Layar | Yang dilakukan | Yang diucapkan |
|---|---|---|---|
| 0:00-0:20 | Dashboard | Tunjuk kartu KPI | "Klaim BPJS diperiksa satu per satu. Kolusi antar-faskes tidak terlihat dari satu berkas. JALA membaca jaringan faskes, dokter, dan peserta." |
| 0:20-0:45 | Dashboard | Sorot tiga kartu dan grafik tren | "Pada data sintetis yang sedang ditampilkan, JALA menandai 295 dugaan Phantom Billing, 252 dugaan Repeat Billing, dan 102 dugaan Self-Referral." |
| 0:45-1:05 | Risk Ranking | Klik *Risk Ranking* di sidebar, tunjuk klaster teratas yang tampil | "Klaster diurutkan menurut skor prioritas. Buka satu klaster dan baca jumlah faskes, klaim terkait, serta skor /100 yang ditampilkan." |
| 1:05-1:35 | Network Graph | Klik *Lihat Sub-Graph*, tunjuk hubungan yang benar-benar terlihat | "Graf membantu menelusuri hubungan antarentitas yang terkait. Hubungan ini adalah petunjuk untuk diperiksa, bukan bukti pelanggaran." |
| 1:35-1:55 | Claim Details | Buka detail klaster dan baca indikator yang tampil | "Setiap indikator ditelusuri dari catatan sintetis yang mendasarinya. Saya hanya menyebut nilai yang terlihat di layar; skor bukan probabilitas." |
| 1:55-2:20 | Audit Action | Klik *Tindak lanjut: Audit Action*, gulir ke *Bagaimana kalau dokter ini dikeluarkan?* | "Panel ini mensimulasikan dampak mengeluarkan dokter dari klaster. Baca perubahan dan proporsi klaim yang tampil; ini analisis struktur jaringan, bukan penilaian hukum atas dokter." |
| 2:20-2:40 | Audit Action | Klik *Berkas Bukti Klaster (.zip)* | "Satu klik menghasilkan berkas untuk pemeriksa dokumen: klaim terkait, alasan, dan gambar jaringan. JALA menyaring di depan, pemeriksa dokumen memeriksa berkasnya." |
| 2:40-3:00 | About | Tunjuk kartu AUC dan grafik kapasitas audit, lalu kotak Batasan | "Pada benchmark sintetis seed 2026, AUC JALA 0,997 dibanding 0,551 untuk aturan sederhana; di kapasitas 500, recall masing-masing 65,1% dan 12,5%. Ini hasil sintetis, bukan akurasi pada data BPJS nyata." |

## Tambahan jika ada waktu 30 detik: verifikator mengoreksi sistem

| Layar | Yang dilakukan | Yang diucapkan |
|---|---|---|
| Dashboard | Klik **Buka kasus pembanding**, lalu periksa detail dan indikator yang tampil | "Kasus pembanding memperlihatkan pola berulang yang dapat memiliki penjelasan layanan wajar, seperti terapi terjadwal. Karena itu, pola dan skor tetap perlu ditinjau bersama konteks dan dokumen." |
| Audit Action | Pilih hasil tinjauan yang sesuai dan simpan catatan | "Keputusan dan alasan pemeriksa dicatat. Bila memilih pola wajar, kalibrasi demo dapat mengubah prioritas klaster serupa; perubahan yang tampil bukan pelatihan ulang model." |
| Risk Ranking | Tunjuk spanduk umpan balik | "Peringkat berubah di layar, dan bisa dibatalkan." |

Pada simulasi, bila verifikator meninjau antrean dari atas dan men-dismiss klaster yang sebenarnya tidak berisi fraud,
presisi antrean Auto-Flagged naik dari 73% menjadi 89% lalu 100%, tanpa satu pun klaster fraud sungguhan ikut turun
(`python -m core.feedback`).

## Skenario kerja dan dampak yang belum diukur

Gunakan klaster teratas yang tampil sebagai contoh, dengan seluruh identitas dan transaksi tetap sintetis. Petugas
mulai dari antrean, membuka hubungan yang ditampilkan, lalu memeriksa indikator per klaim dan mengunduh berkas bukti.
Gunakan tombol kasus pembanding untuk melihat pola layanan yang dapat memiliki penjelasan wajar, seperti terapi
terjadwal. Catat apakah kasus perlu diperiksa lebih lanjut atau memiliki konteks yang menjelaskannya.

Demo ini menunjukkan **pengurutan dan pengumpulan konteks**, bukan penghematan waktu yang sudah terbukti. Belum ada
uji waktu dengan verifikator atau data operasional. Untuk mengukur dampak pada pilot, bandingkan waktu median dari
mulai membuka satu kasus sampai rekomendasi awal pada dua kondisi: pemeriksaan berkas biasa dan alur JALA. Gunakan
kasus yang sama, beberapa petugas, catat keputusan yang berubah setelah bukti dibuka, dan laporkan jumlah kasus,
median serta rentang waktu, dan tingkat kesepakatan. Jangan menyebut penghematan sebagai hasil sampai pengukuran itu
dilakukan.

## Jawaban untuk pertanyaan juri

**1. Data sintetis, bagaimana buktinya di dunia nyata?**
Belum terbukti, dan kami tidak mengklaimnya. Yang kami buktikan: logika deteksi bekerja pada pola yang didefinisikan, divalidasi
silang per kelompok faskes, dengan kasus sah yang sengaja mirip fraud (dialisis, bencana, batch RS). Pada ablasi sintetis,
fitur per-klaim menghasilkan AUC 0,802, agregat entitas 0,992, dan JALA penuh 0,996. Ini mendukung nilai tambah informasi
entitas dan relasi pada generator ini, bukan bukti lapangan. Transfer ke dunia B dengan parameter bergeser menghasilkan AUC
0,995, tetapi dunia tersebut masih dari keluarga pembangkit yang sama. Pada skenario pembangkit terpisah, rata-rata AUC
0,824 dan recall@100 35,56% (`docs/independent-evaluation.json`), yang menunjukkan batas generalisasi. Langkah berikutnya:
validasi data dan pilot hanya dengan persetujuan tata kelola.

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
- [ ] Angka 295 / 252 / 102, AUC benchmark 0,997 vs 0,551, dan recall@500 65,1% vs 12,5% cocok dengan artefak yang disebut.
