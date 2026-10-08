"""Penyamaran ID peserta untuk tampilan peran (core/privacy.py)."""
import copy

import pytest

from core import privacy


def test_mask_is_deterministic_and_wellformed():
    token = privacy.mask_participant_id("12345")
    assert token == privacy.mask_participant_id("12345")          # stabil antar-panggilan
    assert token.startswith("PESERTA-") and len(token) == len("PESERTA-") + 8
    body = token.split("-", 1)[1]
    assert body == body.upper() and all(c in "0123456789ABCDEF" for c in body)


def test_distinct_inputs_get_distinct_tokens():
    tokens = {privacy.mask_participant_id(v) for v in ("1", "2", "3", "p_1", "01")}
    assert len(tokens) == 5                                        # tidak bentrok untuk input berbeda


@pytest.fixture
def graph():
    nodes = [
        {"id": "p_1", "type": "pasien", "label": "Budi", "sub": "x"},
        {"id": "p_22", "type": "pasien", "label": "Sari", "sub": "y"},
        {"id": "f_A", "type": "faskes", "label": "Klinik A", "sub": "z"},
        {"id": "d_9", "type": "dokter", "label": "dr. X", "sub": "w"},
    ]
    edges = [
        {"src": "p_1", "dst": "f_A"},
        {"src": "p_22", "dst": "d_9"},
        {"src": "d_9", "dst": "f_A"},                              # kedua ujung non-pasien
    ]
    return nodes, edges


def test_pasien_nodes_are_masked_and_others_untouched(graph):
    nodes, edges = graph
    masked, _ = privacy.mask_graph(nodes, edges)
    by_id = {n["id"]: n for n in masked}

    # pasien: id & label tersamar, konsisten dengan mask_participant_id(person)
    for original in (n for n in nodes if n["type"] == "pasien"):
        person = original["id"].removeprefix("p_")
        token = privacy.mask_participant_id(person)
        new = by_id["p_" + token]
        assert new["label"] == f"Peserta {token}"
        assert new["sub"] == original["sub"]                       # field lain dipertahankan
        assert original["label"] not in new["label"]               # nama asli tidak bocor

    # non-pasien: tidak berubah sama sekali
    for original in (n for n in nodes if n["type"] != "pasien"):
        assert by_id[original["id"]] == original


def test_edges_are_remapped_consistently(graph):
    nodes, edges = graph
    masked_nodes, masked_edges = privacy.mask_graph(nodes, edges)
    node_ids = {n["id"] for n in masked_nodes}

    person_map = {"p_1": "p_" + privacy.mask_participant_id("1"),
                  "p_22": "p_" + privacy.mask_participant_id("22")}
    expected = [(person_map.get(e["src"], e["src"]), person_map.get(e["dst"], e["dst"])) for e in edges]

    assert [(e["src"], e["dst"]) for e in masked_edges] == expected
    assert all(e["src"] in node_ids and e["dst"] in node_ids for e in masked_edges)  # tidak ada edge yatim


def test_mask_graph_is_pure_and_deterministic(graph):
    nodes, edges = graph
    snapshot_nodes, snapshot_edges = copy.deepcopy(nodes), copy.deepcopy(edges)

    a_nodes, a_edges = privacy.mask_graph(nodes, edges)
    b_nodes, b_edges = privacy.mask_graph(nodes, edges)

    assert a_nodes == b_nodes and a_edges == b_edges               # deterministik
    assert nodes == snapshot_nodes and edges == snapshot_edges      # input tidak dimutasi
