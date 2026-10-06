"""Tes uji ketahanan: konfigurasi pembangkit, penanda klaim sah, fitur Repeat, dan konsistensi docs/robustness.json."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import robustness as rb
from core.detect import FEATURES, FEATURES_REPEAT, FEATURES_V1, assert_no_labels, build_features
from core.synthetic import DEFAULT, SEED, SHIFTED, WorldConfig, evasive_config, generate_world

ROB = Path(__file__).resolve().parent.parent / "docs" / "robustness.json"


# ---------- konfigurasi pembangkit ----------
def test_default_config_reproduces_default_world():
    a, b = generate_world(seed=7), generate_world(seed=7, cfg=WorldConfig())
    pd.testing.assert_frame_equal(a.claims, b.claims)
    pd.testing.assert_frame_equal(a.labels, b.labels)


def test_evasive_level_zero_is_default_and_level_one_differs():
    assert evasive_config(0) == DEFAULT
    e = evasive_config(1)
    assert e.burst_submit_jitter > 60 and e.burst_visit_window > 1800   # lolos jendela ±60 dtk dan ±30 menit
    assert e.fraud_overcap_p == 0 and e.ghost_n > DEFAULT.ghost_n and e.ring_doc_own_p > 0


def test_shifted_world_is_a_different_distribution():
    a, b = generate_world(seed=7), generate_world(seed=7, cfg=SHIFTED)
    assert len(b.claims) != len(a.claims)
    assert set(b.labels.typology[b.labels.is_fraud == 1]) == {"phantom", "repeat", "selfref"}


def test_legit_kind_only_on_legit_claims_and_hidden_from_detector():
    w = generate_world(seed=7)
    assert (w.labels.legit_kind[w.labels.is_fraud == 1] == "").all()
    assert {"dialisis", "ugd_ulang", "batch_malam_rs", "dokter_dua_praktik", "bencana"} <= set(w.labels.legit_kind)
    assert "legit_kind" not in w.claims.columns
    with pytest.raises(ValueError):
        assert_no_labels(w.claims.assign(legit_kind="x"))


# ---------- fitur Repeat Billing ----------
def test_repeat_feature_lists():
    assert FEATURES == FEATURES_V1 + FEATURES_REPEAT and len(FEATURES_V1) == 19 and len(FEATURES) == 22


def _rows(rows):
    c = pd.DataFrame(rows, columns=["claim_id", "faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_ts",
                                    "submit_ts", "referral_from_faskes", "referral_from_doctor"])
    c["visit_ts"], c["submit_ts"] = pd.to_datetime(c.visit_ts), pd.to_datetime(c.submit_ts)
    f = pd.DataFrame({"faskes_id": ["A", "B"], "type": ["klinik"] * 2, "region": ["R1"] * 2, "capacity": [25] * 2})
    p = pd.DataFrame({"patient_id": ["p1"], "home_region": ["R1"]})
    a = pd.DataFrame([("d1", "A"), ("d2", "B")], columns=["doctor_id", "faskes_id"])
    return c, f, a, p


def test_tarif_match_and_cross_pair_features():
    r = [("C1", "A", "d1", "p1", "M54.5", 200_000, "2026-07-01 09:00", "2026-07-01 12:00", None, None),
         ("C2", "B", "d2", "p1", "M54.5", 202_000, "2026-07-01 15:00", "2026-07-01 18:00", None, None),
         ("C3", "B", "d2", "p1", "M54.5", 150_000, "2026-07-20 09:00", "2026-07-20 12:00", None, None)]
    X = build_features(*_rows(r))
    assert X.loc["C2", "f_tarif_match_prev"] == pytest.approx(0.01)       # selisih 1%
    assert X.loc["C2", "f_dup_pair_cross"] == 1                           # A -> B, lintas faskes
    assert X.loc["C1", "f_tarif_match_prev"] == 1.0 and X.loc["C3", "f_tarif_match_prev"] == 1.0   # tanpa klaim ulang < 48 jam
    assert X.loc["C3", "f_dup_pair_cross"] == 0


# ---------- metrik ----------
def test_block_r_precision_and_per_typology():
    y = np.array([1, 1, 0, 0, 0, 0])
    typ = np.array(["phantom", "repeat", "", "", "", ""])
    b = rb._block(y, np.array([.9, .8, .3, .2, .1, .0]), typ)
    assert b["r_precision"] == pytest.approx(1.0) and b["auc"] == pytest.approx(1.0)
    assert set(b["per_typology"]) == {"phantom", "repeat"}


def test_false_positive_breakdown_counts():
    y = np.array([1, 0, 0, 0, 1, 0])
    s = np.array([.9, .8, .7, .1, .6, .0])
    kind = np.array(["", "dialisis", "dialisis", "bencana", "", "bencana"])
    p = rb.Prepared(None, None, y, np.array([""] * 6), kind, np.zeros(6), np.zeros(6))
    fp = rb.false_positives(p, s, k=3)
    assert fp["fraud_di_top_k"] == 1 and fp["sah_di_top_k"] == 2
    assert fp["per_jenis_sah"]["dialisis"]["salah_ditandai"] == 2
    assert fp["per_jenis_sah"]["bencana"]["salah_ditandai"] == 0


def test_feature_groups_partition_all_features():
    flat = rb.G_PER_CLAIM + rb.G_ENTITY + rb.G_RELATIONAL
    assert sorted(flat) == sorted(FEATURES) and len(flat) == len(set(flat))


# ---------- docs/robustness.json: ada, utuh, dan tidak basi ----------
@pytest.fixture(scope="module")
def saved():
    assert ROB.exists(), "jalankan: python -m core.robustness --json docs/robustness.json"
    return json.loads(ROB.read_text(encoding="utf-8"))


def test_saved_results_have_expected_structure(saved):
    for k in ("meta", "main", "ablation", "transfer", "evasion", "false_positives", "repeat_before_after", "caveats"):
        assert k in saved
    assert [e["level"] for e in saved["evasion"]] == list(rb.LEVELS)
    assert len(saved["repeat_before_after"]["multi_seed"]["per_seed"]) == 5


def test_saved_results_support_the_claims_shown_on_screen(saved):
    stages = list(saved["ablation"]["bertahap"].values())
    assert stages[2]["ap"] > stages[0]["ap"] + 0.3                                  # jaringan + agregat jauh di atas per-klaim saja
    assert stages[2]["per_typology"]["selfref"]["ap"] > stages[1]["per_typology"]["selfref"]["ap"] + 0.2
    ev = saved["evasion"]
    assert ev[-1]["model_beku"]["r_precision"] < ev[0]["model_beku"]["r_precision"]   # menghindar memang menurunkan kinerja
    assert all(e["model_beku"]["r_precision"] > e["rules"]["r_precision"] for e in ev)
    assert saved["transfer"]["A_ke_B"]["jala_transfer"]["auc"] > saved["transfer"]["A_ke_B"]["rules"]["auc"] + 0.2
    ms = saved["repeat_before_after"]["multi_seed"]["mean"]
    assert ms["v2"]["ap_repeat"] > ms["v1"]["ap_repeat"]


def test_saved_main_matches_fresh_run(saved):
    """Penjaga berkas basi: hitung ulang dunia utama dan bandingkan dengan yang tersimpan."""
    p = rb.prepare(generate_world(SEED))
    fresh = rb._block(p.y, rb._score_world(p, FEATURES, SEED), p.typ)
    assert fresh["auc"] == pytest.approx(saved["main"]["auc"], abs=0.01)
    assert fresh["ap"] == pytest.approx(saved["main"]["ap"], abs=0.03)
