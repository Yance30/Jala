"""Posisi tiga tipologi JALA terhadap modus kecurangan di BPJS Kesehatan Healthkathon 2026 (Kategori
Efisiensi Risiko pada Fasilitas Kesehatan), beserta batas apa yang bisa dibuktikan dari data klaim.

Sumber nomor dan definisi: Participant Guide Healthkathon 2026, bagian 6 (dirangkum, bukan kutipan penuh).
Satu sumber kebenaran untuk layar, berkas bukti, dan tes, agar JALA konsisten diposisikan sebagai alat
PRIORITAS PEMERIKSAAN, bukan pembuktian kecurangan.
"""
from __future__ import annotations

PRINSIP = ("Hasil JALA adalah prioritas pemeriksaan, bukan pembuktian kecurangan. "
           "Keputusan akhir ada pada verifikator.")

MODUS = {
    "Phantom Billing": {
        "no": 6, "nama": "Phantom billing (klaim palsu)",
        "definisi": "Klaim atas layanan yang tidak pernah diberikan kepada pasien.",
        "ditangkap": "Peserta luar wilayah, klaim dikirim serentak, dan dokter yang sama menagih di banyak faskes "
                     "dalam 30 menit.",
        "batas": "JALA hanya menduga dari pola klaim. Bahwa layanan benar-benar tidak diberikan hanya bisa "
                 "dipastikan lewat pemeriksaan lapangan atau dokumen.",
    },
    "Repeat Billing": {
        "no": 11, "nama": "Repeat billing (klaim berulang)",
        "definisi": "Klaim diulang pada kasus yang sama yang sudah ditagihkan dan dibayarkan.",
        "ditangkap": "Peserta dan diagnosis yang sama ditagih lagi dalam hitungan jam, termasuk lintas faskes.",
        "batas": "Data tidak memuat status pembayaran, jadi unsur \"sudah dibayarkan\" belum dimodelkan. "
                 "Kunjungan ulang yang sah (mis. hemodialisis terjadwal, kontrol UGD) juga bisa tertandai.",
    },
    "Self-Referral": {
        "no": 10, "nama": "Self-referral (rujukan semu)",
        "definisi": "Klaim akibat rujukan ke RS/dokter tertentu tanpa alasan keterbatasan fasilitas.",
        "ditangkap": "Dokter perujuk terdaftar (SIP) di faskes tujuan, konsentrasi rujukan, dan rujukan balik "
                     "yang membentuk siklus.",
        "batas": "Data tidak memuat kapabilitas faskes, jadi unsur \"tanpa alasan keterbatasan fasilitas\" tidak "
                 "bisa dinilai. JALA hanya melihat afiliasi dokter dengan faskes tujuan dan pola rujukan.",
    },
}


def info(typology: str) -> dict | None:
    return MODUS.get(typology)


def headline(typology: str) -> str:
    m = info(typology)
    return f"Modus Healthkathon 2026 no. {m['no']}: {m['nama']}" if m else ""
