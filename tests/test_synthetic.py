import pandas as pd
import pytest

from core.synthetic import generate_world


@pytest.fixture(scope="module")
def world():
    return generate_world(seed=7)


def test_deterministic():
    a, b = generate_world(seed=11), generate_world(seed=11)
    pd.testing.assert_frame_equal(a.claims, b.claims)
    pd.testing.assert_frame_equal(a.labels, b.labels)


def test_different_seed_differs():
    assert not generate_world(seed=1).claims.equals(generate_world(seed=2).claims)


def test_fraud_rate_in_range(world):
    rate = world.labels.is_fraud.mean()
    assert 0.02 < rate < 0.07


def test_all_three_typologies_present(world):
    assert set(world.labels.typology[world.labels.is_fraud == 1]) == {"phantom", "repeat", "selfref"}


def test_claims_have_no_label_columns(world):
    assert not ({"is_fraud", "typology", "group"} & set(world.claims.columns))


def test_labels_align_with_claims(world):
    assert list(world.labels.claim_id) == list(world.claims.claim_id)
    assert world.claims.claim_id.is_unique


def test_referential_integrity(world):
    c = world.claims
    assert set(c.faskes_id) <= set(world.faskes.faskes_id)
    assert set(c.patient_id) <= set(world.patients.patient_id)
    ref = c.referral_from_faskes.dropna()
    assert set(ref) <= set(world.faskes.faskes_id)


def test_hard_negatives_exist(world):
    """Fraud tidak boleh satu-satunya yang tampak 'aneh': harus ada klaim sah berpola serupa."""
    c = world.claims.merge(world.labels, on="claim_id").merge(world.patients, on="patient_id") \
        .merge(world.faskes[["faskes_id", "region"]], on="faskes_id")
    legit = c[c.is_fraud == 0]
    assert (legit.home_region != legit.region).sum() > 100          # pengungsi bencana + pasien lintas wilayah
    assert (legit.icd == "N18.6").sum() > 100                        # dialisis berulang
    assert legit.referral_from_doctor.notna().sum() > 500            # rujukan sah banyak


def test_fraud_group_faskes_mapping(world):
    assert any(g.startswith("phantom") for g in world.faskes_group.values())
    assert world.fraud_faskes
