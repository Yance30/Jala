"""Pembangkit dunia klaim sintetis berlabel untuk JALA.

Semua data fiktif (UU PDP: tidak ada data peserta nyata). Satu seed -> satu dunia yang sama.

Tiga tipologi fraud yang disisipkan (sesuai UI JALA):
  * phantom  : cincin klinik menagih peserta fiktif luar wilayah, serentak, oleh dokter yang
               tercatat praktik di banyak faskes pada jam yang sama.
  * repeat   : klaim berulang (pasien + diagnosis sama) dalam hitungan jam, antar-faskes konsorsium.
  * selfref  : dokter merujuk pasien kronis hampir selalu ke faskes tempat ia juga terdaftar,
               plus rujukan balik yang membentuk siklus.

Kasus sah yang sengaja dibuat mirip fraud (hard negatives), agar detektor tidak menang dengan curang:
  * RS mengirim klaim dalam batch malam hari (lonjakan serentak itu normal untuk RS)
  * klinik dialisis: pasien kembali tiap ~2,3 hari
  * kunjungan ulang UGD dalam 6-30 jam
  * lonjakan bencana: pasien luar wilayah (pengungsi) di satu wilayah selama 3 hari
  * dokter dengan dua tempat praktik (shift pagi/sore), termasuk dua dokter "daerah" yang
    wajar merujuk ~35% pasiennya ke RS tempat ia juga praktik
  * rujuk balik (PRB) RS -> faskes asal

`World.claims` hanya berisi kolom yang bisa diamati. Label ada di `World.labels` dan
TIDAK boleh dibaca oleh core.detect.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

SEED = 2026
PERIOD_START = pd.Timestamp("2026-07-01")
PERIOD_DAYS = 92
DAY = 86400
_START_WD = PERIOD_START.weekday()

REGIONS = [f"WIL-{i:02d}" for i in range(1, 9)]

# kode: (nama, tarif dasar Rp, plafon Rp) -- plafon bergaya INA-CBG, fiktif
ICD = {
    "I10": ("Hipertensi esensial", 180_000, 250_000),
    "E11.9": ("DM tipe 2", 220_000, 300_000),
    "J06.9": ("ISPA", 120_000, 170_000),
    "K29.7": ("Gastritis", 150_000, 210_000),
    "M54.5": ("Low back pain", 200_000, 280_000),
    "A09": ("Diare/gastroenteritis", 140_000, 200_000),
    "L30.9": ("Dermatitis", 110_000, 160_000),
    "Z00.0": ("Pemeriksaan umum", 90_000, 130_000),
    "M62.8": ("Fisioterapi", 130_000, 180_000),
    "N18.6": ("Hemodialisis", 950_000, 1_200_000),
    "I50": ("Gagal jantung", 1_800_000, 2_400_000),
    "J18.9": ("Pneumonia", 2_500_000, 3_300_000),
}
ICD_CAP = {k: v[2] for k, v in ICD.items()}

TYPE_CAPACITY = {"puskesmas": 60, "klinik": 25, "rs_c": 120, "rs_b": 220}
TYPE_LABEL = {"puskesmas": "Puskesmas", "klinik": "Klinik Pratama", "rs_c": "RS Tipe C", "rs_b": "RS Tipe B"}
TYPE_DOCS = {"puskesmas": 3, "klinik": 2, "rs_c": 5, "rs_b": 8}
_ICD_MIX = {
    "primary": (["I10", "E11.9", "J06.9", "K29.7", "A09", "L30.9", "Z00.0", "M54.5"],
                [.20, .13, .24, .11, .08, .07, .09, .08]),
    "rs": (["I10", "E11.9", "I50", "J18.9", "K29.7", "M54.5", "J06.9", "A09"],
           [.12, .13, .15, .17, .09, .10, .14, .10]),
}
CHRONIC_PHANTOM_ICD = ["E11.9", "I10", "M54.5"]


def _pick_icd(rng, kind: str) -> str:
    codes, p = _ICD_MIX[kind]
    return str(rng.choice(codes, p=np.array(p) / sum(p)))


@dataclass(frozen=True)
class WorldConfig:
    """Parameter pembangkit. Nilai default = dunia utama (hasilnya identik dengan sebelum ada konfigurasi).

    Dipakai untuk dua uji ketahanan di core.robustness:
      * SHIFTED  : distribusi bergeser (dunia B) untuk menguji transfer model dari dunia A
      * evasive_config(level): fraud yang sengaja menghindari fitur deteksi
    """
    n_oneoff: int = 13000
    home_p: float = 0.93              # peluang peserta sah berdomisili di wilayah faskes
    rs_batch_p: float = 0.7           # peluang RS mengirim klaim dalam batch malam
    pusk_batch_p: float = 0.4         # peluang puskesmas mengirim batch sore
    ghost_n: int = 40                 # peserta fiktif per cincin phantom
    ghost_local_p: float = 0.25       # peserta fiktif berdomisili setempat (bukan luar wilayah)
    phantom_bursts: int = 10          # jumlah kiriman serentak per cincin
    burst_lo: int = 8                 # klaim per kiriman serentak: [lo, hi)
    burst_hi: int = 13
    burst_visit_window: float = 1800.0   # detik: sebaran jam kunjungan dalam satu kiriman
    burst_submit_jitter: float = 5.0     # detik: sebaran jam kirim dalam satu kiriman
    phantom_quiet: int = 22           # klaim phantom "diam-diam" per cincin
    fraud_overcap_p: float = 0.10     # peluang klaim fraud melewati plafon tarif
    repeat_n: int = 45                # klaim asli per konsorsium repeat
    repeat_gap_scale: float = 1.0     # pengali jarak antar klaim ulang
    repeat_tail_p: float = 0.12       # peluang klaim ulang berjarak panjang
    repeat_tarif_jitter: float = 0.03  # selisih tarif klaim ulang vs klaim asli (+-)
    selfref_n: int = 70
    selfref_cycle_p: float = 0.30     # peluang rujukan balik membentuk siklus
    ring_doc_own_p: float = 0.0       # peluang klaim phantom memakai dokter faskesnya sendiri (bukan dokter cincin mana pun)


DEFAULT = WorldConfig()

# Dunia B: distribusi bergeser dari dunia utama (bukan data nyata, tetap keluarga pembangkit yang sama).
SHIFTED = WorldConfig(
    n_oneoff=9500, home_p=0.88, rs_batch_p=0.5, pusk_batch_p=0.25,
    ghost_n=30, ghost_local_p=0.40, phantom_bursts=8, burst_lo=6, burst_hi=11,
    burst_visit_window=2400.0, burst_submit_jitter=20.0, phantom_quiet=30, fraud_overcap_p=0.05,
    repeat_n=60, repeat_gap_scale=1.5, repeat_tail_p=0.20, repeat_tarif_jitter=0.08,
    selfref_n=55, selfref_cycle_p=0.20,
)


def evasive_config(level: float) -> WorldConfig:
    """level 0 = dunia utama; 1 = fraud paling menghindar: kiriman dipecah (>60 dtk), kunjungan tersebar
    melewati jendela 30 menit, peserta fiktif berdomisili setempat dan diperbanyak (tiap peserta jarang berulang),
    dokter cincin tidak lagi menagih lintas faskes, klaim ulang berjarak lebih lama, tarif tidak melewati plafon,
    kiriman lebih kecil, siklus rujukan balik berkurang."""
    L = float(min(max(level, 0.0), 1.0))
    return replace(
        DEFAULT,
        burst_submit_jitter=5.0 + L * 600.0, burst_visit_window=1800.0 + L * 4 * 3600.0,
        ghost_local_p=0.25 + L * 0.65, repeat_gap_scale=1.0 + L * 3.0, repeat_tail_p=0.12 + L * 0.30,
        fraud_overcap_p=0.10 * (1 - L), selfref_cycle_p=0.30 * (1 - L),
        ghost_n=int(round(40 + L * 360)), ring_doc_own_p=L * 0.8,
        burst_lo=8 - int(round(L * 5)), burst_hi=13 - int(round(L * 7)),
    )


@dataclass
class World:
    claims: pd.DataFrame        # kolom teramati saja
    faskes: pd.DataFrame
    affiliations: pd.DataFrame  # doctor_id, faskes_id (registrasi SIP)
    patients: pd.DataFrame      # patient_id, home_region
    labels: pd.DataFrame        # claim_id, is_fraud, typology, group, legit_kind  (TERSEMBUNYI dari detektor)
    faskes_group: dict = field(default_factory=dict)  # faskes_id -> grup fraud (untuk CV per kelompok)
    seed: int = SEED

    @property
    def fraud_faskes(self) -> set:
        m = self.claims.merge(self.labels, on="claim_id")
        return set(m.loc[m.is_fraud == 1, "faskes_id"])


class _Builder:
    def __init__(self, seed: int, cfg: WorldConfig = DEFAULT):
        self.cfg = cfg
        self.rng = np.random.default_rng(seed)
        self.rows: list[tuple] = []
        self.patients: list[tuple] = []     # (id, home_region)
        self.aff: list[tuple] = []
        self.shift: dict = {}               # (doctor, faskes) -> "am" | "pm"
        self.reserved: set = set()
        self.faskes_group: dict = {}
        self._pat_n = 0

    # ---------- util waktu ----------
    def visit_sec(self, shift="any") -> float:
        r = self.rng
        while True:
            d = int(r.integers(0, PERIOD_DAYS))
            if (_START_WD + d) % 7 < 5 or r.random() < 0.2:
                break
        lo, hi = {"any": (8, 16.5), "am": (8, 12.5), "pm": (12.75, 17)}[shift]
        return d * DAY + r.uniform(lo, hi) * 3600

    def daytime(self, sec: float) -> float | None:
        h = (sec % DAY) / 3600
        if not (7 <= h < 20):
            start = sec - sec % DAY + (DAY if h >= 20 else 0)
            sec = start + self.rng.uniform(8, 11) * 3600
        return sec if sec < PERIOD_DAYS * DAY else None

    def submit_sec(self, visit: float, ftype: str) -> float:
        r = self.rng
        if ftype in ("rs_c", "rs_b") and r.random() < self.cfg.rs_batch_p:           # batch malam RS
            return (visit // DAY + 1) * DAY + 23 * 3600 + r.uniform(0, 300)
        if ftype == "puskesmas" and r.random() < self.cfg.pusk_batch_p:                # batch sore puskesmas
            return (visit // DAY) * DAY + 16.5 * 3600 + r.uniform(0, 120)
        return visit + r.uniform(0.5, 48) * 3600

    def tarif(self, icd: str, over_cap_p: float) -> int:
        base, cap = ICD[icd][1], ICD[icd][2]
        if self.rng.random() < over_cap_p:
            return int(cap * self.rng.uniform(1.02, 1.2))
        return int(min(base * self.rng.lognormal(0, .12), cap * .99))

    def new_patient(self, region: str) -> str:
        self._pat_n += 1
        pid = f"P{self._pat_n:05d}"
        self.patients.append((pid, region))
        return pid

    def emit(self, f, d, p, icd, tarif, visit, submit, ref_f=None, ref_d=None, fraud=0, typ="", grp="", kind=""):
        self.rows.append((f, d, p, icd, tarif, visit, submit, ref_f, ref_d, fraud, typ, grp, kind))


def _make_faskes(rng) -> pd.DataFrame:
    types = ["puskesmas"] * 24 + ["klinik"] * 20 + ["rs_c"] * 10 + ["rs_b"] * 6
    regions = [REGIONS[i % 8] for i in range(24)] + list(rng.choice(REGIONS, 36))
    rows = []
    for i, (t, rg) in enumerate(zip(types, regions), start=1):
        rows.append((f"F{i:03d}", f"{TYPE_LABEL[t]} {i:02d}", t, rg, TYPE_CAPACITY[t]))
    return pd.DataFrame(rows, columns=["faskes_id", "name", "type", "region", "capacity"])


def generate_world(seed: int = SEED, n_oneoff: int = 13000, cfg: WorldConfig | None = None) -> World:
    cfg = cfg or WorldConfig(n_oneoff=n_oneoff)
    n_oneoff = cfg.n_oneoff
    b = _Builder(seed, cfg)
    rng = b.rng
    faskes = _make_faskes(rng)
    ftype = dict(zip(faskes.faskes_id, faskes.type))
    freg = dict(zip(faskes.faskes_id, faskes.region))
    by_type = {t: list(faskes.loc[faskes.type == t, "faskes_id"]) for t in TYPE_CAPACITY}

    # ---------- pasien ----------
    for _ in range(5000):
        b.new_patient(str(rng.choice(REGIONS)))
    pat_region = {p: r for p, r in b.patients}
    pool = {r: [p for p, rr in b.patients if rr == r] for r in REGIONS}

    def pick_patient(region: str) -> str:
        r = region if rng.random() < cfg.home_p else str(rng.choice(REGIONS))
        return str(rng.choice(pool[r]))

    # ---------- peran faskes ----------
    kl = list(rng.permutation(by_type["klinik"]))
    rc = list(rng.permutation(by_type["rs_c"]))
    phantom_sets = [kl[0:3], kl[3:6], kl[6:9]]
    repeat_sets = [[kl[9], rc[0]], [kl[10], rc[1]], [kl[11], kl[12]]]
    selfref_sets = [(kl[13], rc[2]), (kl[14], rc[3])]
    dialysis = [kl[15], rc[4]]
    legit_kl = [f for f in kl[16:]]
    legit_rc = [f for f in rc[5:]]

    # ---------- dokter ----------
    docs_by_f, d_n = {}, 0
    for f in faskes.itertuples():
        docs_by_f[f.faskes_id] = []
        for _ in range(TYPE_DOCS[f.type]):
            d_n += 1
            docs_by_f[f.faskes_id].append(f"D{d_n:03d}")
            b.aff.append((f"D{d_n:03d}", f.faskes_id))
    doc_home = {d: f for f, ds in docs_by_f.items() for d in ds}

    # ---------- dokter khusus (dicadangkan) ----------
    ring_docs = []
    for ri, fs in enumerate(phantom_sets):
        docs = [docs_by_f[f][0] for f in fs]
        ring_docs.append(docs)
        b.reserved.update(docs)
        for d in docs:                       # SIP terdaftar di seluruh faskes cincin
            for f in fs:
                if (d, f) not in b.aff:
                    b.aff.append((d, f))
        for f in fs:
            b.faskes_group[f] = f"phantom-{ri + 1}"
    for ci, fs in enumerate(repeat_sets):
        for f in fs:
            b.faskes_group[f] = f"repeat-{ci + 1}"
    selfref_doc = []
    for si, (a, bb) in enumerate(selfref_sets):
        d = docs_by_f[a][0]
        selfref_doc.append(d)
        b.reserved.add(d)
        b.aff.append((d, bb))
        b.faskes_group[a] = b.faskes_group[bb] = f"selfref-{si + 1}"
    rural = []                               # hard negative: dokter daerah, ~35% rujukan ke RS tempat ia praktik
    for k in range(2):
        a = legit_kl[k]
        same = [h for h in legit_rc if freg[h] == freg[a]] or legit_rc
        h = same[k % len(same)]
        d = docs_by_f[a][0]
        rural.append((d, a, h))
        b.reserved.add(d)
        b.aff.append((d, h))

    # ---------- dokter dua tempat praktik (legit, shift pagi/sore) ----------
    for d, home in doc_home.items():
        if d in b.reserved or rng.random() > 0.12:
            continue
        cands = [f for f in faskes.faskes_id if freg[f] == freg[home] and f != home]
        if cands:
            other = str(rng.choice(cands))
            b.aff.append((d, other))
            b.shift[(d, home)] = "am"
            b.shift[(d, other)] = "pm"
    docs_at = {f: [] for f in faskes.faskes_id}
    for d, f in b.aff:
        if b.shift.get((d, f)) is not None or doc_home.get(d) == f:
            docs_at[f].append(d)

    def pick_doc(f: str) -> str:
        return str(rng.choice(docs_by_f[f] if rng.random() < .8 else docs_at[f]))

    def free_doc(f: str) -> str:               # dokter yang bukan dokter khusus
        c = [d for d in docs_at[f] if d not in b.reserved]
        return str(rng.choice(c if c else docs_by_f[f]))

    referrers = {t: [f for f in by_type[t]] for t in ("puskesmas", "klinik")}

    # ---------- klaim sah: sekali kunjungan ----------
    w = faskes.capacity.values * rng.lognormal(0, .25, len(faskes))
    n_f = np.rint(w / w.sum() * n_oneoff).astype(int)

    def legit_claim(f, doc=None, icd=None, patient=None, ref=None):
        t = ftype[f]
        doc = doc or free_doc(f)
        icd = icd or _pick_icd(rng, "rs" if t.startswith("rs") else "primary")
        patient = patient or pick_patient(freg[f])
        v = b.visit_sec(b.shift.get((doc, f), "any"))
        ref_f, ref_d = ref if ref else (None, None)
        b.emit(f, doc, patient, icd, b.tarif(icd, .015), v, b.submit_sec(v, t), ref_f, ref_d)
        return patient, icd, v, doc

    for f, n in zip(faskes.faskes_id, n_f):
        t = ftype[f]
        for _ in range(n):
            ref = None
            if t.startswith("rs") and rng.random() < 0.4:
                pl = referrers["puskesmas"] + referrers["klinik"]
                same = [x for x in pl if freg[x] == freg[f]]
                rf = str(rng.choice(same if (same and rng.random() < .8) else pl))
                rd = str(rng.choice([d for d in docs_by_f[rf] if d not in b.reserved] or docs_by_f[rf]))
                ref = (rf, rd)
            p, icd, v, _d = legit_claim(f, ref=ref)
            if t != "klinik" and rng.random() < 0.012:                     # kunjungan ulang UGD
                v2 = b.daytime(v + rng.uniform(6, 30) * 3600)
                if v2:
                    d2 = free_doc(f)
                    b.emit(f, d2, p, icd, b.tarif(icd, .015), v2, b.submit_sec(v2, t), kind="ugd_ulang")
            if ref and rng.random() < 0.10:                                # rujuk balik (PRB)
                v2 = b.daytime(v + rng.uniform(7, 25) * DAY)
                if v2:
                    rf = ref[0]
                    b.emit(rf, free_doc(rf), p, icd, b.tarif(icd, .015), v2, b.submit_sec(v2, ftype[rf]),
                           f, free_doc(f), kind="rujuk_balik")

    # ---------- dokter daerah: rujukan sah yang banyak ke RS tempat ia praktik ----------
    for d, a, h in rural:
        others = [x for x in by_type["rs_c"] + by_type["rs_b"] if x != h]
        for i in range(60):
            dest = h if i < 21 else str(rng.choice(others))
            p = pick_patient(freg[a])
            icd = _pick_icd(rng, "rs")
            v = b.visit_sec()
            b.emit(dest, free_doc(dest), p, icd, b.tarif(icd, .015), v, b.submit_sec(v, ftype[dest]), a, d,
                   kind="dokter_daerah")

    # ---------- klaim sah: pasien kronis berulang ----------
    def series(f, p, icd, interval_days, jitter_h, hour_lo, hour_hi, kind=""):
        t0 = rng.uniform(0, interval_days) * DAY
        doc = free_doc(f)
        while t0 < PERIOD_DAYS * DAY:
            v = (t0 // DAY) * DAY + rng.uniform(hour_lo, hour_hi) * 3600 + rng.uniform(-jitter_h, jitter_h) * 3600
            if 0 <= v < PERIOD_DAYS * DAY:
                b.emit(f, doc, p, icd, b.tarif(icd, .01), v, b.submit_sec(v, ftype[f]), kind=kind)
            t0 += interval_days * DAY

    for k in range(12):                                         # dialisis 3x/minggu
        f = dialysis[k % 2]
        series(f, pick_patient(freg[f]), "N18.6", 2.33, 2, 7, 11, "dialisis")
    prim = by_type["puskesmas"] + by_type["klinik"]
    for _ in range(30):                                         # fisioterapi mingguan
        f = str(rng.choice(prim))
        series(f, pick_patient(freg[f]), "M62.8", 7, 3, 8, 15, "fisioterapi_mingguan")
    for _ in range(500):                                        # kontrol bulanan DM/HT
        f = str(rng.choice(by_type["puskesmas"]))
        series(f, pick_patient(freg[f]), str(rng.choice(["E11.9", "I10"])), 30, 48, 8, 14, "kontrol_bulanan")

    # ---------- lonjakan bencana (sah): pengungsi luar wilayah di WIL-03, hari 40-42 ----------
    for f in faskes.faskes_id:
        if freg[f] != "WIL-03" or ftype[f] == "klinik":
            continue
        for _ in range(60 if ftype[f] == "puskesmas" else 90):
            home = str(rng.choice([r for r in REGIONS if r != "WIL-03"]))
            p = b.new_patient(home)
            icd = str(rng.choice(["J06.9", "A09", "L30.9"]))
            for _k in range(1 + int(rng.random() < .3)):
                v = (40 + int(rng.integers(0, 3))) * DAY + rng.uniform(8, 17) * 3600
                b.emit(f, free_doc(f), p, icd, b.tarif(icd, .015), v, b.submit_sec(v, ftype[f]), kind="bencana")

    # ======================= FRAUD =======================
    # 1) Phantom billing
    for ri, fs in enumerate(phantom_sets):
        grp = f"phantom-{ri + 1}"
        regs = {freg[f] for f in fs}
        ghost_region = [r for r in REGIONS if r not in regs]
        # 25% peserta fiktif memakai domisili setempat agar tidak semudah "luar wilayah"
        ghosts = [b.new_patient(str(rng.choice(ghost_region)) if rng.random() < 1 - cfg.ghost_local_p else freg[fs[0]])
                  for _ in range(cfg.ghost_n)]
        for _ in range(cfg.phantom_bursts):
            while True:
                d = int(rng.integers(0, PERIOD_DAYS))
                if (_START_WD + d) % 7 < 5:
                    break
            base = d * DAY + rng.uniform(9, 15) * 3600
            sub = base + 2 * 3600 + rng.uniform(0, 90)
            for j in range(int(rng.integers(cfg.burst_lo, cfg.burst_hi))):
                f = fs[j % 3]
                v = base + rng.uniform(0, cfg.burst_visit_window)
                icd = str(rng.choice(CHRONIC_PHANTOM_ICD))
                doc_ = (ring_docs[ri][fs.index(f)] if cfg.ring_doc_own_p and rng.random() < cfg.ring_doc_own_p
                        else str(rng.choice(ring_docs[ri])))
                b.emit(f, doc_, str(rng.choice(ghosts)), icd, b.tarif(icd, cfg.fraud_overcap_p),
                       v, sub + rng.uniform(0, cfg.burst_submit_jitter), None, None, 1, "phantom", grp)

        for _ in range(cfg.phantom_quiet):                     # klaim "diam-diam": tidak serentak, dikirim sendiri
            f = str(rng.choice(fs))
            v = b.visit_sec()
            icd = str(rng.choice(CHRONIC_PHANTOM_ICD))
            doc_ = (ring_docs[ri][fs.index(f)] if cfg.ring_doc_own_p and rng.random() < cfg.ring_doc_own_p
                    else str(rng.choice(ring_docs[ri])))
            b.emit(f, doc_, str(rng.choice(ghosts)), icd, b.tarif(icd, cfg.fraud_overcap_p),
                   v, b.submit_sec(v, ftype[f]), None, None, 1, "phantom", grp)

    # 2) Repeat billing
    for ci, fs in enumerate(repeat_sets):
        grp = f"repeat-{ci + 1}"
        for _ in range(cfg.repeat_n):
            f0 = str(rng.choice(fs))
            p = pick_patient(freg[f0])
            icd = str(rng.choice(["M54.5", "E11.9", "I10", "K29.7", "M62.8"]))
            doc = free_doc(f0)
            v = b.visit_sec(b.shift.get((doc, f0), "any"))
            tar = b.tarif(icd, .10)
            b.emit(f0, doc, p, icd, tar, v, b.submit_sec(v, ftype[f0]), kind="asli_dalam_sindikat")  # klaim asli (sah)
            prev = v
            for _m in range(int(rng.choice([1, 2, 3], p=[.5, .35, .15]))):
                gap = (rng.uniform(0.5, 30 * cfg.repeat_gap_scale) if rng.random() < 1 - cfg.repeat_tail_p
                       else rng.uniform(30 * cfg.repeat_gap_scale, 44 * cfg.repeat_gap_scale))
                v2 = b.daytime(prev + gap * 3600)
                if not v2:
                    break
                f2 = str(rng.choice(fs))
                b.emit(f2, free_doc(f2), p, icd, int(tar * rng.uniform(1 - cfg.repeat_tarif_jitter, 1 + cfg.repeat_tarif_jitter)), v2,
                       b.submit_sec(v2, ftype[f2]), None, None, 1, "repeat", grp)
                prev = v2

    # 3) Self-referral
    for si, (a, hb) in enumerate(selfref_sets):
        grp, d = f"selfref-{si + 1}", selfref_doc[si]
        for _ in range(cfg.selfref_n):
            p = pick_patient(freg[a])
            icd = str(rng.choice(["E11.9", "I10"]))
            v = b.visit_sec()
            b.emit(a, d, p, icd, b.tarif(icd, .01), v, b.submit_sec(v, ftype[a]), kind="awal_dalam_sindikat")  # kunjungan awal (sah)
            v2 = b.daytime(v + rng.uniform(0.5, 3) * DAY)
            if v2:
                icd2 = str(rng.choice(["I50", "E11.9"]))
                b.emit(hb, free_doc(hb), p, icd2, b.tarif(icd2, cfg.fraud_overcap_p), v2, b.submit_sec(v2, ftype[hb]),
                       a, d, 1, "selfref", grp)
                if rng.random() < cfg.selfref_cycle_p:                                                 # rujukan balik membentuk siklus
                    v3 = b.daytime(v2 + rng.uniform(7, 20) * DAY)
                    if v3:
                        b.emit(a, d, p, icd, b.tarif(icd, cfg.fraud_overcap_p), v3, b.submit_sec(v3, ftype[a]),
                               hb, d, 1, "selfref", grp)
        others = [x for x in by_type["rs_c"] + by_type["rs_b"] if x != hb]
        for _ in range(3):                                                             # sedikit rujukan sah ke tempat lain
            dest = str(rng.choice(others))
            p, icd = pick_patient(freg[a]), str(rng.choice(["E11.9", "I10"]))
            v = b.visit_sec()
            b.emit(dest, free_doc(dest), p, icd, b.tarif(icd, .015), v, b.submit_sec(v, ftype[dest]), a, d,
                   kind="rujukan_sah_lain")

    # ---------- rakit ----------
    cols = ["faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_s", "submit_s",
            "referral_from_faskes", "referral_from_doctor", "is_fraud", "typology", "group", "legit_kind"]
    df = pd.DataFrame(b.rows, columns=cols)
    # kategori klaim sah yang mirip fraud, ditandai SETELAH data jadi (hanya untuk analisis false positive)
    hour = (df.submit_s % DAY) / 3600
    is_rs = df.faskes_id.map(ftype).isin(["rs_c", "rs_b"])
    dual = {d for d, _f in b.shift}
    empty = (df.legit_kind == "") & (df.is_fraud == 0)
    df.loc[empty & is_rs & (hour >= 23) & (hour < 23.1), "legit_kind"] = "batch_malam_rs"
    empty = (df.legit_kind == "") & (df.is_fraud == 0)
    df.loc[empty & (df.faskes_id.map(ftype) == "puskesmas") & (hour >= 16.5) & (hour < 16.55), "legit_kind"] = "batch_sore_puskesmas"
    empty = (df.legit_kind == "") & (df.is_fraud == 0)
    df.loc[empty & df.doctor_id.isin(dual), "legit_kind"] = "dokter_dua_praktik"
    df = df.sort_values(["visit_s", "submit_s"], kind="stable").reset_index(drop=True)
    df.insert(0, "claim_id", [f"C{i:06d}" for i in range(1, len(df) + 1)])
    df["visit_ts"] = PERIOD_START + pd.to_timedelta(df.visit_s, unit="s")
    df["submit_ts"] = PERIOD_START + pd.to_timedelta(df.submit_s, unit="s")
    obs = ["claim_id", "faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_ts", "submit_ts",
           "referral_from_faskes", "referral_from_doctor"]
    patients = pd.DataFrame(b.patients, columns=["patient_id", "home_region"])
    aff = pd.DataFrame(sorted(set(b.aff)), columns=["doctor_id", "faskes_id"])
    return World(
        claims=df[obs].copy(), faskes=faskes, affiliations=aff, patients=patients,
        labels=df[["claim_id", "is_fraud", "typology", "group", "legit_kind"]].copy(),
        faskes_group=dict(b.faskes_group), seed=seed,
    )


if __name__ == "__main__":
    w = generate_world()
    print(len(w.claims), "klaim;", int(w.labels.is_fraud.sum()), "fraud;",
          w.labels.typology.value_counts().to_dict())
