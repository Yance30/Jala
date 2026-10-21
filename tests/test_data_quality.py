import copy
import json

import pandas as pd
import pytest

from core.data_quality import feature_readiness, inspect, require_valid


@pytest.fixture
def tables():
    return dict(
        claims=pd.DataFrame([dict(claim_id="C1", faskes_id="F1", doctor_id="D1", patient_id="PRIVATE-ID",
                                 icd="I10", tarif=100., visit_ts=pd.Timestamp("2026-07-01"),
                                 submit_ts=pd.Timestamp("2026-07-02"), referral_from_faskes=None,
                                 referral_from_doctor="")]),
        faskes=pd.DataFrame([dict(faskes_id="F1", type="klinik", region="R1", capacity=25)]),
        affiliations=pd.DataFrame([dict(doctor_id="D1", faskes_id="F1")]),
        patients=pd.DataFrame([dict(patient_id="PRIVATE-ID", home_region="R1")]),
    )


def test_valid_input_and_no_mutation_or_identifiers_in_report(tables):
    before = copy.deepcopy(tables)
    report = require_valid(**tables)
    assert report["passed"]
    assert "PRIVATE-ID" not in json.dumps(report)
    for name in tables:
        pd.testing.assert_frame_equal(tables[name], before[name])


def test_duplicate_master_and_orphan_claim_are_rejected(tables):
    tables["patients"] = pd.concat([tables["patients"]] * 2, ignore_index=True)
    tables["claims"].loc[0, "faskes_id"] = "UNKNOWN"
    report = inspect(**tables)
    assert {i["code"] for i in report["issues"]} == {"duplicate_key", "unknown_reference"}
    with pytest.raises(ValueError, match="duplicate_key"):
        require_valid(**tables)


def test_invalid_values_and_chronology(tables):
    tables["claims"].loc[0, "tarif"] = float("inf")
    tables["faskes"].loc[0, "capacity"] = 0
    tables["claims"].loc[0, "submit_ts"] = pd.Timestamp("2026-06-30")
    report = inspect(**tables)
    assert sum(i["code"] == "invalid_number" for i in report["issues"]) == 2
    assert any(i["code"] == "invalid_chronology" for i in report["issues"])


def test_schema_errors_and_label_leakage_return_report(tables):
    tables["claims"] = tables["claims"].drop(columns="tarif").assign(is_fraud=True)
    assert {i["code"] for i in inspect(**tables)["issues"]} == {"missing_column", "label_leakage"}


def test_strings_are_not_silently_coerced(tables):
    tables["claims"]["submit_ts"] = "2026-07-02"
    tables["claims"]["tarif"] = "100"
    assert {i["code"] for i in inspect(**tables)["issues"]} == {"datetime_dtype", "numeric_dtype"}


def test_duplicate_columns_and_missing_values_are_reported(tables):
    tables["claims"].loc[0, "patient_id"] = " "
    assert any(i["code"] == "missing_value" for i in inspect(**tables)["issues"])
    tables["claims"] = pd.concat([tables["claims"], tables["claims"][["tarif"]]], axis=1)
    assert any(i["code"] == "duplicate_column" for i in inspect(**tables)["issues"])


def test_feature_readiness_does_not_overclaim_timestamp_precision(tables):
    rows = feature_readiness(tables["claims"], tariff_caps={"I10": 100})
    by_feature = {row["fitur"]: row for row in rows}
    assert "ketelitian menit belum dapat dipastikan" in by_feature["Konkurensi dokter lintas faskes"]["batas"]
    assert "ketelitian detik belum dapat dipastikan" in by_feature["Pengajuan serentak"]["batas"]

    tables["claims"]["visit_ts"] = pd.to_datetime(["2026-07-01 09:30"])
    tables["claims"]["submit_ts"] = pd.to_datetime(["2026-07-01 09:31"])
    rows = feature_readiness(tables["claims"], tariff_caps={"I10": 100})
    by_feature = {row["fitur"]: row for row in rows}
    assert "ketelitian menit tetap harus dikonfirmasi" in by_feature["Konkurensi dokter lintas faskes"]["batas"]
    assert "ketelitian detik tetap harus dikonfirmasi" in by_feature["Pengajuan serentak"]["batas"]
