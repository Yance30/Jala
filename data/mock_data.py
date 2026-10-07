"""Teks tampilan dan konstanta statis. Angka dan daftar (klaster, KPI, graf, antrean) TIDAK lagi diketik di sini:
semuanya dihitung oleh core/live.py dari skor nyata."""

QUARTER = "Q3 2026 (1 Jul - 30 Sep)"
QUARTER_SHORT = QUARTER.split(" (")[0]  # "Q3 2026" — dipakai di versi mobile
QUARTERS = ["Q3 2026 (1 Jul - 30 Sep)", "Q2 2026 (1 Apr - 30 Jun)", "Q1 2026 (Jan - Mar)"]


TREND_COLORS = {"Phantom Billing": "#0F766E", "Repeat Billing": "#9A3412", "Self-Referral": "#4B5563"}


GRAPH_LEGEND_NODES = [
    ("Pasien (Patient)", "circle", "#0F766E"),
    ("Faskes (Facility)", "circle", "#0F766E"),
    ("Dokter (Doctor)", "square", "#115E59"),
    ("ICD-10 (Diagnosis)", "diamond", "#0F766E"),
]
GRAPH_LEGEND_EDGES = [
    ("Merujuk (Refers)", "solid"),
    ("Menangani (Treats)", "dash"),
    ("Mengajukan Klaim", "dot"),
]


AUDIT_ACTIONS = [
    {
        "id": "suspend",
        "icon": "⚖", "icon_tone": "teal", "tag": ("Tindak lanjut", "red"),
        "title": "Simulasi penangguhan klaim",
        "body": "Catat simulasi penangguhan klaim untuk klaster ini. Tidak ada pembayaran yang "
                "ditangguhkan atau sistem eksternal yang dihubungi.",
        "button": "Simulasikan penangguhan", "button_kind": "primary",
        "note": "Simulasi; pembayaran tetap tidak berubah",
    },
    {
        "id": "field_audit",
        "icon": "🔎", "icon_tone": "grey", "tag": ("Pemeriksaan lapangan", "grey"),
        "title": "Jadwalkan pemeriksaan lapangan",
        "body": "Catat rencana pemeriksaan lapangan. Tidak ada tim yang ditugaskan atau surat "
                "tugas yang diterbitkan.",
        "button": "Catat rencana pemeriksaan", "button_kind": "secondary",
        "note": "Rencana demo; surat tugas tidak diterbitkan",
    },
    {
        "id": "dismiss",
        "icon": "🛡", "icon_tone": "grey", "tag": ("Klarifikasi pola", "grey"),
        "title": "Tandai sebagai pola wajar",
        "body": "Catat penjelasan bahwa pola memiliki konteks yang wajar. Kalibrasi skor hanya "
                "berlaku di sesi demo ini.",
        "button": "Tandai pola wajar", "button_kind": "secondary",
        "note": "Sertakan catatan konteks pendukung",
    },
]


AUDIT_TEMPLATES = ["Suspensio-01", "Tim-Lapan", "Clear"]

COMPARISON = {
    "legacy": {
        "tag": "Rule-Based Engine (Legacy)",
        "title": "Evaluates each claim individually against rules",
        "sub": "Blind to organized fraud rings that look administratively complete.",
        "panel_label": "Model Verifikasi: Terisolasi (Single-Claim)",
        "panel_note": "Klaim lolos filter otomatis karena kelengkapan berkas fisik terpenuhi per individu invoice.",
        "points": [
            "Pemeriksaan linier per klaim (asumsi kami tentang mesin lama: batas tarif statis, tanpa riwayat relasi).",
            "Tidak mendeteksi pergeseran pola rujukan ganda antar-faskes dan spesialis.",
            "Tinggi resiko lolos klaim fiktif terkoordinasi (phantom billing massal).",
        ],
        "coverage": "1 Klaim Tunggal",
    },
    "han": {
        "tag": "Heterogeneous Graph Neural Network (HAN)",
        "title": "Maps relationships across Faskes, Dokter, and Pasien as a graph",
        "sub": "Reveals hidden collusion patterns invisible in isolated claims.",
        "panel_label": "Topologi Relasional: Multi-Partai (Metapath)",
        "panel_note": "Korelasi siklus klaim terdeteksi secara otomatis melalui keterkaitan aktor berulang & anomali rujukan.",
        "points": [
            "Pelacakan metapath otomatis (Faskes ↔ Dokter ↔ Pasien ↔ ICD-10).",
            "Mendeteksi anomali keterlibatan sindikat meski berkas individual tampak sah.",
            "Skor risiko kolusi dari fitur graf (prototipe); arsitektur target: HAN.",
        ],
        "coverage": "Jejaring Lintas Ekosistem",
    },
}

ABOUT = {
    "title": "Catatan Privasi & Sumber Data Prototipe",
    "subtitle": "JALA — Jaringan Analitik Lintas Aktor • Environmental Sandbox",
    "quote": "“This prototype uses synthetic/dummy data only. No real BPJS participant data is used, "
             "in compliance with Indonesia's Personal Data Protection Law (UU PDP).”",
    "law": "Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)",
    "chips": [
        ("🧠 Synthetic Graph Generator (core/synthetic.py)", "teal"),
        ("🔒 Zero PII Ingestion", "teal"),
        ("♻ Fully Pseudonymized Entities", "teal"),
    ],
    "owner": "Direktorat Jaminan Pelayanan Kesehatan | Tim Pencegahan Kecurangan (Fraud) BPJS Kesehatan",
}

FOOTER_STATUS = [
    ("amber", "Mode: prototipe, data sintetis"),
    ("teal", "Data sintetis: seed 2026"),
    ("teal", "Metrik terukur: About → Bukti Evaluasi"),
]
FOOTER_CUTOFF = "Batas data simulasi: 30 Sep 2026, 23.59 WIB"

NAV_PAGES = [
    ("dashboard", "Dashboard"),
    ("network", "Network Graph"),
    ("risk", "Risk Ranking"),
    ("audit", "Audit Action"),
    ("about", "About"),
]

PAGE_TITLES = {
    "dashboard": "Ringkasan",
    "network": "Peta Jaringan",
    "risk": "Prioritas Klaster",
    "claim": "Alasan Penandaan",
    "audit": "Tindak Lanjut Audit",
    "about": "Tentang JALA",
}
