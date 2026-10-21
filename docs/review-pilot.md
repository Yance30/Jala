# Paket demonstrasi dan uji pemeriksa JALA

Status: instrumen siap; belum ada peserta atau hasil uji manusia. Jangan menyebut penghematan waktu atau akurasi operasional sebagai hasil.

## Mengulang demo

1. Jalankan `python scripts/build_review_pack.py`. Artefak: `artifacts/jala-review-pack.zip`.
2. Ekstrak ZIP. Pada Data & Prediksi, unggah CSV/JSON dari folder `package` bersama-sama.
3. Validasi, gunakan cutoff `2026-09-30` UTC, baseline, kapasitas 100. Jalankan prediksi.
4. Cocokkan metadata versi/runtime dan laporan dengan `expected-results.json`. Versi berbeda perlu membangun ulang paket.
5. Buka antrean; gunakan ID pada `participant/tasks.json`. Baca indikator, catatan sumber, dan ketidakpastian. Catat hasil serta prioritas kerja tanpa mengubah skor model.
6. Unggah paket `insufficient`: validasi struktur dapat lulus, tetapi prediksi harus menolak waktu yang hanya berupa tanggal. Jangan menambah jam buatan.
7. Unduh antrean/riwayat. Hapus model dan antrean melalui pengelolaan data bila demo selesai.

ZIP memuat dua kasus bertanda label sintetis dan satu kasus data tidak memadai. Kunci fasilitator jangan diberikan sebelum tugas selesai. Data label untuk pelatihan tetap terpisah dari input fitur.

## Protokol uji dengan calon verifikator

- Rekrut peserta yang bersedia dan mempunyai pengalaman relevan. Gunakan pseudonim; tidak memerlukan data pasien nyata.
- Sebelum mulai, sepakati tugas, definisi selesai, kapasitas pemeriksaan dan rubrik. Jangan mengubah rubrik setelah melihat hasil.
- Bandingkan pemeriksaan berkas biasa dengan JALA. Acak/counterbalance urutan kondisi dan kasus; bila kasus yang sama diulang, catat risiko efek belajar.
- Mulai timer saat kasus dibuka dan hentikan setelah peserta menyimpan rekomendasi. Catat waktu, sumber bukti, rekomendasi, perubahan keputusan, kesalahan, dan informasi yang sulit ditemukan.
- Gunakan `participant/observations.csv`; jangan mengisi waktu atau keputusan rekaan.
- Rubrik per tugas: sumber bukti sesuai (0–2), penjelasan keterbatasan (0–2), rekomendasi sesuai bukti (0–2), dan keberhasilan menyelesaikan alur (ya/tidak). Dua penilai mendiskusikan perbedaan; label pembangkit bukan pengganti penilaian klinis.
- Laporkan jumlah peserta/kasus, median dan rentang waktu per kondisi, kesalahan, kesepakatan penilai, serta keterbatasan sampel. Laporkan kasus gagal juga. Sampel kecil hanya memberi temuan awal.

## Evaluasi mesin yang dibekukan

`docs/evaluation-protocol-v2.json` menetapkan seed, cutoff, kapasitas dan batas sebelum run. Jalankan `python scripts/build_review_pack.py --evaluate` untuk membuat `docs/evaluation-v2.json` dan paket.

Bandingkan precision/recall, kasus sah yang ikut diperiksa, fraud yang terlewat, serta hasil per keluarga pada kapasitas 20/50/100. Rentang antar-run bukan interval kepercayaan. Data dan skenario tetap sintetis dari tim yang sama. Perubahan fitur berikutnya harus dievaluasi pada protokol yang sama tanpa menyesuaikan model berdasarkan seed holdout.
