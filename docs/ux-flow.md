# Alur pengguna JALA

Poin UX 2–5: ringkasan batch mengutamakan jumlah klaim, periode pengajuan, dan sumber.
ID serta versi model berada di **Rincian teknis batch**. Pintasan **Ke detail klaim**,
**Ke hasil tinjauan**, dan **Kembali ke antrean** memudahkan perpindahan pada layar
ponsel. Ringkasan progres dihitung dari status terakhir, bukan jumlah catatan yang
tersimpan: **Belum ditinjau**, **Dalam pemeriksaan**, dan **Selesai**. Hanya status
Selesai ditinjau dan Penjelasan layanan wajar termasuk selesai; kesalahan data dan
data belum cukup tetap perlu tindak lanjut. Rincian graf dibuka sesuai kebutuhan.

Pintu masuk operasional adalah **Data & Prediksi**, melalui sidebar atau tombol mulai pada ringkasan demo.

Pematangan UX 21 Oktober 2026: halaman operasional menampilkan lima tahap
**Siapkan data → Validasi → Prediksi → Tinjau → Unduh hasil**. Pengguna baru dapat
langsung memilih **Gunakan data contoh**; pengguna unggahan mengekstrak ZIP dahulu,
memilih CSV/JSON, lalu menekan **Validasi paket unggahan**. Pesan penolakan diikuti
petunjuk memperbaiki dan mengunggah kembali berkas.

Pada tinjauan, klik baris tabel atau gunakan pemilih klaim. ID klaim aktif tampil
di judul detail. **Simpan & lanjut** menyimpan keputusan sebelum membuka klaim
berikutnya dalam hasil filter; nama pemeriksa diingat selama sesi. Tombol
**Klaim berikutnya** hanya berpindah, tanpa menyimpan. Pada klaim terakhir gunakan
**Simpan tinjauan**. Hasil pencarian kosong menyediakan **Reset filter**.

Kolom antrean memakai label Indonesia, tarif ditampilkan sebagai rupiah, dan waktu
layanan/pengajuan diberi label UTC. Rincian fitur teknis terpisah dari catatan
pembanding. Sumber batch dan perilaku penyimpanan sesuai mode ditampilkan di atas
antrean. Area unduhan menjelaskan perbedaan CSV hasil terbaru dan JSON riwayat.
Latar halaman operasional disederhanakan agar pembacaan bukti lebih nyaman.

Responsivitas disatukan dalam `components/responsive.py`, dimuat setelah tema dan
topbar. Pada lebar sampai 900 px, kolom Streamlit bertumpuk agar panel tidak terlalu
sempit. Sampai 640 px, margin konten menjadi 16 px, tombol aksi memakai lebar penuh
dan tinggi minimal 44 px, input memakai ukuran huruf 16 px, serta tahap alur menjadi
dua kolom. Tabel dan grafik tetap dibatasi lebar konten; tabel yang lebar digeser di
dalam komponennya, bukan dengan menggeser seluruh halaman. Aturan ini menggunakan
selector Streamlit sehingga pemeriksaan browser perlu diulang saat versi UI berubah.

Verifikasi responsif 21 Oktober 2026: lima tes browser awal lulus; pemeriksaan
lanjutan dua tes lulus, mencakup sembilan halaman pada lebar 320, 390, 768, 1024,
dan 1440 px serta antrean berisi data. Setelah perbaikan lebar wadah tombol,
satu tes alur lengkap diulang dan lulus (70,01 detik), termasuk pengukuran lebar
tombol simpan dan susunan kolom. Tangkapan formulir mobile diperiksa secara visual.
Pengujian memakai Chromium; bukan jaminan semua perangkat/browser. `compileall`
dan `git diff --check` lulus. Perubahan belum di-deploy.

1. Gunakan contoh sintetis atau unggah paket, lalu validasi.
2. Periksa identitas batch dan periode pengajuan. Tentukan batas pelatihan, lalu jalankan prediksi. Baseline graf + GBM tetap default; kandidat berada di pengaturan lanjutan.
3. Buka antrean tinjauan. Cari klaim/faskes atau filter status, baca detail serta indikator, dan simpan keputusan dengan catatan dan nama pemeriksa.
4. Baca catatan sumber dan nilai fitur; pisahkan skor model, prioritas kerja, dan keputusan pemeriksa.
5. Lanjutkan ke klaim berikutnya atau unduh hasil. SQLite dipisahkan per sesi demo atau identitas login;
   mode lokal satu pengguna harus dipilih eksplisit. Hapus model/antrean melalui pengelolaan data.

Menu jaringan, prioritas klaster, dan tindak lanjut diberi label demo karena memakai dunia sintetis bawaan, bukan graf unggahan. Tentang & Evaluasi memuat bukti eksperimen dan batasan. Skor ditampilkan pada skala /100, bukan probabilitas fraud.

Perubahan visual mempertahankan teal JALA, memakai kartu langkah responsif, fokus keyboard yang terlihat, dan tata letak antrean/detail berdampingan. Penggantian paket membersihkan hasil prediksi sebelumnya. Periode pada halaman batch tidak lagi menampilkan kuartal demo yang tetap.
