import pandas as pd
import pytest

from core.case_context import build, evidence
from core.review_queue import prepare
from core import batch_store
from components.case_context import figure


def data():
    return pd.DataFrame({
        "claim_id": ["a", "b", "c", "d", "e"],
        "patient_id": ["X", "X", "P3", "P4", "X"],
        "doctor_id": ["X", "D2", "D3", "D4", "D5"],
        "faskes_id": ["X", "F2", "F3", "X", "F5"],
        "icd": ["I10"] * 5, "tarif": [100.] * 5,
        "visit_ts": pd.to_datetime(["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-12-01"]),
        "submit_ts": pd.to_datetime(["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-12-02"]),
        "referral_from_doctor": [None, None, "X", None, None],
        "referral_from_faskes": [None, None, "X", None, None],
    })


def test_links_are_observed_and_time_bounded():
    context = build(data(), "a")
    assert set(context["related"].claim_id) == {"a", "b", "c"}
    assert context["total_tariff"] == 300
    assert {("Peserta", "X"), ("Dokter", "X"), ("Faskes", "X")} <= set(context["nodes"])
    assert any(label == "dokter perujuk" for _, _, label in context["edges"])
    assert len(figure(context).data) == 6


def test_graph_cap_preserves_focus_and_full_timeline():
    context = build(data(), "c", graph_limit=1)
    assert ("Klaim", "c") in context["nodes"]
    assert context["graph_claims"] == 1 and context["omitted"] > 0
    assert len(context["related"]) > context["graph_claims"]
    with pytest.raises(ValueError):
        build(data(), "absent")


def test_legacy_batch_without_referrals_still_works():
    context = build(data().drop(columns=["referral_from_doctor", "referral_from_faskes"]), "a")
    assert not context["referral_available"]
    assert set(context["related"].claim_id) == {"a", "b"}


def test_persisted_batch_keeps_referrals_and_exports_only_related_reviews():
    claims = data()
    scores = pd.DataFrame({"claim_id": claims.claim_id, "priority_score": [10.] * 5})
    queue = batch_store.save_queue(prepare(claims, scores, {"version": "test"}))
    loaded = batch_store.load_queue(queue["id"])
    context = build(loaded["claims"], "a")
    assert set(context["related"].claim_id) == {"a", "b", "c"}
    loaded["events"] = [{"claim_id": "a"}, {"claim_id": "d"}]
    report = evidence(loaded, context)
    assert report["review_events"] == [{"claim_id": "a"}]
    assert len(report["claims"]) == 3
