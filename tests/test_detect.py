import pandas as pd
import pytest

from core.detect import FEATURES, assert_no_labels, build_features, explain, rule_flags
from core.synthetic import generate_world


@pytest.fixture(scope="module")
def world():
    return generate_world(seed=7)


@pytest.fixture(scope="module")
def feats(world):
    return build_features(world.claims, world.faskes, world.affiliations, world.patients)


def test_label_columns_rejected(world):
    with pytest.raises(ValueError):
        assert_no_labels(world.claims.merge(world.labels, on="claim_id"))
    with pytest.raises(ValueError):
        build_features(world.claims.merge(world.labels, on="claim_id"), world.faskes,
                       world.affiliations, world.patients)


def test_feature_matrix_shape_and_no_nan(world, feats):
    assert list(feats.columns) == FEATURES
    assert len(feats) == len(world.claims)
    assert not feats.isna().any().any()


def test_detect_module_never_reads_labels():
    """Penjaga statis: core/detect.py tidak boleh mengakses World.labels."""
    import inspect
    import core.detect as det
    src = inspect.getsource(det)
    assert ".labels" not in src and "labels[" not in src
    assert "synthetic import ICD_CAP" in src          # satu-satunya impor dari pembangkit: tabel plafon, bukan label
    params = inspect.signature(det.build_features).parameters
    assert list(params) == ["claims", "faskes", "affiliations", "patients"]


def _tiny(rows, aff=None):
    claims = pd.DataFrame(rows, columns=["claim_id", "faskes_id", "doctor_id", "patient_id", "icd", "tarif",
                                         "visit_ts", "submit_ts", "referral_from_faskes", "referral_from_doctor"])
    claims["visit_ts"] = pd.to_datetime(claims.visit_ts)
    claims["submit_ts"] = pd.to_datetime(claims.submit_ts)
    faskes = pd.DataFrame({"faskes_id": ["A", "B"], "type": ["klinik", "klinik"], "region": ["R1", "R1"], "capacity": [25, 25]})
    patients = pd.DataFrame({"patient_id": ["p1", "p2"], "home_region": ["R1", "R2"]})
    affs = pd.DataFrame(aff or [("d1", "A"), ("d1", "B")], columns=["doctor_id", "faskes_id"])
    return claims, faskes, affs, patients


def test_doctor_concurrency_detected_and_shifts_not():
    base = ("C1", "A", "d1", "p1", "I10", 100_000, "2026-07-01 09:00", "2026-07-01 10:00", None, None)
    same_hour = ("C2", "B", "d1", "p2", "I10", 100_000, "2026-07-01 09:10", "2026-07-01 10:00", None, None)
    next_day = ("C3", "B", "d1", "p2", "I10", 100_000, "2026-07-02 14:00", "2026-07-02 15:00", None, None)
    X = build_features(*_tiny([base, same_hour, next_day]))
    assert X.loc["C1", "f_doc_conc"] == 1 and X.loc["C2", "f_doc_conc"] == 1
    assert X.loc["C3", "f_doc_conc"] == 0


def test_repeat_gap_and_cross_faskes():
    r = [("C1", "A", "d1", "p1", "M54.5", 200_000, "2026-07-01 09:00", "2026-07-01 12:00", None, None),
         ("C2", "B", "d1", "p1", "M54.5", 200_000, "2026-07-01 15:00", "2026-07-01 18:00", None, None),
         ("C3", "B", "d1", "p1", "M54.5", 200_000, "2026-07-20 09:00", "2026-07-20 12:00", None, None)]
    X = build_features(*_tiny(r))
    assert X.loc["C2", "f_dup_recent"] == 1 and X.loc["C2", "f_dup_cross"] == 1
    assert X.loc["C2", "f_gap_prev_h"] == pytest.approx(6.0)
    assert X.loc["C1", "f_dup_recent"] == 0 and X.loc["C3", "f_dup_recent"] == 0


def test_internal_referral_flag():
    r = [("C1", "B", "d2", "p1", "I10", 100_000, "2026-07-01 09:00", "2026-07-01 10:00", "A", "d1"),
         ("C2", "B", "d2", "p2", "I10", 100_000, "2026-07-02 09:00", "2026-07-02 10:00", "A", "d9")]
    X = build_features(*_tiny(r))
    assert X.loc["C1", "f_ref_internal"] == 1   # d1 terdaftar di B
    assert X.loc["C2", "f_ref_internal"] == 0


def test_rule_baseline():
    r = [("C1", "A", "d1", "p1", "I10", 999_999, "2026-07-01 09:00", "2026-07-01 10:00", None, None),
         ("C2", "A", "d1", "p2", "I10", 100_000, "2026-07-01 09:00", "2026-07-01 10:00", None, None),
         ("C3", "A", "d1", "p2", "I10", 100_000, "2026-07-01 15:00", "2026-07-01 16:00", None, None)]
    f = rule_flags(_tiny(r)[0])
    assert f.loc["C1", "rule_over_cap"] == 1
    assert f.loc["C3", "rule_same_day_dup"] == 1 and f.loc["C2", "rule_same_day_dup"] == 0


def test_explain_maps_to_typology(feats):
    row = feats.iloc[0].copy()
    row[:] = 0
    row["f_dup_recent"], row["f_gap_prev_h"], row["f_dup_cross"] = 1, 5.0, 1
    out = explain(row)
    assert out["typology"] == "Repeat Billing" and "5 jam" in out["reasons"][0]
    row["f_dup_recent"] = 0
    assert explain(row)["typology"] is None
