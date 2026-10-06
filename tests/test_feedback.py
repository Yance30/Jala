"""Loop verifikator: dismiss menurunkan skor, peringkat berubah, klaster serupa ikut turun (core/feedback.py)."""
import inspect

import pytest

from core import feedback as F

FP = "JALA-F006"      # klaster dialisis yang salah tandai pada dunia default
FP_SIMILAR = "JALA-F044"


@pytest.fixture(scope="module")
def lv(engine):
    return engine[1]


def test_no_feedback_returns_same_object(lv):
    assert F.adjust(lv, {}) is lv and F.adjust(lv, None) is lv


def test_record_rejects_unknown_verdict():
    with pytest.raises(ValueError):
        F.record({}, "X", "hapus")


def test_dismiss_lowers_score_and_rank(lv):
    adj = F.adjust(lv, F.record({}, FP, "dismiss", at="t"))
    c, b = adj.by_id[FP], lv.by_id[FP]
    assert c["score"] == round(b["score"] * F.DISMISS_FACTOR) and c["score_base"] == b["score"]
    rank = lambda L, cid: [x["id"] for x in L.clusters].index(cid)
    assert rank(adj, FP) > rank(lv, FP)
    assert c["fb"]["kind"] == "dismiss"


def test_similar_pattern_cluster_is_lowered_with_reason(lv):
    adj = F.adjust(lv, F.record({}, FP, "dismiss", at="t"))
    s = adj.by_id[FP_SIMILAR]
    assert s["score"] < lv.by_id[FP_SIMILAR]["score"]
    assert s["fb"]["kind"] == "similar" and s["fb"]["source"] == FP and s["fb"]["sim"] >= F.SIM_THRESHOLD
    assert s["score"] >= round(lv.by_id[FP_SIMILAR]["score"] * (1 - F.SIMILAR_MAX_DROP))   # penurunan terbatas


def test_only_dismissed_or_similar_clusters_change(lv):
    adj = F.adjust(lv, F.record({}, FP, "dismiss", at="t"))
    for c in adj.clusters:
        if c["id"] not in (FP, FP_SIMILAR):
            assert c["score"] == lv.by_id[c["id"]]["score"] and c["fb"] is None, c["id"]


def test_confirmed_cluster_is_protected_from_similarity_drop(lv):
    fb = F.record(F.record({}, FP, "dismiss", at="t"), FP_SIMILAR, "confirm", at="t")
    adj = F.adjust(lv, fb)
    assert adj.by_id[FP_SIMILAR]["score"] == lv.by_id[FP_SIMILAR]["score"]
    assert adj.by_id[FP_SIMILAR]["fb"]["kind"] == "confirm"


def test_undo_restores_original_scores(lv):
    fb = F.record({}, FP, "dismiss", at="t")
    back = F.adjust(lv, F.undo(fb, FP))
    assert [(c["id"], c["score"]) for c in back.clusters] == [(c["id"], c["score"]) for c in lv.clusters]


def test_scores_stay_valid_and_list_stays_sorted(lv):
    fb = {}
    for c in lv.clusters:
        fb = F.record(fb, c["id"], "dismiss", at="t")
        adj = F.adjust(lv, fb)
        sc = [x["score"] for x in adj.clusters]
        assert all(isinstance(s, int) and 0 <= s <= 100 for s in sc) and sc == sorted(sc, reverse=True)


def test_changes_lists_dismissed_first_and_describes_ranks(lv):
    adj = F.adjust(lv, F.record({}, FP, "dismiss", at="t"))
    ch = F.changes(lv, adj)
    assert ch[0]["id"] == FP and ch[0]["kind"] == "dismiss"
    assert {x["id"] for x in ch} >= {FP, FP_SIMILAR}
    text = F.describe(ch[0])
    assert FP in text and "→" in text
    assert "tetap" in F.describe({**ch[0], "rank_before": 3, "rank_after": 3})


def test_loop_improves_queue_precision_without_demoting_real_fraud(engine):
    w, lv = engine
    res = F.evaluate_loop(lv, w)
    prec = [s["precision"] for s in res["steps"]]
    assert prec == sorted(prec) and prec[-1] == 1.0 and prec[0] < prec[-1]
    assert all(s["fraud_clusters_demoted"] == 0 for s in res["steps"])
    assert res["steps"][-1]["reviews_to_last_fraud"] <= res["steps"][0]["reviews_to_last_fraud"]


def test_wrong_dismissal_of_real_fraud_demotes_peers_but_never_hides_them(engine):
    """Keterbatasan yang diakui: dismiss keliru pada cincin fraud menurunkan cincin serupa, tetapi
    klaster tetap terlihat (tidak dihapus) dan bisa dibatalkan."""
    w, lv = engine
    ring = next(c["id"] for c in lv.clusters if c["typology"] == "Phantom Billing")
    adj = F.adjust(lv, F.record({}, ring, "dismiss", at="t"))
    peers = [c for c in adj.clusters if c["fb"] and c["fb"]["kind"] == "similar"]
    assert peers and len(adj.clusters) == len(lv.clusters)
    assert all(c["score"] >= 50 for c in peers)
    restored = F.adjust(lv, F.undo(F.record({}, ring, "dismiss", at="t"), ring))
    assert [c["score"] for c in restored.clusters] == [c["score"] for c in lv.clusters]


def test_feedback_never_reads_labels_outside_evaluate_loop():
    src = inspect.getsource(F).replace(inspect.getsource(F.evaluate_loop), "")
    assert ".labels" not in src and "is_fraud" not in src
