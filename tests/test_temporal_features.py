import pandas as pd
import pytest

from core.temporal_features import extend, EXTRA_FEATURES


def claims():
    return pd.DataFrame({"claim_id": ["a", "b", "c"], "patient_id": ["P"] * 3, "icd": ["X"] * 3,
                         "faskes_id": ["F1", "F2", "F2"], "tarif": [100, 102, 100],
                         "visit_ts": pd.to_datetime(["2026-01-01", "2026-01-05", "2026-01-20"]),
                         "referral_from_doctor": [None, "D1", "D1"]})


def test_delayed_episode_and_directional_referral():
    data = claims()
    x = extend(data, pd.DataFrame(index=data.claim_id))
    assert x.loc["b", "episode_cross_7d"] == 1
    assert x.loc["b", "episode_gap_days"] == 4
    assert x.loc["c", "episode_prior_7d"] == 0
    assert x.loc["c", "episode_prior_30d"] == 2
    assert x.loc["b", "episode_cross_tariff_similarity"] > .98
    assert x.loc["b", "ref_target_share"] == 1
    assert x.loc["b", "ref_doctor_volume"] == 2


def test_no_future_service_event_in_episode_features_and_no_labels():
    data = claims()
    first = extend(data.iloc[:2], pd.DataFrame(index=data.claim_id[:2]))
    full = extend(data, pd.DataFrame(index=data.claim_id))
    pd.testing.assert_frame_equal(first[EXTRA_FEATURES[:6]], full.loc[first.index, EXTRA_FEATURES[:6]])
    with pytest.raises(ValueError, match="label"):
        extend(data.assign(is_fraud=1), pd.DataFrame(index=data.claim_id))


def test_order_and_equal_timestamps_do_not_create_artificial_history():
    data = claims()
    data.loc[1, "visit_ts"] = data.loc[0, "visit_ts"]
    x = extend(data, pd.DataFrame(index=data.claim_id))
    assert x.loc["b", "episode_prior_7d"] == 0
    reverse = extend(data.iloc[::-1], pd.DataFrame(index=data.claim_id))
    pd.testing.assert_frame_equal(x, reverse)


def test_temporal_model_predicts_external_batch():
    from components.external_lab import example_files
    from core.import_data import load, run_holdout
    model, scores, report = run_holdout(load(example_files()), cutoff="2026-09-30", feature_set="temporal")
    assert model.metadata["feature_set"] == "temporal"
    assert "temporal_indicators" in scores
    assert report["evaluation_available"]
