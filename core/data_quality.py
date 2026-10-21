"""Structural data checks before modelling; not clinical or fraud validation.

Reports contain counts and column names, never participant IDs or row samples.
This inspector does not modify or silently repair its inputs.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

from core.contract import MINIMAL
from core.detect import LABEL_COLS


def inspect(claims, faskes, affiliations, patients) -> dict:
    frames = dict(claims=claims, faskes=faskes, affiliations=affiliations, patients=patients)
    issues = []

    def add(table, column, code, count, message):
        if count:
            issues.append(dict(table=table, column=column, code=code,
                               count=int(count), message=message))

    def blank(series):
        return series.isna() | series.astype(str).str.strip().eq("")

    for table, frame in frames.items():
        add(table, "", "empty_table", int(frame.empty), "Tabel kosong.")
        for column in MINIMAL[table]:
            add(table, column, "missing_column", int(column not in frame), "Kolom wajib belum tersedia.")
        for column in sorted(LABEL_COLS.intersection(frame.columns)):
            add(table, column, "label_leakage", 1, "Label evaluasi harus dipisahkan dari input detektor.")
        for column in frame.columns[frame.columns.duplicated()].unique():
            add(table, column, "duplicate_column", 1, "Nama kolom harus unik.")

    # A malformed schema cannot safely be indexed for the remaining checks.
    if not any(i["code"] in ("missing_column", "duplicate_column") for i in issues):
        for table, frame in frames.items():
            for column in MINIMAL[table]:
                if column not in ("referral_from_faskes", "referral_from_doctor"):
                    add(table, column, "missing_value", blank(frame[column]).sum(), "Nilai wajib kosong.")

        for table, keys in (("claims", ["claim_id"]), ("faskes", ["faskes_id"]),
                            ("patients", ["patient_id"]), ("affiliations", ["doctor_id", "faskes_id"])):
            add(table, ",".join(keys), "duplicate_key", frames[table].duplicated(keys).sum(),
                "Kunci duplikat dapat menggandakan hasil penggabungan atau fitur.")

        links = [("claims", "faskes_id", "faskes", "faskes_id"),
                 ("claims", "patient_id", "patients", "patient_id"),
                 ("affiliations", "faskes_id", "faskes", "faskes_id"),
                 ("claims", "doctor_id", "affiliations", "doctor_id"),
                 ("claims", "referral_from_faskes", "faskes", "faskes_id"),
                 ("claims", "referral_from_doctor", "affiliations", "doctor_id")]
        for table, column, target, key in links:
            values = frames[table][column]
            count = (~blank(values) & ~values.isin(frames[target][key])).sum()
            add(table, column, "unknown_reference", count, f"Referensi tidak ditemukan di {target}.{key}.")

        for table, column, allow_zero in (("claims", "tarif", True), ("faskes", "capacity", False)):
            values = frames[table][column]
            if not is_numeric_dtype(values):
                add(table, column, "numeric_dtype", 1, "Kolom harus bertipe numerik sebelum pemodelan.")
            else:
                number = values.to_numpy(dtype=float, na_value=np.nan)
                invalid = ~np.isfinite(number) | (number < 0 if allow_zero else number <= 0)
                add(table, column, "invalid_number", invalid.sum(),
                    "Nilai harus terbatas dan tidak negatif; kapasitas harus lebih besar dari nol.")

        dates_ready = True
        for column in ("visit_ts", "submit_ts"):
            if not is_datetime64_any_dtype(claims[column]):
                dates_ready = False
                add("claims", column, "datetime_dtype", 1, "Konversi waktu secara eksplisit sebelum pemodelan.")
        if dates_ready:
            try:
                count = (claims.submit_ts < claims.visit_ts).sum()
                add("claims", "submit_ts", "invalid_chronology", count, "Pengajuan mendahului waktu layanan.")
            except TypeError:
                add("claims", "submit_ts", "timezone_mismatch", 1, "Zona waktu layanan dan pengajuan tidak kompatibel.")

    return {"schema_version": 1, "passed": not issues,
            "rows": {name: len(frame) for name, frame in frames.items()}, "issues": issues,
            "scope": "Pemeriksaan struktur dan konsistensi data; bukan validasi klinis, kebenaran label, atau kepatuhan."}


def require_valid(claims, faskes, affiliations, patients) -> dict:
    """Optional gate for a future batch adapter; refuse invalid data without repairing it."""
    report = inspect(claims, faskes, affiliations, patients)
    if not report["passed"]:
        detail = "; ".join(f"{i['table']}.{i['column']}: {i['code']} ({i['count']})" for i in report["issues"])
        raise ValueError("Kualitas data belum memenuhi pemeriksaan: " + detail)
    return report


def require_time_resolution(claims):
    """Conservative abstention: date-only values cannot support this model."""
    missing = [column for column in ("visit_ts", "submit_ts")
               if claims[column].eq(claims[column].dt.normalize()).all()]
    if missing:
        raise ValueError("Data belum cukup untuk dinilai: " + ", ".join(missing) +
                         " hanya menunjukkan tanggal/tengah malam. Model memerlukan jam layanan "
                         "dan waktu pengajuan; jangan mengisi jam buatan.")


def feature_readiness(claims, *, tariff_caps) -> list[dict]:
    """Describe structural feature support without asserting source-field semantics."""
    def time_note(column, needed):
        values = claims[column]
        has_intraday = values.ne(values.dt.normalize()).any()
        if not has_intraday:
            return f"Nilai {column} hanya menunjukkan tengah malam; {needed} belum dapat dipastikan."
        return f"Ada nilai intrahari pada {column}; presisi {needed} tetap harus dikonfirmasi dari kamus sumber."

    return [
        dict(
            fitur="Jaringan peserta–kunjungan–faskes",
            struktur="Kolom tersedia",
            kebutuhan="patient_id, faskes_id, visit_ts",
            batas="Kesamaan ID lintas tabel/periode dan arti unit baris harus dikonfirmasi.",
        ),
        dict(
            fitur="Kunjungan berulang peserta–diagnosis",
            struktur="Kolom tersedia",
            kebutuhan="patient_id, icd, visit_ts",
            batas="Indikasi kunjungan berulang bukan bukti klaim atau pembayaran ganda.",
        ),
        dict(
            fitur="Konkurensi dokter lintas faskes",
            struktur="Belum cukup untuk dinilai" if claims.visit_ts.eq(claims.visit_ts.dt.normalize()).all() else "Kolom tersedia",
            kebutuhan="doctor_id, faskes_id, affiliations, visit_ts",
            batas=time_note("visit_ts", "ketelitian menit"),
        ),
        dict(
            fitur="Pengajuan serentak",
            struktur="Belum cukup untuk dinilai" if claims.submit_ts.eq(claims.submit_ts.dt.normalize()).all() else "Kolom tersedia",
            kebutuhan="faskes_id, submit_ts",
            batas=time_note("submit_ts", "ketelitian detik"),
        ),
        dict(
            fitur="Rujukan dan afiliasi",
            struktur="Kolom tersedia",
            kebutuhan="referral_from_faskes, referral_from_doctor, affiliations",
            batas="Keberadaan kolom tidak memverifikasi arti rujukan atau hubungan praktik.",
        ),
        dict(
            fitur="Anomali tarif",
            struktur="Kolom tersedia" if tariff_caps else "Referensi tarif kosong",
            kebutuhan="tarif, icd, tariff_caps",
            batas="Referensi tarif dalam paket belum tentu plafon resmi.",
        ),
    ]


if __name__ == "__main__":
    from core.synthetic import generate_world

    world = generate_world()
    report = inspect(world.claims, world.faskes, world.affiliations, world.patients)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
