"""Panduan berbahasa sederhana yang dipakai bersama oleh tutorial dan setiap halaman.

Satu sumber untuk tiga hal:
* PAGES: tujuan tiap halaman, cara membacanya, dan apa langkah berikutnya.
* GLOSSARY: istilah teknis yang dijelaskan dengan bahasa sehari-hari.
* render_page_guide(): kotak "Cara membaca halaman ini" yang bisa dibuka di atas setiap halaman.

Tidak ada angka tetap di teks ini agar tidak basi; angka selalu datang dari skor nyata di halaman.
"""
import html

import streamlit as st
from components.typology import label as typology_label

PAGES = {
    "dashboard": {
        "purpose": "Ringkasan keadaan hari ini dalam satu layar.",
        "read": [
            "Kartu di atas menjawab: berapa klaim yang perlu perhatian dan seberapa besar risikonya.",
            "Grafik tren menunjukkan apakah dugaan kecurangan naik atau turun dari waktu ke waktu.",
            "Daftar di bawah berisi kelompok yang paling mendesak untuk diperiksa.",
        ],
        "next": "Pilih kelompok di daftar untuk melihat alasan dan buktinya.",
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
            "Hubungan yang rapat atau berulang adalah petunjuk untuk diperiksa, bukan bukti pelanggaran.",
            "Faskes yang pudar adalah faskes sejenis yang wajar, dipakai sebagai pembanding.",
        ],
        "next": "Buka alasan penandaan untuk membaca konteks dan bukti terkait.",
    },
    "claim": {
        "purpose": "Alasan sebuah kelompok mendapat prioritas tinjauan, beserta konteks dan bukti yang dapat diperiksa.",
        "read": [
            "Skor mengurutkan prioritas; skor bukan probabilitas atau bukti kecurangan.",
            "Bukti terukur menunjukkan pola pada data sintetis dan perlu diperiksa bersama konteks layanan.",
            "Daftar klaim menampilkan contoh klaim terkait, bukan putusan atas pihak tertentu.",
        ],
        "next": "Periksa klaim sumber, catat alasan, lalu pilih tindak lanjut simulasi.",
    },
    "audit": {
        "purpose": "Tempat memutuskan tindakan dan mencatat alasannya.",
        "read": [
            "Tulis catatan lebih dulu agar keputusan punya jejak yang jelas.",
            "Tiga pilihan mencatat simulasi penangguhan, rencana pemeriksaan lapangan, atau penandaan pola wajar.",
            "Catatan dan keputusan tersimpan di riwayat lokal; tidak ada tindakan yang dikirim ke sistem BPJS.",
        ],
        "next": "Tinjau ringkasan status dan riwayat klaster sebelum kembali ke antrean.",
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
    ("Skor prioritas", "Indeks 0–100 dari model untuk mengurutkan pemeriksaan. Bukan probabilitas dan bukan bukti kecurangan."),
    ("Skor risiko", "Istilah lama untuk skor prioritas; angkanya bukan probabilitas dan bukan bukti kecurangan."),
    ("Tipologi", "Nama pola yang dicari model. Ini dugaan untuk ditinjau, bukan kesimpulan tentang pelanggaran."),
    ("Phantom Billing (Klaim Palsu)", "Dugaan klaim atas layanan atau kunjungan yang perlu dicocokkan dengan catatan pelayanan."),
    ("Repeat Billing", "Dugaan pola klaim berulang yang perlu dicocokkan dengan tanggal layanan dan dokumen klaim."),
    ("Rujukan tidak sesuai (Self-referral)", "Dugaan pola rujukan yang perlu diperiksa terhadap kebutuhan klinis, aturan, dan konteks layanan."),
    ("AUC / AP", "Ukuran pembanding model pada data sintetis yang jawabannya diketahui. Angka ini tidak menyatakan kinerja pada data nyata."),
    ("Prioritas otomatis", "Skor klaster melewati ambang antrean awal. Artinya diperiksa lebih dulu, bukan terbukti curang."),
    ("Faskes", "Fasilitas kesehatan: rumah sakit, klinik, atau puskesmas."),
    ("Verifikator", "Petugas yang memeriksa dan memutuskan. JALA hanya membantu menyusun urutan pemeriksaan."),
    ("Dismiss", "Istilah teknis untuk mencatat pola wajar. Kalibrasi demo dapat mengubah prioritas kelompok yang serupa."),
    ("Pola wajar", "Catatan verifikator bahwa pola ini punya penjelasan yang wajar."),
    ("Data sintetis", "Data buatan yang meniru pola nyata. Tidak ada data peserta sungguhan di aplikasi ini."),
    ("Prototipe", "Versi percobaan untuk menunjukkan cara kerja, belum dipakai untuk keputusan sungguhan."),
]


def render_typology_glossary() -> None:
    """Compact, contextual descriptions for the typology labels used in the queue."""
    terms = {typology_label("Phantom Billing"), "Repeat Billing", typology_label("Self-Referral")}
    with st.expander("Arti label pola (dugaan, bukan putusan)"):
        st.markdown(
            "\n".join(f"- **{term}:** {description}" for term, description in GLOSSARY if term in terms)
        )


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
