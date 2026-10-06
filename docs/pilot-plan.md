# Rencana pilot JALA tiga fase

Semua fase memerlukan persetujuan tata kelola dan penggunaan data yang sah. Sistem tidak mengambil keputusan pembayaran otomatis.

| Fase | Kegiatan | Ukuran keberhasilan | Risiko dan kendali |
|---|---|---|---|
| 1. Validasi simulasi panitia | Sepakati kontrak data minimal, contoh kasus, modus sah, dan protokol label; jalankan ulang benchmark dan replay | Semua kolom wajib terpetakan; metrik dan batas dapat direproduksi; tidak ada kebocoran waktu/kelompok | Generator terlalu mudah; panitia meninjau kasus sulit dan mengubah skenario sebelum klaim dampak |
| 2. Mode bayangan | Skor data yang disetujui secara terisolasi; proses resmi tetap berjalan; verifikator menilai urutan dan alasan tanpa tindakan otomatis | Recall pada kapasitas yang disepakati, precision, false positive per tipe/wilayah, waktu tinjau median, kesepakatan antarverifikator, dan alasan dismiss | Bias, data sensitif, dan automation bias; minimisasi data, masking, akses berbasis peran nyata, log, serta hak override |
| 3. Integrasi terbatas | Integrasi hanya setelah gerbang keamanan, hukum, dan operasi; rekomendasi tetap memerlukan persetujuan manusia | SLA, ketersediaan, jejak audit lengkap, tingkat koreksi, manfaat proses terukur, dan tidak ada tindakan tanpa otorisasi | Gangguan atau dampak pada peserta/faskes; rollback, kill switch, audit berkala, dan tidak ada penangguhan otomatis |

## Gerbang lanjut/henti

- Jangan lanjut ke fase berikutnya jika kualitas data, dasar pemrosesan, pemilik keputusan, atau jalur koreksi belum jelas.
- Tetapkan ambang metrik dan ukuran sampel sebelum melihat hasil pilot; laporkan interval ketidakpastian dan hasil per kelompok.
- Bandingkan waktu mulai kasus sampai rekomendasi awal pada kasus yang sama, beberapa petugas, dan catat perubahan keputusan setelah bukti dibuka.
- Publikasikan hasil negatif dan false positive bersama metrik deteksi.
