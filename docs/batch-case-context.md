# Jaringan dan riwayat kasus dari batch

Di **Tinjauan klaim**, pilih klaim lalu buka **Telusuri jaringan & riwayat kasus**. Ringkasan, graf, linimasa, dan unduhan berasal dari antrean batch tersimpan yang dipilih, bukan dunia sintetis dashboard.

Klaim terkait dipilih dalam jendela ±30 hari dari waktu layanan klaim fokus jika mempunyai peserta yang sama, dokter layanan yang sama, atau dokter terkait rujukan. Kesamaan faskes atau diagnosis saja tidak cukup untuk memasukkan klaim. Ini penelusuran hubungan satu langkah, bukan deteksi komunitas fraud baru.

Graf menghubungkan klaim dengan peserta, dokter, faskes, diagnosis, dan entitas rujukan yang tercatat. Identitas simpul dibedakan menurut tipe agar ID peserta dan dokter yang kebetulan sama tidak digabung. Klaim fokus selalu terlihat. Graf dibatasi 40 klaim terdekat agar terbaca; jumlah yang tidak ditampilkan dijelaskan. Linimasa, ringkasan nilai, dan unduhan tetap memuat seluruh klaim yang memenuhi pilihan.

Nilai total merupakan jumlah tarif klaim, bukan kerugian atau penghematan. Hubungan bukan bukti kolusi atau atribusi prediksi model. Data historis pelatihan, rekam medis, dan klaim di luar batch tidak disertakan. Paket pemeriksaan JSON menyertakan metadata model, cakupan, klaim terkait dan riwayat keputusan terkait.

Antrean baru menyimpan kolom rujukan. Antrean lama tetap dapat dibaca, tetapi rujukan yang dulu tidak disimpan tidak direkonstruksi; kirim ulang hasil prediksi untuk membuat antrean dengan informasi tersebut.
