"""Kontrak data minimal pipeline JALA: kolom yang HARUS ada agar `core.detect.build_features` jalan.

Data sintetis memenuhi kontrak ini. Bila panitia menyediakan data simulasi atau skema resmi, cukup tulis adapter
yang memetakan kolom data itu ke kontrak di bawah (lihat docs/pemetaan-data.md); `validate` memberi pesan jelas
kolom mana yang masih hilang.
"""
from __future__ import annotations

MINIMAL: dict[str, list[str]] = {
    "claims": ["claim_id", "faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_ts", "submit_ts",
               "referral_from_faskes", "referral_from_doctor"],
    "faskes": ["faskes_id", "type", "region", "capacity"],
    "affiliations": ["doctor_id", "faskes_id"],
    "patients": ["patient_id", "home_region"],
}


def missing(**frames) -> dict[str, list[str]]:
    """Kolom wajib yang hilang per tabel (kosong bila lengkap)."""
    out = {}
    for name, cols in MINIMAL.items():
        lacking = [c for c in cols if c not in frames[name].columns]
        if lacking:
            out[name] = lacking
    return out


def validate(claims, faskes, affiliations, patients) -> None:
    lacking = missing(claims=claims, faskes=faskes, affiliations=affiliations, patients=patients)
    if lacking:
        detail = "; ".join(f"{t}: {', '.join(c)}" for t, c in lacking.items())
        raise ValueError(f"Kolom wajib hilang (lihat docs/pemetaan-data.md): {detail}")
