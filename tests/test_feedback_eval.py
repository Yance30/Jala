"""Evaluasi sensitivitas wrong-dismissal pada loop umpan balik (core/feedback_eval.py)."""
import pytest

from core import feedback_eval as fe
from core.live import AUTO_FLAG


@pytest.fixture(scope="module")
def result(engine):
    world, live = engine
    return fe.evaluate_wrong_dismissal(live, world, error_rates=(.1, .2), repeats=12, seed=2026)


def test_structure_and_ranges(result):
    assert set(result) == {"baseline_precision", "n_flagged_clusters", "n_fraud_flagged", "scenarios", "caveat"}
    assert 0.0 <= result["baseline_precision"] <= 1.0
    assert 0 <= result["n_fraud_flagged"] <= result["n_flagged_clusters"]
    assert result["caveat"].strip()
    assert [s["error_rate"] for s in result["scenarios"]] == [.1, .2]
    for s in result["scenarios"]:
        assert {"error_rate", "repeats", "precision_mean", "precision_p10", "precision_p90",
                "fraud_clusters_demoted_mean", "fraud_clusters_dismissed_mean"} <= set(s)
        assert s["repeats"] == 12
        assert 0.0 <= s["precision_p10"] <= s["precision_mean"] <= s["precision_p90"] <= 1.0


def test_flagged_count_and_baseline_match_live(result, engine):
    """Angka yang dilaporkan harus cocok dengan definisi flagged di core.live."""
    _, live = engine
    flagged = [c for c in live.clusters if c["score"] >= AUTO_FLAG]
    assert result["n_flagged_clusters"] == len(flagged)
    if flagged:
        assert result["baseline_precision"] == pytest.approx(
            result["n_fraud_flagged"] / result["n_flagged_clusters"])


def test_wrong_dismissal_scales_with_error_rate(result):
    """Semakin tinggi tingkat salah-dismiss, semakin banyak klaster fraud yang terdampak."""
    dismissed = [s["fraud_clusters_dismissed_mean"] for s in result["scenarios"]]
    assert dismissed == sorted(dismissed)                       # monoton naik terhadap error_rate
    assert all(0.0 <= d <= result["n_fraud_flagged"] for d in dismissed)
    demoted = [s["fraud_clusters_demoted_mean"] for s in result["scenarios"]]
    assert demoted == sorted(demoted)


def test_deterministic_for_fixed_seed(result, engine):
    world, live = engine
    again = fe.evaluate_wrong_dismissal(live, world, error_rates=(.1, .2), repeats=12, seed=2026)
    assert again == result
