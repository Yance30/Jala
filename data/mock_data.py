"""Synthetic mock data mirroring the Stitch export (no real BPJS data)."""

QUARTER = "Q3 2024 (1 Jul - 30 Sep)"
QUARTER_SHORT = QUARTER.split(" (")[0]  # "Q3 2024" — dipakai di versi mobile
QUARTERS = ["Q3 2024 (1 Jul - 30 Sep)", "Q2 2024 (1 Apr - 30 Jun)", "Q1 2024 (Jan - Mar)"]

DASHBOARD_KPIS = [
    {
        "label": "Phantom Billing Flagged",
        "badge": ("Critical", "red"),
        "value": "1,284",
        "icon": "",
        "note": "Identified via disconnected claims & synthetic provider nodes",
    },
    {
        "label": "Repeat Billing Flagged",
        "badge": ("High Surge", "amber"),
        "value": "847",
        "icon": "⧉",
        "note": "Identified via duplicate visit timestamps across Faskes",
    },
    {
        "label": "Self-Referral Flagged",
        "badge": ("Collusion Risk", "green"),
        "value": "419",
        "icon": "⇄",
        "note": "Identified via circular doctor-clinic ownership subgraph",
    },
]

TREND_WEEKS = [f"W{i:02d}" for i in range(1, 13)]
TREND_SERIES = {
    "Phantom Billing": [36, 44, 62, 74, 95, 110, 118, 126, 138, 144, 150, 157],
    "Repeat Billing": [18, 24, 32, 44, 58, 52, 66, 81, 75, 92, 99, 110],
    "Self-Referral": [8, 12, 16, 22, 28, 33, 38, 42, 48, 54, 60, 66],
}
TREND_COLORS = {"Phantom Billing": "#0F766E", "Repeat Billing": "#9A3412", "Self-Referral": "#4B5563"}

DASHBOARD_FOOTER = [
    {"icon": "🕸", "label": "Total Monitored Nodes", "value": "2.4M Entities (Faskes, Dokter, Peserta)", "tone": "dark"},
    {"icon": "❋", "label": "Flagged Subgraph Density", "value": "0.084", "extra": "(High Anomaly Concentration)", "tone": "dark"},
    {"icon": "", "label": "Next Verifikator Action Queue", "value": "18 High-Priority Clusters pending field review", "tone": "red"},
]

RISK_LEVELS = ["All Risk Levels", "Critical Anomaly (Score > 0.85)", "Moderate Risk", "Normal / Baseline"]
TYPOLOGIES = [
    "All Typologies",
    "Spatial-Temporal Mobilization",
    "Phantom Billing Ring",
    "Circular Self-Referral",
    "Upcoding / Diagnosis Stacking",
]

GRAPH_NODES = [
    # normal baseline subgraph (teal)
    {"id": "rsud", "x": 3.0, "y": 5.0, "type": "faskes", "label": "RSUD Sejahtera", "sub": "Tipe B · Terakreditasi", "risk": False},
    {"id": "drA", "x": 2.2, "y": 7.0, "type": "dokter", "label": "dr. Sp.A (SIP-4412)", "sub": "Spesialis Anak", "risk": False},
    {"id": "p1029", "x": 1.6, "y": 4.6, "type": "pasien", "label": "Pasien P-1029", "sub": "NIK 3204***", "risk": False},
    {"id": "p8492", "x": 3.0, "y": 2.6, "type": "pasien", "label": "Pasien P-8492", "sub": "NIK 3171***", "risk": False},
    {"id": "i10", "x": 4.6, "y": 6.6, "type": "icd", "label": "ICD: I10", "sub": "Hipertensi Esensial", "risk": False},
    {"id": "z00", "x": 4.6, "y": 3.6, "type": "icd", "label": "ICD: Z00.0", "sub": "Pemeriksaan Umum", "risk": False},
    # flagged cluster (orange)
    {"id": "kpx", "x": 9.0, "y": 4.0, "type": "faskes", "label": "Klinik Utama Pratama X", "sub": "HAN Suspicion 0.94", "risk": True},
    {"id": "drMK", "x": 9.4, "y": 7.0, "type": "dokter", "label": "dr. M.K (SIP-9912)", "sub": "Multi-Faskes Concurrency", "risk": True},
    {"id": "drBS", "x": 10.6, "y": 6.2, "type": "dokter", "label": "dr. B.S (SIP-8823)", "sub": "", "risk": True},
    {"id": "p9102", "x": 7.4, "y": 6.0, "type": "pasien", "label": "Pasien P-9102", "sub": "KTP Luar Wilayah", "risk": True},
    {"id": "p9103", "x": 7.0, "y": 4.2, "type": "pasien", "label": "Pasien P-9103", "sub": "KTP Luar Wilayah", "risk": True},
    {"id": "p9108", "x": 7.6, "y": 2.0, "type": "pasien", "label": "Pasien P-9108", "sub": "KTP Luar Wilayah", "risk": True},
    {"id": "p9140", "x": 10.6, "y": 2.6, "type": "pasien", "label": "Pasien P-9140", "sub": "", "risk": True},
    {"id": "m545", "x": 11.6, "y": 4.8, "type": "icd", "label": "ICD: M54.5", "sub": "Low Back Pain (Staged)", "risk": True},
    {"id": "e119", "x": 11.6, "y": 3.2, "type": "icd", "label": "ICD: E11.9", "sub": "Type 2 DM (Replicated)", "risk": True},
]

GRAPH_EDGES = [
    {"src": "drA", "dst": "rsud", "style": "dash", "label": "", "risk": False},
    {"src": "p1029", "dst": "rsud", "style": "solid", "label": "t-14d", "risk": False},
    {"src": "rsud", "dst": "p8492", "style": "solid", "label": "", "risk": False},
    {"src": "rsud", "dst": "i10", "style": "dot", "label": "t-12d", "risk": False},
    {"src": "rsud", "dst": "z00", "style": "dot", "label": "", "risk": False},
    {"src": "p9102", "dst": "kpx", "style": "solid", "label": "t-00:04", "risk": True},
    {"src": "p9103", "dst": "kpx", "style": "solid", "label": "t-00:07", "risk": True},
    {"src": "p9108", "dst": "kpx", "style": "solid", "label": "t-00:11", "risk": True},
    {"src": "p9140", "dst": "kpx", "style": "solid", "label": "", "risk": True},
    {"src": "drMK", "dst": "kpx", "style": "dash", "label": "", "risk": True},
    {"src": "drBS", "dst": "kpx", "style": "dash", "label": "", "risk": True},
    {"src": "kpx", "dst": "m545", "style": "dot", "label": "", "risk": True},
    {"src": "kpx", "dst": "e119", "style": "dot", "label": "t-burst", "risk": True},
    {"src": "rsud", "dst": "kpx", "style": "dot", "label": "", "risk": False, "faint": True},
]

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

RISK_STATS = [
    {"label": "Total Flagged Entities", "value": "42", "tone": "dark", "icon": "🕸", "icon_tone": "grey", "note": ""},
    {"label": "Auto-Flagged (>85%)", "value": "18", "tone": "red", "icon": "⚠", "icon_tone": "red", "note": "Kritis (Prioritas A1)"},
    {"label": "Under Active Audit", "value": "12", "tone": "dark", "icon": "✅", "icon_tone": "amber", "note": ""},
    {"label": "Avg Cluster Density", "value": "0.74", "tone": "teal", "icon": "❋", "icon_tone": "green", "note": "Modularity: 0.68"},
]

RISK_FILTERS = ["Semua Entitas (8)", ">85% Auto-Flagged (5)", "Phantom Billing", "Repeat Billing"]

RISK_CLUSTERS = [
    {
        "id": "JALA-HAN-089", "name": "Sindikat Ring #JALA-HAN-089",
        "subtitle": "Klinik Utama Pratama X + 4 Faskes Cabang, 8 Dokter Terafiliasi",
        "status": ("Auto-Flagged", "red"), "score": 96, "conf": "Confidence Max",
        "metric": "Cluster Weight: 4.88 · E-Score 0.94", "typology": ("Phantom Billing", "amber"),
        "why": "Spatial-temporal anomaly: ratusan klaim peserta fiktif dari luar domisili diajukan "
               "serentak tanpa riwayat antrean faskes primer.",
        "actions": ["Lihat Sub-Graph", "Berkas Bukti (14)"], "icon": "✳", "icon_tone": "amber",
    },
    {
        "id": "JALA-HAN-077", "name": "Klaster Rujukan dr. B.S. & Klinik Medika 04",
        "subtitle": "dr. B.S., Sp.PD / SIP 8823-JBR · Faskes FKRTL Wilayah 4",
        "status": ("Auto-Flagged", "red"), "score": 94, "conf": "Confidence Max",
        "metric": "Directed Cycle Rank: 0.91 · Mod: 0.72", "typology": ("Self-Referral", "green"),
        "why": "Pola sirkular tertutup: dokter merujuk pasien kronis ke klinik pribadi dengan rasio "
               "rujukan internal 98.4% tanpa indikasi medis rujukan balik.",
        "actions": ["Lihat Sub-Graph", "Rekomendasi Sanksi"], "icon": "♻", "icon_tone": "green",
    },
    {
        "id": "JALA-HAN-061", "name": "Konsorsium Faskes Cahaya Husada",
        "subtitle": "RS Swasta Kelas C + 3 Apotek Jejaring",
        "status": ("Auto-Flagged", "red"), "score": 91, "conf": "Confidence Max",
        "metric": "Pair Collision: 342 kejadian", "typology": ("Repeat Billing", "amber"),
        "why": "Duplikasi klaim kode ICD-10 M54.5 dengan timestamp selisih < 12 jam pada hari yang "
               "sama lintas fasilitas penunjang.",
        "actions": ["Lihat Sub-Graph", "Matrix Duplikasi"], "icon": "⧉", "icon_tone": "amber",
    },
    {
        "id": "JALA-HAN-054", "name": "Sindikat Klaim Laboratorium Sentral Y",
        "subtitle": "Lab Pratama & Jaringan Dokter Umum (Kode Wil. 1109)",
        "status": ("Auto-Flagged", "red"), "score": 88, "conf": "Confidence High",
        "metric": "Cluster Weight: 3.90 · E-Score 0.86", "typology": ("Phantom Billing", "amber"),
        "why": "Pengajuan klaim panel darah lengkap tanpa data verifikasi sidik jari/biometrik "
               "peserta BPJS aktif.",
        "actions": ["Lihat Sub-Graph"], "icon": "🧪", "icon_tone": "amber",
    },
    {
        "id": "JALA-HAN-048", "name": "Klaster Poliklinik Gigi Mandiri Sehat",
        "subtitle": "drg. A.R. / SIP 4412-DKI (Klinik Pratama Rawat Jalan)",
        "status": ("Auto-Flagged", "red"), "score": 86, "conf": "Confidence High",
        "metric": "Interval Anomaly: Δt = 36h avg", "typology": ("Repeat Billing", "amber"),
        "why": "Split billing sistematis: prosedur restorasi komposit dipecah menjadi beberapa sesi "
               "klaim terpisah dalam kurun 48 jam.",
        "actions": ["Lihat Sub-Graph"], "icon": "🦷", "icon_tone": "amber",
    },
    {
        "id": "JALA-HAN-033", "name": "Jejaring Faskes Tingkat Pertama (FKTP) Kasih Ibu",
        "subtitle": "FKTP 0112B004 · 3 Cabang Kab. Sukabumi",
        "status": ("Standard Review", "grey"), "score": 82, "conf": "Standard Review",
        "metric": "Cluster Weight: 2.76", "typology": ("Self-Referral", "green"),
        "why": "Rujukan anomali terkonsentrasi ke fasilitas diagnostik terafiliasi keluarga dengan "
               "volume 4x standar regional.",
        "actions": ["Lihat Sub-Graph"], "icon": "🏥", "icon_tone": "green",
    },
    {
        "id": "JALA-HAN-027", "name": "Sentra Rehabilitasi Medik Prima",
        "subtitle": "Klinik Fisioterapi & Dokter Sp.KFR",
        "status": ("Standard Review", "grey"), "score": 78, "conf": "Standard Review",
        "metric": "Throughput Anomaly: 184% cap", "typology": ("Repeat Billing", "amber"),
        "why": "Frekuensi klaim fisioterapi melampaui kapasitas tempat tidur/waktu operasional "
               "terdaftar faskes.",
        "actions": ["Lihat Sub-Graph"], "icon": "🏃", "icon_tone": "amber",
    },
    {
        "id": "JALA-HAN-019", "name": "Klinik Pratama Rawat Inap Berkah",
        "subtitle": "Faskes 0304U019 · Rawat Inap Tingkat Pertama",
        "status": ("Standard Review", "grey"), "score": 71, "conf": "Standard Review",
        "metric": "Seasonal Factor: 3.20x normal", "typology": ("Phantom Billing", "amber"),
        "why": "Peningkatan volume klaim rawat inap 320% pada tanggal libur nasional tanpa lonjakan "
               "pasien gawat darurat.",
        "actions": ["Lihat Sub-Graph"], "icon": "🛏", "icon_tone": "amber",
    },
]

TRIAGE_STATS = [
    {"label": "Total Klaster Diaudit", "value": "1,248", "delta": "↑ +14.2%", "note": "Dari 3.4M transaksi klaim", "tone": "dark"},
    {"label": "Anomali Kritis (>90%)", "value": "42", "delta": "", "note": "Memerlukan freeze pembayaran", "tone": "amber"},
    {"label": "Eksposur Finansial", "value": "Rp 38.4 M", "delta": "", "note": "Total potensi kerugian negara", "tone": "dark"},
    {"label": "Metapath Akurasi", "value": "98.1%", "delta": "", "note": "AUC-ROC post-human review", "tone": "teal"},
]

TRIAGE_QUEUE = [
    {"id": "JALA-HAN-089", "name": "Sindikat Ring #JALA-HAN-089", "nodes": "5 Node Utama · Wilayah Jawa Barat",
     "typology": "Phantom Billing", "faskes": "Klinik Pratama X (+4 Cabang)", "volume": 412,
     "value": "Rp 1.840.000.000", "score": 96, "status": ("Auto-Flagged", "red")},
    {"id": "JALA-HAN-042", "name": "Klaster Farmasi #JALA-HAN-042", "nodes": "8 Node Resep · DKI Jakarta",
     "typology": "Ghost Prescription", "faskes": "Apotek Terpadu Medika", "volume": 289,
     "value": "Rp 912.450.000", "score": 91, "status": ("Review Pending", "amber")},
    {"id": "JALA-HAN-104", "name": "Grup Rujukan #JALA-HAN-104", "nodes": "3 RS Swasta Tipe C · Jawa Timur",
     "typology": "Upcoding Prosedur", "faskes": "RS Karsa Husada Group", "volume": 610,
     "value": "Rp 3.120.000.000", "score": 88, "status": ("Investigasi Lanjut", "grey")},
    {"id": "JALA-HAN-021", "name": "Kolektif Dialisis #JALA-HAN-021", "nodes": "Klinik Hemodialisa · Sumatra Utara",
     "typology": "Repeat Billing", "faskes": "Klinik Ginjal Sehat Abadi", "volume": 154,
     "value": "Rp 742.000.000", "score": 79, "status": ("Monitoring", "green")},
]

CLAIM_DETAILS = {
    "JALA-HAN-089": {
        "title": "Sindikat Ring #JALA-HAN-089",
        "typology": ("Phantom Billing", "amber"),
        "flag": "AUTO-FLAGGED (96%)",
        "profile": [
            ("Fasilitas Kesehatan", "Klinik Utama Pratama X + 4 Cabang"),
            ("Periode Observasi", "Q3 2024 (Jul - Sep)"),
            ("Total Klaim Anomali", "412 klaim", "red"),
            ("Keterikatan Metapath", "P-D-F-C Synchronous", "teal"),
        ],
        "freq_labels": ["01 Agu", "15 Agu", "28-30 Agu (Spike)", "10 Sep", "30 Sep"],
        "freq_baseline": [14, 16, 21, 15, 13],
        "freq_spike": [15, 22, 142, 38, 16],
        "peak": "142/hr",
        "why": "Cluster flagged for Phantom Billing due to an unnatural spatial-temporal surge of claims "
               "from non-domicile patient identities without prior primary care referral records. "
               "Heterogeneous Graph Attention Network (HAN) cluster scoring revealed an abnormal metapath "
               "concentration of 96%, indicating synchronized synthetic claim submissions across "
               "affiliated facilities.",
        "why_note": "Detected via graph cluster analysis — Network Risk Score: 96%.",
        "evidence": [
            ("👥", "Synchronous Patient NIK", "92% NIK terdaftar di luar radius faskes 35km", ("Anomali", "red")),
            ("🕐", "Submission Window", "Batch terkirim serentak dalam rentang 180 detik", ("Sinkronisasi", "amber")),
            ("🪪", "SIP Dokter Penanggung Jawab", "1 dokter tercatat praktik bersamaan di 4 lokasi", ("Kritis", "red")),
        ],
    },
}

DEFAULT_DETAIL = {
    "typology": ("Phantom Billing", "amber"),
    "flag": "AUTO-FLAGGED",
    "profile": [
        ("Fasilitas Kesehatan", "Entitas jaringan terafiliasi"),
        ("Periode Observasi", "Q3 2024 (Jul - Sep)"),
        ("Total Klaim Anomali", "— klaim", "red"),
        ("Keterikatan Metapath", "P-D-F Synchronous", "teal"),
    ],
    "freq_labels": ["01 Agu", "15 Agu", "28-30 Agu (Spike)", "10 Sep", "30 Sep"],
    "freq_baseline": [12, 14, 18, 13, 12],
    "freq_spike": [13, 20, 96, 31, 14],
    "peak": "96/hr",
    "why": "Cluster flagged by the Heterogeneous Graph Attention Network (HAN) for anomalous metapath "
           "concentration and synchronized claim submission patterns across affiliated entities.",
    "why_note": "Detected via graph cluster analysis.",
    "evidence": [
        ("👥", "Synchronous Patient NIK", "NIK terdaftar di luar radius faskes", ("Anomali", "red")),
        ("🕐", "Submission Window", "Batch terkirim dalam rentang sempit", ("Sinkronisasi", "amber")),
    ],
}

AUDIT_CLUSTER = {
    "name": "Sindikat Ring #JALA-HAN-089",
    "flag": "AUTO-FLAGGED (96%)",
    "typology": ("Phantom Billing", "amber"),
    "algo": "Deteksi Algoritma: HAN Subgraph Partitioning v2.4 (GNN Attention Score: 0.9612)",
    "score": 96,
    "score_note": "Kategori: Sangat Tinggi",
    "cards": [
        ("Faskes Terkait", "5 Faskes Terkait", "Klinik Utama Pratama X + 4 Jejaring Rujukan", "dark"),
        ("Potensi Klaim Anomali", "412 Klaim Anomali", "Est. Rp 1.482.000.000,-", "red"),
        ("Pola Metapath (Graph HAN)", "P-D-F-C Synchronous", "Spatial-temporal anomaly pattern", "dark"),
        ("Entitas Sentralitas Tertinggi", "dr. H.S., Sp.A (SIP.812)", "Degree Centrality: 0.884 (Cluster Core)", "teal"),
    ],
    "evidence": "Ratusan klaim fiktif teridentifikasi diajukan secara terkoordinasi dari peserta lintas "
                "domisili tanpa catatan riwayat antrean faskes primer. Terdapat kesamaan timestamp "
                "transmisi klaim (kurang dari 12 detik) antarfaskes berbeda untuk diagnosa kronis yang identik.",
    "density": "Graph Density: 0.74",
}

AUDIT_ACTIONS = [
    {
        "icon": "⚖", "icon_tone": "teal", "tag": ("Tindakan Preventif", "red"),
        "title": "Suspend Claims for This Ring",
        "body": "Freeze pembayaran klaim sementara & terbitkan instruksi penangguhan dana secara otomatis "
                "ke sistem perbendaharaan DJS.",
        "button": "Eksekusi Penangguhan (Freeze)", "button_kind": "primary",
        "note": "Otorisasi Level: Kepala Cabang / Verifikator Utama",
    },
    {
        "icon": "🔎", "icon_tone": "grey", "tag": ("Inspeksi On-Site", "grey"),
        "title": "Trigger Targeted Field Audit",
        "body": "Tugaskan Tim Pemeriksa Lapangan Khusus untuk audit fisik ke 5 faskes, sampling berkas "
                "rekam medis manual, dan wawancara peserta.",
        "button": "Bentuk Tim Pemeriksa Lapangan", "button_kind": "secondary",
        "note": "Penerbitan Surat Tugas (SP-Audit) Form 04",
    },
    {
        "icon": "🛡", "icon_tone": "grey", "tag": ("Kliring Kasus", "grey"),
        "title": "Dismiss as False Positive",
        "body": "Tandai sebagai anomali wajar (cth: bencana alam/rujukan massal terkonfirmasi) & simpan "
                "catatan evaluasi untuk kalibrasi bobot GNN.",
        "button": "Arsipkan & Kalibrasi Model", "button_kind": "secondary",
        "note": "Wajib menyertakan Berita Acara Klarifikasi",
    },
]

AUDIT_FASKES = [
    ("0192B004 · Klinik Utama Pratama X", "Kota Administrasi Jakarta Pusat", "FKTP", ("Origin Aggregator", "red"), 188, "Rp 684.200.000"),
    ("0192S011 · RS Harapan Medika Indah", "Kota Bekasi", "FKRTL (Tipe C)", ("Receiver Hub", "amber"), 104, "Rp 412.500.000"),
    ("0192B088 · Klinik Pratama Rawat Inap Z", "Kabupaten Bogor", "FKTP", ("Sub-Origin", "green"), 62, "Rp 198.300.000"),
    ("0192S032 · RS Citra Husada Mandiri", "Kota Depok", "FKRTL (Tipe D)", ("Sub-Receiver", "green"), 38, "Rp 115.000.000"),
    ("0192B104 · Klinik Medika Sejahtera Pratama", "Jakarta Selatan", "FKTP", ("Relay Node", "green"), 20, "Rp 72.000.000"),
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
            "Pemeriksaan linier berbasis batasan tarif INA-CBG statis tanpa riwayat relasi.",
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
            "Skor probabilitas kolusi real-time terintegrasi engine GNN v2.4.",
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
        ("🧠 Synthetic Graph Generator v2.4", "teal"),
        ("🔒 Zero PII Ingestion", "teal"),
        ("♻ Fully Pseudonymized Entities", "teal"),
    ],
    "owner": "Direktorat Jaminan Pelayanan Kesehatan | Tim Pencegahan Kecurangan (Fraud) BPJS Kesehatan",
}

FOOTER_STATUS = [
    ("green", "Cluster Engine: Running (0.04s)"),
    ("teal", "Graph Nodes Synced: 148,290 Klaim"),
    ("amber", "High-Risk Linkages: 41 FKTP/FKRTL"),
]
FOOTER_CUTOFF = "Data cut-off: 30-Sep-2024 23:59:59 WIB"

NAV_PAGES = [
    ("dashboard", "Dashboard"),
    ("network", "Network Graph"),
    ("risk", "Risk Ranking"),
    ("audit", "Audit Action"),
    ("about", "About"),
]

PAGE_TITLES = {
    "dashboard": "Dashboard",
    "network": "Network Graph",
    "risk": "Risk Ranking",
    "claim": "Claim Details",
    "audit": "Audit Action",
    "about": "About JALA",
}