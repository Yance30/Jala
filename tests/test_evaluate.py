import numpy as np
import pytest

from core.evaluate import benchmark, expected_hits, fold_assignment
from core.synthetic import generate_world


@pytest.fixture(scope="module")
def bm():
    return benchmark(seed=7)


def test_expected_hits_handles_ties():
    y = np.array([1, 0, 0, 1, 0, 0])
    s = np.array([1, 1, 1, 1, 0, 0], float)         # empat skor kembar berisi 2 fraud
    assert expected_hits(y, s, (2,))[0] == pytest.approx(1.0)
    assert expected_hits(y, s, (4,))[0] == pytest.approx(2.0)


def test_expected_hits_perfect_ranking():
    y = np.array([1, 1, 0, 0])
    assert list(expected_hits(y, np.array([.9, .8, .2, .1]), (1, 2, 4))) == [1, 2, 2]


def test_no_fraud_group_spans_folds():
    w = generate_world(seed=7)
    fold = fold_assignment(w)
    for g in set(w.faskes_group.values()):
        members = [f for f, gg in w.faskes_group.items() if gg == g]
        assert fold[members].nunique() == 1
    assert fold.nunique() == 4


def test_every_fold_has_fraud():
    w = generate_world(seed=7)
    fold = fold_assignment(w)
    fraud_folds = {fold[f] for f in w.fraud_faskes}
    assert fraud_folds == {0, 1, 2, 3}


def test_graph_scorer_beats_random_and_rules(bm):
    m = bm.metrics
    g, r = m["scorers"]["graph_gbm"], m["scorers"]["rules"]
    assert g["auc"] > 0.9 and g["auc"] > r["auc"] + 0.2
    assert g["recall_at_k"][500] > 3 * m["random"]["recall_at_k"][500]
    assert g["recall_at_k"][500] > 2 * r["recall_at_k"][500]


def test_no_single_feature_gives_away_the_label(bm):
    assert max(bm.metrics["single_feature_auc"].values()) < 0.9


def test_all_typologies_detected_above_chance(bm):
    for t, v in bm.metrics["per_typology"].items():
        assert v["graph_gbm"]["auc"] > 0.85, t


def test_metrics_are_json_serialisable(bm):
    import json
    json.dumps(bm.metrics)


def test_scored_has_no_nan(bm):
    assert not bm.scored[["score_graph", "score_iforest", "score_rules"]].isna().any().any()
