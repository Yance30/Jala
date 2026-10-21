from dataclasses import replace
import io

import pandas as pd
import pytest

from core import batch
from core.data_quality import inspect
from core.synthetic import DEFAULT, PERIOD_START, generate_world


@pytest.fixture(scope="module")
def experiment():
    world = generate_world(7, cfg=replace(DEFAULT, n_oneoff=1000, chronological_submissions=True))
    cutoff = PERIOD_START + pd.Timedelta(days=60)
    old = world.claims[world.claims.submit_ts <= cutoff]
    new = world.claims[world.claims.submit_ts > cutoff].head(40).copy()
    labels = world.labels[world.labels.claim_id.isin(old.claim_id)]
    model = batch.train(old, world.faskes, world.affiliations, world.patients, labels, cutoff=cutoff)
    return world, model, new


def test_v2_chronology_and_feature_input_quality(experiment):
    world, _, _ = experiment
    assert inspect(world.claims, world.faskes, world.affiliations, world.patients)["passed"]


def test_prediction_needs_no_labels_or_retraining_and_keeps_model_fixed(experiment, monkeypatch):
    _, model, new = experiment
    original_history = model.history.copy(deep=True)
    def fail(*args, **kwargs):
        raise AssertionError("Prediction must never fit a model")
    monkeypatch.setattr(model.estimator, "fit", fail)
    scores = batch.predict(model, new, as_of=new.submit_ts.max())
    assert set(scores.claim_id) == set(new.claim_id)
    assert scores.priority_score.between(0, 100).all()
    assert scores.priority_score.is_monotonic_decreasing
    pd.testing.assert_frame_equal(model.history, original_history)


def test_refuses_labels_and_future_or_historical_claims(experiment, monkeypatch):
    _, model, new = experiment
    with pytest.raises(ValueError, match="label_leakage"):
        batch.predict(model, new.assign(is_fraud=1), as_of=new.submit_ts.max())
    with pytest.raises(ValueError, match="as_of"):
        batch.predict(model, new, as_of=new.submit_ts.min() - pd.Timedelta(seconds=1))
    with pytest.raises(ValueError, match="cutoff"):
        batch.predict(model, model.history.head(2), as_of=new.submit_ts.max())
    monkeypatch.setitem(model.metadata, "version", "batch-gbm-v1")
    with pytest.raises(ValueError, match="versi lama"):
        batch.predict(model, new, as_of=new.submit_ts.max())


def test_training_rejects_future_data_and_bad_labels(experiment):
    world, model, new = experiment
    labels = world.labels[world.labels.claim_id.isin(new.claim_id)]
    with pytest.raises(ValueError, match="batas waktu"):
        batch.train(new, world.faskes, world.affiliations, world.patients, labels,
                    cutoff=model.metadata["cutoff"])
    with pytest.raises(ValueError, match="tepat sesuai"):
        batch.train(new, world.faskes, world.affiliations, world.patients, labels.iloc[1:],
                    cutoff=new.submit_ts.max())


def test_evaluation_aligns_labels_and_averages_ties():
    scores = pd.DataFrame({"claim_id": ["A", "B", "C"], "priority_score": [90, 90, 10]})
    labels = pd.DataFrame({"claim_id": ["C", "B", "A"], "is_fraud": [0, 0, 1]})
    report = batch.evaluate(scores, labels, capacity=1)
    assert report["expected_fraud_at_k"] == .5
    assert report["precision_at_k"] == .5
    assert batch.evaluate(scores, labels, capacity=100)["capacity"] == 3


def test_unknown_diagnosis_is_not_silently_scored(experiment):
    _, model, new = experiment
    with pytest.raises(ValueError, match="referensi tarif"):
        batch.predict(model, new.assign(icd="UNKNOWN"), as_of=new.submit_ts.max())


def test_csv_batch_roundtrip(experiment):
    from core.contract import MINIMAL
    _, model, new = experiment
    incoming = pd.read_csv(io.StringIO(new.to_csv(index=False)), dtype={
        name: "string" for name in MINIMAL["claims"] if name not in ("tarif", "visit_ts", "submit_ts")})
    for column in ("visit_ts", "submit_ts"):
        incoming[column] = pd.to_datetime(incoming[column])
    result = batch.predict(model, incoming, as_of=incoming.submit_ts.max())
    assert len(result) == len(new)


def test_lab_can_train_and_render_results():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_string("from components.batch_lab import render\nrender()", default_timeout=90).run()
    assert not app.exception
    app.button(key="batch_run").click().run()
    assert not app.exception
    assert app.session_state["batch_experiment"][2]["quality"]["passed"]
    assert len(app.dataframe) == 2
