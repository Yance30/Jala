"""Upcoding candidate features: isolated as a feature_set so published baselines stay valid."""
import numpy as np
import pandas as pd
import pytest

from core import batch
from core.detect import FEATURES, build_features
from core.independent_scenarios import generate
from core.upcoding_features import UPCODING_FEATURES, _tariff_jump, extend

CAPS = {"I10": 250000, "E11.9": 300000, "N18.6": 1200000, "I50": 2400000}


def features(case):
    base = build_features(case.claims, case.faskes, case.affiliations, case.patients, tariff_caps=CAPS)
    return extend(case.claims, base, case.faskes)


def test_upcoded_claims_stand_out_from_legitimate_severe_cases():
    case = generate(31, n_routine=800, upcoding=True)
    x = features(case)
    scenario = case.labels.set_index("claim_id").scenario.reindex(x.index)
    upcoded = x[scenario.eq("upcoding")]
    legitimate = x[scenario.eq("legit_severe")]
    assert not upcoded.empty and not legitimate.empty
    # Both bill the same high-severity code; only the clinic deviates from its peer group.
    assert upcoded.f_icd_mix_z.median() > legitimate.f_icd_mix_z.median() + 2
    assert upcoded.f_pat_tarif_jump.median() > .5
    assert legitimate.f_pat_tarif_jump.median() == 0.


def test_routine_claims_are_not_flagged():
    case = generate(31, n_routine=800, upcoding=True)
    x = features(case)
    scenario = case.labels.set_index("claim_id").scenario.reindex(x.index)
    routine = x[scenario.eq("routine")]
    assert routine.f_icd_mix_z.median() < 1
    assert (routine.f_pat_tarif_jump > .5).mean() < .05


def test_tariff_jump_ignores_equal_timestamps():
    when = pd.Timestamp("2026-09-01T08:00:00")
    claims = pd.DataFrame({"claim_id": ["a", "b", "c"], "patient_id": ["P", "P", "P"],
                           "tarif": [100000., 1000000., 1000000.],
                           "visit_ts": [when, when, when + pd.Timedelta(days=1)]})
    assert _tariff_jump(claims).tolist()[:2] == [0., 0.]
    assert _tariff_jump(claims)[2] == pytest.approx(.45, abs=.01)


def test_labels_are_rejected():
    case = generate(31, n_routine=50, upcoding=True)
    base = build_features(case.claims, case.faskes, case.affiliations, case.patients, tariff_caps=CAPS)
    leaked = case.claims.assign(is_fraud=0)
    with pytest.raises(ValueError):
        extend(leaked, base, case.faskes)


def test_default_scenario_generation_is_unchanged():
    case = generate(31, n_routine=200)
    assert not case.claims.icd.eq("I50").any()
    assert not case.labels.scenario.isin(["upcoding", "upcode_original", "legit_severe"]).any()
    assert set(case.claims.icd) == {"I10", "E11.9", "N18.6"}


def test_feature_set_is_registered_and_versioned():
    assert batch.feature_names("upcoding") == list(FEATURES) + UPCODING_FEATURES
    assert batch.MODE_VERSION["upcoding"] == batch.UPCODING_VERSION
    with pytest.raises(ValueError, match="feature_set"):
        batch.feature_names("lainnya")


def test_upcoding_model_is_trained_scored_and_stored():
    from core import batch_store
    case = generate(31, n_routine=400, days=70, upcoding=True)
    cutoff = pd.Timestamp("2026-10-01")
    history = case.claims[case.claims.submit_ts <= cutoff]
    incoming = case.claims[case.claims.submit_ts > cutoff]
    labels = case.labels[["claim_id", "is_fraud"]]
    model = batch.train(history, case.faskes, case.affiliations, case.patients,
                        labels=labels[labels.claim_id.isin(history.claim_id)],
                        cutoff=cutoff, tariff_caps=CAPS, feature_set="upcoding")
    assert model.metadata["version"] == batch.UPCODING_VERSION
    assert model.metadata["features"] == batch.feature_names("upcoding")
    scores = batch.predict(model, incoming, as_of=incoming.submit_ts.max())
    assert "upcoding_indicators" in scores and "temporal_indicators" not in scores
    assert np.isfinite(scores.priority_score).all()
    assert batch_store.load_model(batch_store.save_model(model)).metadata == model.metadata
