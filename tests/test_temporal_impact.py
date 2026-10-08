"""Replay mingguan time-to-first-detection (core/temporal_impact.py).

Dunia dipotong ke 3 minggu pertama agar jalur GBM asli tetap teruji tanpa
menunggu 14 fit (kira-kira 20 detik) di setiap run suite.
"""
import pandas as pd
import pytest

from core import temporal_impact as ti
from core.synthetic import World, generate_world


@pytest.fixture(scope="module")
def replay():
    """Jalankan weekly_replay sekali di dunia 3-minggu, bagi hasilnya ke semua tes."""
    w = generate_world(seed=2026, n_oneoff=0)
    cut = w.claims.submit_ts.min().normalize() + pd.Timedelta(days=21)
    claims = w.claims[w.claims.submit_ts < cut].reset_index(drop=True)
    labels = w.labels[w.labels.claim_id.isin(claims.claim_id)]
    world = World(claims=claims, faskes=w.faskes, affiliations=w.affiliations,
                  patients=w.patients, labels=labels, seed=w.seed)
    return ti.weekly_replay(world, capacity_per_week=100), world


def test_top_level_and_meta_shape(replay):
    r, world = replay
    assert set(r) == {"meta", "weekly", "capacity_grid", "rings"}
    assert r["capacity_grid"] == list(range(0, 1201, 5))
    meta = r["meta"]
    assert {"seed", "capacity_claims_per_week", "n_claims", "n_weeks", "method", "caveat"} <= set(meta)
    assert meta["seed"] == world.seed and meta["capacity_claims_per_week"] == 100
    assert meta["n_claims"] == len(world.claims) and meta["n_weeks"] == len(r["weekly"])
    assert "sintetis" in meta["caveat"].lower() or "synthetic" in meta["caveat"].lower()


def test_weeks_are_ordered_and_counts_consistent(replay):
    r, _ = replay
    weeks = r["weekly"]
    assert [w["week"] for w in weeks] == list(range(1, len(weeks) + 1))
    starts = [pd.Timestamp(w["start"]) for w in weeks]
    assert starts == sorted(starts) and len(set(starts)) == len(starts)
    for w in weeks:
        assert 0 <= w["n_fraud"] <= w["n_claims"]
        assert w["rings_caught_jala"] <= w["rings_active"]
        assert w["rings_caught_rules"] <= w["rings_active"]


def test_no_model_in_first_week_no_future_leakage(replay):
    """Minggu 1 tidak punya data historis, GBM tidak boleh tersedia (cegah kebocoran masa depan)."""
    r, _ = replay
    weeks = r["weekly"]
    assert weeks[0]["jala_model_available"] is False
    assert any(w["jala_model_available"] for w in weeks[1:])


def test_capacity_curve_is_monotonic_and_bounded(replay):
    r, _ = replay
    grid = r["capacity_grid"]
    for w in r["weekly"]:
        curve = w["capacity_curve"]
        assert curve["capacity_per_week"] == grid
        for key in ("fraud_caught_jala", "fraud_caught_rules"):
            arr = curve[key]
            assert len(arr) == len(grid)
            assert all(b >= a for a, b in zip(arr, arr[1:]))
            assert arr[0] == 0 and max(arr) <= w["n_fraud"]
        if not w["jala_model_available"]:
            assert set(curve["fraud_caught_jala"]) == {0}


def test_ring_rows_respect_first_active_week(replay):
    r, _ = replay
    assert r["rings"], "minimal satu ring terdeteksi"
    for ring in r["rings"]:
        assert {"ring", "typology", "first_week_active"} <= set(ring)
        assert ring["first_week_active"] >= 1
        for wk in ("jala_week", "rules_week"):
            if wk in ring:
                assert ring[wk] >= ring["first_week_active"]
        if ring.get("jala_week") is not None and ring.get("rules_week") is not None:
            assert ring["weeks_earlier"] == ring["rules_week"] - ring["jala_week"]
        else:
            assert ring["weeks_earlier"] is None


def test_replay_is_deterministic(replay):
    first, world = replay
    assert ti.weekly_replay(world, capacity_per_week=100) == first
