"""Simulasi struktural 'bagaimana kalau dokter ini dikeluarkan' (core/whatif.py)."""
import inspect

from core import whatif


def _edges(G):
    return {tuple(sorted(e)) for e in G.edges}


def test_structure_matches_live_graph_for_every_cluster(engine):
    """Invarian: graf yang dihitung ulang tanpa menghapus apa pun sama dengan sisi antar-faskes di core.live."""
    w, lv = engine
    for c in lv.clusters:
        G = whatif.structure(lv.flagged.loc[c["idx"]])
        assert _edges(G) == {tuple(sorted(e[:2])) for e in c["fedges"]}, c["id"]


def test_self_referral_director_is_core_of_network(engine):
    w, lv = engine
    sr = [c for c in lv.clusters if c["typology"] == "Self-Referral"]
    assert sr
    for c in sr:
        top = whatif.rank_doctors(lv, c["id"])[0]
        assert top["role"] == "inti" and top["claims_share"] >= .9, c["id"]


def test_phantom_ring_does_not_hinge_on_a_single_doctor(engine):
    """Cincin dibagi beberapa dokter: mengeluarkan satu dokter tidak memecah klaster."""
    w, lv = engine
    for c in [c for c in lv.clusters if c["typology"] == "Phantom Billing"]:
        assert not any(r["split"] for r in whatif.rank_doctors(lv, c["id"])), c["id"]


def test_removal_never_adds_claims_or_weight(engine):
    w, lv = engine
    for c in lv.clusters:
        for r in whatif.rank_doctors(lv, c["id"]):
            assert 0 <= r["claims_removed"] <= r["claims_total"]
            assert r["weight_after"] <= r["weight_before"]
            assert 0 <= r["weight_lost_share"] <= 1 and 0 <= r["claims_share"] <= 1
            assert r["faskes_after"] <= r["faskes_before"]


def test_ranking_orders_core_before_peripheral(engine):
    w, lv = engine
    rank = {"inti": 0, "pendukung": 1, "periferal": 2}
    for c in lv.clusters:
        roles = [rank[r["role"]] for r in whatif.rank_doctors(lv, c["id"])]
        assert roles == sorted(roles), c["id"]


def test_doctor_outside_cluster_changes_nothing(engine):
    w, lv = engine
    r = whatif.evaluate_removal(lv, lv.clusters[0]["id"], "D-TIDAK-ADA")
    assert r["claims_removed"] == 0 and r["weight_lost_share"] == 0 and r["role"] == "periferal"
    assert r["components_before"] == r["components_after"]


def test_simulation_does_not_mutate_live(engine):
    w, lv = engine
    cid = lv.clusters[0]["id"]
    before = lv.flagged.copy()
    whatif.rank_doctors(lv, cid)
    assert before.equals(lv.flagged)


def test_verdict_text_is_human_readable(engine):
    w, lv = engine
    for c in lv.clusters[:3]:
        for r in whatif.rank_doctors(lv, c["id"], top=3):
            assert r["doctor"] in r["verdict"] and len(r["verdict"]) > 30


def test_whatif_never_reads_labels():
    src = inspect.getsource(whatif)
    assert ".labels" not in src and "is_fraud" not in src
