# Mode penggunaan, penyimpanan dan pemulihan JALA

## Mode default: demo per sesi

`JALA_MODE=demo` adalah default aplikasi. Identitas acak dibuat server dan tidak diterima dari URL atau formulir. Database setiap sesi berada di `.jala/sessions/<hash>/batch.sqlite3`. Sesi lain tidak mendapat akses walaupun mengetahui ID model/antrean. Menutup browser dapat menghilangkan kemampuan membuka sesi tersebut kembali.

Database demo yang idle 24 jam dibersihkan pada akses penyimpanan berikutnya. Jika aplikasi mati, pembersihan baru terjadi ketika dijalankan kembali. Ini retensi demo, bukan jaminan penghapusan fisik disk/backup. Hanya gunakan data sintetis/uji.

## Mode lokal satu pengguna

`run_demo.bat` menyelaraskan dependensi dengan lock Windows, menetapkan `JALA_MODE=local`, dan mengikat server ke `127.0.0.1`. Data lama `.jala/batch.sqlite3` tetap dapat diakses dalam mode ini. Jangan membagikan instance lokal ini ke pengguna lain.

Di sistem lain: set `JALA_MODE=local`, lalu `streamlit run app.py --server.address=127.0.0.1`.

## Mode bersama dengan login

1. Pasang runtime lock dan tambahan `requirements-auth.txt`. Tambahan login masih menggunakan resolver ekstra Streamlit; bekukan lock deployment lengkap sebelum rilis lingkungan bersama.
2. Konfigurasikan OIDC pada `.streamlit/secrets.toml` menggunakan konfigurasi `auth` Streamlit: `redirect_uri`, `cookie_secret`, `client_id`, `client_secret`, dan `server_metadata_url`. Jangan commit kredensial.
3. Set `JALA_MODE=shared` dan `JALA_OIDC_ISSUER` sama persis dengan klaim `iss` dari penyedia identitas.
4. Login wajib mempunyai `sub` serta issuer yang cocok. Aplikasi menolak akses bila identitas, dependensi, atau konfigurasi dasar belum tersedia.
5. Database disekat per gabungan issuer + subject di `.jala/owners/<hash>/`. Peran pratinjau tidak mengubah akses. Antrean tidak dibagikan antar pengguna; kolaborasi satu antrean membutuhkan desain izin tambahan.
6. Verifikasi callback HTTPS, cookie, logout, dua akun dan pembatasan jaringan pada penyedia/hosting yang sebenarnya sebelum dibuka. Tes lokal memakai identitas terkontrol; login penyedia nyata belum diuji tanpa konfigurasi akun.

Nama pemeriksa adalah nama tampilan; event mode bersama juga menyimpan fingerprint identitas terautentikasi. Administrator mesin tetap dapat mengubah database. Ini bukan log tahan perubahan.

## Apa yang disimpan

| Aksi | Data yang disimpan |
|---|---|
| Validasi/latih paket | Dataset dan hasil dalam sesi |
| Simpan model | Estimator, riwayat klaim pelatihan, referensi, metadata runtime |
| Prediksi model tersimpan | Riwayat observasi kumulatif dan referensi untuk konteks batch berikutnya |
| Buka antrean | Klaim yang dinilai, skor, catatan pembanding, metadata sumber |
| Simpan tinjauan | Status, catatan, pemeriksa, prioritas kerja, waktu; skor model tidak diubah |

Pada Data & Prediksi / Status sistem, pengguna dapat membersihkan paket sesi, menghapus satu model/antrean, atau seluruh data ruangnya. Hapus model **dan** antrean bila ingin menghapus kedua salinan. Riwayat demo klaster opsional `JALA_REVIEW_HISTORY_DB` terpisah dari batch dan tidak dihapus oleh pengelola batch.

## Backup dan restore

Gunakan `python scripts/storage_backup.py --database <path> --output <backup-baru.sqlite3>` pada database lokal atau path pemilik yang telah ditetapkan administrator. Skrip memakai SQLite backup API dan memeriksa integritas. File backup memuat data sensitif yang sama dengan database asal; simpan dengan izin OS terbatas. Jangan masukkan backup ke Git.

Untuk restore: hentikan aplikasi, periksa checksum backup terhadap catatan yang disimpan terpisah, simpan salinan database lama, lalu salin backup tepercaya ke path pemilik yang benar. Jalankan `PRAGMA integrity_check` dan smoke test model/tinjauan di lingkungan asal sebelum membuka layanan. Jangan memuat backup pihak lain: blob model berupa pickle. Penghapusan di UI tidak menghapus backup.

## Batas operasional

- Maksimal 5 MB/file unggahan; snapshot maksimal 30.000 klaim, 50.000 baris per referensi, 500 klaim per peserta, dan 500 klaim per dokter dalam jendela ±30 menit.
- Ini batas konservatif prototipe, bukan SLA. Pemrosesan masih sinkron; belum ada worker terpisah atau pembatalan pekerjaan yang sedang berjalan. Jangan menjanjikan layanan beban tinggi.
- Cap waktu yang seluruhnya tengah malam ditolak untuk penilaian. Nilai intrahari sendiri belum membuktikan presisi atau semantik sumber; konfirmasikan kamus data.
- Model lama ditolak setelah perubahan versi fitur. Latih model baru; data lama tidak dimigrasi atau dihapus otomatis.
- Default demo, devcontainer dan Docker mempertahankan proteksi CORS/XSRF. Docker menggunakan user non-root.
