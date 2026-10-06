# Model card JALA (prototipe)

## Tujuan

Mengurutkan klaster klaim yang perlu ditinjau lebih dulu berdasarkan pola lintas faskes, dokter, peserta, diagnosis, dan waktu. JALA memberi prioritas; verifikator tetap mengambil keputusan.

## Data dan metode

- Data saat ini 100% sintetis, seed default 2026, sekitar 17 ribu klaim dan 60 faskes.
- Tiga skenario fraud yang ditanam: Phantom Billing, Repeat Billing, dan Self-Referral. Data juga memuat pola layanan sah yang sengaja mirip fraud.
- Model yang dievaluasi: fitur graf dan gradient boosting, dengan validasi silang per kelompok faskes. Bukan GNN/HAN.
- Baseline aturan adalah aturan pembanding buatan proyek, bukan sistem BPJS.

## Hasil dan batas

Metrik yang ditampilkan di About dihitung dari seed sintetis. Hasil menunjukkan perilaku pada pola yang didefinisikan generator, bukan akurasi, penghematan, atau dampak di BPJS. Ada delapan kelompok fraud pada dunia default sehingga ketidakpastian tinggi. Replay waktu dan audit kelompok juga hanya simulasi.

## Risiko dan mitigasi

- False positive dapat mengganggu faskes yang memberikan layanan sah. Tampilkan bukti terukur dan jalur dismiss/undo; jangan otomatis menahan pembayaran.
- Kesalahan dismiss dapat menurunkan skor klaster berpola serupa. Uji sensitivitas disediakan untuk memperlihatkan risiko itu.
- Perbedaan tipe faskes/wilayah perlu diaudit kembali dengan data dan label operasional yang sah sebelum pilot.
- Prototipe memakai data sintetis. Jangan memasukkan data klaim atau identitas nyata.

## Penggunaan yang dilarang

Jangan gunakan skor sebagai temuan hukum, dasar tunggal tindakan terhadap faskes, atau pengganti verifikasi dokumen/lapangan. Jangan mengklaim integrasi atau kepatuhan produksi.

## Akuntabilitas

Tim verifikator meninjau bukti dan memutuskan tindak lanjut. Pemilik model bertanggung jawab atas validasi, dokumentasi, pemantauan bias, keamanan, dan persetujuan sebelum penggunaan data operasional. Peran Verifikator/Supervisor di demo hanya simulasi UI, bukan kontrol akses.

## Sebelum pilot

Perlu persetujuan tata kelola data, pemetaan skema resmi, evaluasi temporal tanpa kebocoran, uji keadilan pada label yang representatif, tinjauan keamanan/privasi, serta mode bayangan tanpa dampak pembayaran.
