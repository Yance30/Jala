# Latihan tanya jawab juri

Jawab satu kalimat, lalu tunjukkan bukti atau batas di layar.

1. **Apakah JALA terbukti mendeteksi fraud BPJS?** Belum; angka yang tersedia mengukur pola pada data sintetis dan perlu diuji dalam pilot yang disetujui.
2. **Apa pembanding aturan lama?** Baseline ini aturan sederhana buatan proyek, bukan representasi sistem BPJS yang sebenarnya.
3. **Apakah JALA menggantikan pemeriksa dokumen?** Tidak, JALA mengurutkan jaringan dan mengumpulkan konteks agar pemeriksa dapat memeriksa berkas lebih terarah.
4. **Apakah skor berarti probabilitas fraud?** Tidak, skor dipakai untuk prioritas dan bukan bukti atau probabilitas terkalibrasi.
5. **Apa hasil pada kapasitas audit terbatas?** Halaman About menunjukkan perbandingan jumlah fraud sintetis tertangkap pada kapasitas sama, bukan penghematan operasional.
6. **Apa yang terjadi jika verifikator salah dismiss?** Klaster serupa dapat ikut turun skornya, sehingga simulasi kesalahan dan mekanisme undo ditampilkan.
7. **Apakah kelompok tertentu lebih sering salah ditandai?** Audit per tipe faskes dan wilayah tersedia untuk generator sintetis, tetapi keadilan di lapangan belum diketahui.
8. **Apakah data peserta nyata digunakan?** Tidak, seluruh ID dan transaksi pada prototipe ini sintetis.
9. **Apakah tampilan peran memenuhi UU PDP?** Tidak; masking dan pemilih peran hanya simulasi, bukan kontrol akses atau bukti kepatuhan.
10. **Apakah sistem membekukan pembayaran?** Tidak, tindakan pada demo hanya simulasi dan tidak terhubung ke sistem eksternal.
11. **Mengapa belum memakai GNN/HAN?** Fitur graf dan gradient boosting dipilih karena hasilnya dapat diukur dan dijelaskan pada prototipe ini.
12. **Apa langkah berikutnya?** Validasi kontrak data, mode bayangan berdampingan dengan proses saat ini, lalu integrasi terbatas hanya setelah gerbang tata kelola, keamanan, dan evaluasi terpenuhi.
