"""Panduan berbahasa sederhana yang dipakai bersama oleh tutorial dan setiap halaman.

Satu sumber untuk tiga hal:
* PAGES: tujuan tiap halaman, cara membacanya, dan apa langkah berikutnya.
* GLOSSARY: istilah teknis yang dijelaskan dengan bahasa sehari-hari.
* render_page_guide(): kotak "Cara membaca halaman ini" yang bisa dibuka di atas setiap halaman.

Tidak ada angka tetap di teks ini agar tidak basi; angka selalu datang dari skor nyata di halaman.
"""
import html

import streamlit as st

PAGES = {
    "dashboard": {
        "purpose": "Ringkasan keadaan hari ini dalam satu layar.",
        "read": [
            "Kartu di atas menjawab: berapa klaim yang perlu perhatian dan seberapa besar risikonya.",
            "Grafik tren menunjukkan apakah dugaan kecurangan naik atau turun dari waktu ke waktu.",
            "Daftar di bawah berisi kelompok yang paling mendesak untuk diperiksa.",
        ],
        "next": "Klik nama kelompok di daftar untuk melihat detailnya.",
    },
    "risk": {
        "purpose": "Daftar kelompok klaim mencurigakan, diurutkan dari yang paling berisiko.",
        "read": [
            "Skor lebih tinggi berarti kelompok diprioritaskan lebih dulu untuk diperiksa; skor bukan peluang kecurangan.",
            "Label merah berarti skornya sudah melewati batas dan sebaiknya diperiksa lebih dulu.",
            "Gunakan kotak cari atau tombol filter untuk mempersempit daftar.",
        ],
        "next": "Buka satu kelompok untuk melihat alasannya, lalu lihat jaringannya.",
    },
    "network": {
        "purpose": "Peta hubungan antara rumah sakit/klinik, dokter, pasien, dan diagnosis.",
        "read": [
            "Setiap titik adalah satu pihak; setiap garis adalah hubungan di antara mereka.",
            "Hubungan yang terlalu rapat atau berulang di antara pihak yang sama patut dicurigai.",
            "Faskes yang pudar adalah faskes sejenis yang wajar, dipakai sebagai pembanding.",
        ],
        "next": "Buka Claim Details untuk membaca alasan penandaan dalam bahasa biasa.",
    },
    "claim": {
        "purpose": "Penjelasan mengapa kelompok ini ditandai, lengkap dengan buktinya.",
        "read": [
            "Ringkasan di atas menjelaskan kecurigaannya dengan kalimat biasa.",
            "Bukti terukur menunjukkan angka yang mendasari penandaan.",
            "Daftar klaim memperlihatkan klaim mana yang paling mencurigakan.",
        ],
        "next": "Unduh Berkas Bukti untuk diserahkan ke pemeriksa, lalu tentukan tindakan.",
    },
    "audit": {
        "purpose": "Tempat memutuskan tindakan dan mencatat alasannya.",
        "read": [
            "Tulis catatan lebih dulu agar keputusan punya jejak yang jelas.",
            "Ada tiga pilihan: tahan pembayaran (simulasi), kirim pemeriksa ke lapangan, atau tandai sebagai wajar.",
            "Salah memilih? Tombol Batalkan mengembalikan keadaan semula.",
        ],
        "next": "Setelah memutuskan, kembali ke Risk Ranking untuk melihat urutan yang diperbarui.",
    },
    "about": {
        "purpose": "Bukti seberapa baik JALA bekerja, batasannya, dan catatan privasi data.",
        "read": [
            "Hasil di sini diukur pada data buatan yang jawabannya sudah diketahui.",
            "Baca bagian batasan sebelum mengutip angka ke pihak lain.",
            "Angka ini bukan ukuran ketepatan pada data BPJS yang sebenarnya.",
        ],
        "next": "Untuk pengujian nyata, langkah berikutnya adalah uji coba di data asli dengan persetujuan.",
    },
}

# Istilah teknis -> penjelasan sehari-hari. Urutan = urutan tampil.
GLOSSARY = [
    ("Klaster", "Sekelompok rumah sakit, dokter, dan pasien yang klaimnya saling berkaitan erat dan terlihat bergerak bersama."),
    ("Skor risiko", "Indeks prioritas 0–100 dari model untuk mengurutkan pemeriksaan. Bukan probabilitas dan bukan bukti kecurangan."),
    ("Auto-Flagged", "Ditandai otomatis karena skornya melewati batas. Artinya diprioritaskan untuk diperiksa, bukan terbukti curang."),
    ("Faskes", "Fasilitas kesehatan: rumah sakit, klinik, atau puskesmas."),
    ("Verifikator", "Petugas yang memeriksa dan memutuskan. JALA hanya membantu menyusun urutan pemeriksaan."),
    ("Dismiss", "Menandai bahwa kelompok ini ternyata wajar. Skornya turun dan kelompok yang mirip ikut diturunkan sedikit."),
    ("Data sintetis", "Data buatan yang meniru pola nyata. Tidak ada data peserta sungguhan di aplikasi ini."),
    ("Prototipe", "Versi percobaan untuk menunjukkan cara kerja, belum dipakai untuk keputusan sungguhan."),
]


def render_page_guide(page: str) -> None:
    """Kotak lipat 'Cara membaca halaman ini' di bawah judul halaman."""
    g = PAGES.get(page)
    if not g:
        return
    with st.expander("Cara membaca halaman ini", expanded=False):
        items = "".join(f"<li>{html.escape(x)}</li>" for x in g["read"])
        st.markdown(
            f'<div class="jg-box"><p class="jg-purpose">{html.escape(g["purpose"])}</p>'
            f'<ul class="jg-list">{items}</ul>'
            f'<div class="jg-next"><b>Langkah berikutnya.</b> {html.escape(g["next"])}</div></div>',
            unsafe_allow_html=True,
        )


def glossary_html() -> str:
    rows = "".join(
        f'<div class="jg-term"><div class="jg-t">{html.escape(t)}</div>'
        f'<div class="jg-d">{html.escape(d)}</div></div>'
        for t, d in GLOSSARY
    )
    return f'<div class="jg-glossary">{rows}</div>'


CSS = """
<style>
.jg-box{padding:2px 2px 4px;}
.jg-purpose{font-size:14px;font-weight:600;color:#132A1C;margin:0 0 8px;}
.jg-list{margin:0 0 10px 18px;padding:0;font-size:13.5px;line-height:1.6;color:#475569;}
.jg-list li{margin-bottom:4px;}
.jg-next{font-size:13px;color:#475569;background:#F1F5F9;border-left:3px solid #0F766E;border-radius:8px;padding:8px 12px;}
.jg-glossary{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;}
.jg-term{border:1px solid #E2E8F0;border-radius:10px;padding:9px 12px;background:#fff;}
.jg-t{font-size:13px;font-weight:700;color:#0F766E;margin-bottom:2px;}
.jg-d{font-size:12.5px;line-height:1.5;color:#475569;}
</style>
"""
