"""Tes lapisan data hidup (core/live.py): klaster dari skor nyata, tanpa label, dengan skema yang dipakai layar."""
import json

import pandas as pd
import pytest

from core import live as L
from core.detect import FEATURES
from core.evaluate import benchmark
from core.synthetic import generate_world


@pytest.fixture(scope="module")
def eng():
    w = generate_world()
    bm = benchmark(world=w)
    return w, bm, L.build(w, bm.scored)


def test_cluster_recovery_is_stable_within_known_range(eng):
    w, bm, lv = eng
    ev = L.evaluate_clusters(lv)
    # Louvain can split or merge one repeat group across dependency versions.
    # Keep the metric meaningful while allowing either observed partition.
    assert ev["recovered"] >= 7 and ev["n_groups"] == 8
    assert ev["recovered"] == sum(ev["per_group"].values())
    assert ev["flagged_precision"] > 0.8 and ev["flagged_recall"] > 0.7


def test_builder_never_reads_labels(eng):
    """Hanya fitur + skor yang boleh masuk; hasil harus sama walau semua kolom lain dibuang dari `scored`."""
    w, bm, lv = eng
    stripped = bm.scored[FEATURES + ["score_graph"]]
    lv2 = L.build(w, stripped)
    assert [c["id"] for c in lv2.clusters] == [c["id"] for c in lv.clusters]
    assert [c["score"] for c in lv2.clusters] == [c["score"] for c in lv.clusters]


def test_build_is_deterministic(eng):
    w, bm, lv = eng
    again = L.build(w, bm.scored)
    assert [(c["id"], c["score"], c["n"]) for c in again.clusters] == [(c["id"], c["score"], c["n"]) for c in lv.clusters]


def test_cluster_partition_is_disjoint_and_sorted(eng):
    _, _, lv = eng
    seen = set()
    for c in lv.clusters:
        assert not seen & set(c["faskes"])
        seen |= set(c["faskes"])
        assert c["n"] >= L.MIN_CLAIMS
    scores = [c["score"] for c in lv.clusters]
    assert scores == sorted(scores, reverse=True)


def test_screen_schemas_have_required_keys(eng):
    _, _, lv = eng
    cid = lv.clusters[0]["id"]
    for r in lv.risk_rows():
        assert {"id", "name", "subtitle", "status", "score", "conf", "metric", "typology", "why", "icon", "icon_tone"} <= set(r)
    for r in lv.triage_rows():
        assert {"id", "name", "nodes", "typology", "faskes", "volume", "value", "score", "status"} <= set(r)
    d = lv.detail(cid)
    assert {"title", "typology", "flag", "profile", "timeline", "peak", "why", "why_note", "evidence"} <= set(d)
    tl = d["timeline"]
    assert len(tl["labels"]) == len(tl["flagged"]) == len(tl["others"])
    assert sum(tl["flagged"]) == lv.by_id[cid]["n"]
    a = lv.audit(cid)
    assert a["n_claims"] == lv.by_id[cid]["n"] and len(a["faskes_rows"]) == len(lv.by_id[cid]["faskes"])
    assert len(lv.kpis()) == 3 and len(lv.dashboard_footer()) == 3
    labels, series = lv.trend()
    assert all(len(v) == len(labels) for v in series.values())


def test_graph_edges_reference_existing_nodes_and_is_json_safe(eng):
    _, _, lv = eng
    for c in lv.clusters:
        nodes, edges = lv.graph(c["id"])
        ids = {n["id"] for n in nodes}
        assert len(ids) == len(nodes)
        assert all(e["src"] in ids and e["dst"] in ids for e in edges)
        assert all(0 <= n["x"] <= 13.5 and 0 <= n["y"] <= 9 for n in nodes)
        assert any(n["risk"] for n in nodes) and any(not n["risk"] for n in nodes)   # klaster + pembanding normal
        json.dumps(nodes), json.dumps(edges)


def test_typology_guess_matches_what_was_injected(eng):
    """Tipologi dugaan (dari fitur) dibandingkan dengan tipologi yang disisipkan (label, hanya untuk menilai)."""
    w, _, lv = eng
    lab = w.labels.set_index("claim_id")
    mapping = {"phantom": "Phantom Billing", "repeat": "Repeat Billing", "selfref": "Self-Referral"}
    ok = tot = 0
    for c in lv.clusters:
        k = lab.loc[c["idx"]]
        if k.is_fraud.mean() < .5:
            continue
        main = k[k.is_fraud == 1].typology.value_counts().index[0]
        tot += 1
        ok += mapping[main] == c["typology"]
    # Depending on the graph partition, one repeat group can be split across clusters.
    assert tot in (8, 9) and ok == tot


def test_false_positive_clusters_are_disclosed_not_hidden(eng):
    """Klaster tanpa fraud ada (dialisis/UGD ulang mirip klaim berulang); jumlahnya dilaporkan, bukan disembunyikan."""
    w, _, lv = eng
    ev = L.evaluate_clusters(lv)
    assert ev["clusters_without_fraud"] >= 1
    lab = w.labels.set_index("claim_id")
    zero = [lab.loc[c["idx"]] for c in lv.clusters if lab.loc[c["idx"]].is_fraud.mean() == 0]
    pooled = sum(k.legit_kind.isin({"dialisis", "ugd_ulang"}).sum() for k in zero) / sum(len(k) for k in zero)
    assert pooled >= 0.6          # sumber salah tandai: klaim berulang yang sah


def test_search_finds_cluster_by_faskes_name(eng):
    _, _, lv = eng
    c = lv.clusters[0]
    name = lv.world.faskes.set_index("faskes_id").name[c["faskes"][0]]
    assert lv.find(name) == c["id"] and lv.find("tidak-ada-yang-begini") is None


def test_benign_explanations_read_only_observed_icd():
    """Penanda 'mungkin sah' murni dari kolom teramati (icd); spesifik, tidak memberi rasa aman palsu."""
    dia = pd.DataFrame({"icd": ["N18.6"] * 8 + ["J18.9"] * 2})
    out = L.benign_explanations(dia)
    assert len(out) == 1 and out[0]["marker"] == "dialisis_terjadwal"
    assert "80%" in out[0]["text"] and "N18.6" in out[0]["text"]
    # tanpa dominasi dialisis -> kosong (pola tidak spesifik tidak dipakai)
    assert L.benign_explanations(pd.DataFrame({"icd": ["J18.9"] * 10})) == []
    assert L.benign_explanations(pd.DataFrame({"icd": []})) == []


def test_benign_marker_flags_dialysis_false_positive_never_real_fraud(eng):
    """Penanda menyala pada klaster dialisis yang salah tandai, dan TIDAK pada klaster mayoritas fraud."""
    w, _, lv = eng
    lab = w.labels.set_index("claim_id")
    fired_on_fp = False
    for c in lv.clusters:
        markers = lv.benign(c["id"])
        fraud_share = float(lab.loc[c["idx"]].is_fraud.mean())
        if fraud_share >= 0.5:
            assert markers == [], f"{c['id']} mayoritas fraud tetapi diberi penanda penjelasan sah"
        elif markers:
            assert any(m["marker"] == "dialisis_terjadwal" for m in markers)
            fired_on_fp = True
    assert fired_on_fp, "dunia default seharusnya punya klaster dialisis salah-tandai yang diberi penanda"

