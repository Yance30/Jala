import json
import os
import time
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from core import access, batch, batch_store
from core.csv_export import safe_csv
from core.data_quality import require_time_resolution
from core.detect import build_features, explain
from core.import_data import Dataset, load, run_holdout
from core.review_queue import record, export
from core.upcoding_features import _tariff_jump, indicators
from core.workload import require_budget, MAX_EPISODE_ROWS
from tests.test_detect import _tiny
from tests.test_review_queue import sample


def pair(tariffs=(0, 0)):
    return _tiny([
        ("C1", "A", "d1", "p1", "I10", tariffs[0], "2026-07-01 09:00", "2026-07-01 10:00", None, None),
        ("C2", "B", "d1", "p1", "I10", tariffs[1], "2026-07-01 09:00", "2026-07-01 10:00", None, None),
    ])


@pytest.mark.parametrize("tariffs, expected", [((0, 0), 0), ((0, 100), 1), ((100, 0), 1)])
def test_zero_tariff_is_finite(tariffs, expected):
    features = batch._features(*pair(tariffs), {"I10": 250000})
    assert np.isfinite(features.to_numpy()).all()
    assert features.loc["C2", "f_tarif_match_prev"] == expected


def test_equal_time_features_do_not_depend_on_row_order():
    claims, *refs = pair((100, 100))
    a = build_features(claims, *refs).sort_index()
    b = build_features(claims.iloc[::-1], *refs).sort_index()
    pd.testing.assert_frame_equal(a, b)
    assert any("waktu identik" in reason for reason in explain(a.loc["C2"])["reasons"])


def test_upcoding_explanation_names_actual_denominator():
    claims, *_ = pair((100, 300))
    claims.loc[1, "visit_ts"] += pd.Timedelta(days=1)
    jump = _tariff_jump(claims)[1]
    text = " ".join(indicators(pd.Series(dict(f_icd_mix_z=0, f_pat_tarif_jump=jump))))
    assert "67% dari tarif saat ini" in text
    assert "67% di atas median" not in text


def test_csv_neutralizes_formulas_without_mutating_source():
    frame = pd.DataFrame({"text": ["=1+1", " +1", "@SUM(A1)", "\ttext", "normal"], "amount": [-1, 0, 1, 2, 3]})
    before = frame.copy(deep=True)
    decoded = pd.read_csv(__import__("io").StringIO(safe_csv(frame)), keep_default_na=False)
    assert decoded.text.tolist() == ["'=1+1", "' +1", "'@SUM(A1)", "'\ttext", "normal"]
    assert decoded.amount.tolist() == [-1, 0, 1, 2, 3]
    pd.testing.assert_frame_equal(frame, before)


def test_owners_cannot_read_write_or_delete_each_others_queues(monkeypatch):
    monkeypatch.setenv("JALA_MODE", "shared")
    with access.storage_scope("issuer:alice"):
        queue = batch_store.save_queue(sample())
    with access.storage_scope("issuer:bob"):
        assert batch_store.list_queues() == []
        with pytest.raises(ValueError):
            batch_store.load_queue(queue["id"])
        with pytest.raises(ValueError):
            batch_store.save_decision(queue["id"], "anything", "Selesai ditinjau", "test")
        batch_store.delete_queue(queue["id"])
        batch_store.clear_workspace()
    with access.storage_scope("issuer:alice"):
        assert batch_store.load_queue(queue["id"])["claims"].shape == queue["claims"].shape
        batch_store.delete_queue(queue["id"])
        assert batch_store.list_queues() == []


def test_shared_store_fails_closed_without_identity(monkeypatch):
    monkeypatch.setenv("JALA_MODE", "shared")
    with pytest.raises(PermissionError):
        batch_store.list_queues()


def test_demo_expiry_never_removes_local_or_owner_data(tmp_path, monkeypatch):
    monkeypatch.setenv("JALA_MODE", "demo")
    base = tmp_path / "batch.sqlite3"
    local = base
    local.write_text("local")
    with access.storage_scope("expired"):
        expired = access.scoped_path(base)
    expired.parent.mkdir(parents=True)
    expired.write_text("expired")
    os.utime(expired, (0, 0))
    owner = tmp_path / "owners" / ("a" * 64) / base.name
    owner.parent.mkdir(parents=True)
    owner.write_text("owner")
    access.expire_demo_sessions(base)
    assert not expired.exists()
    assert local.read_text() == "local" and owner.read_text() == "owner"


def test_date_only_data_abstains_and_dense_workload_is_rejected():
    claims, *_ = pair()
    claims["visit_ts"] = claims.visit_ts.dt.normalize()
    with pytest.raises(ValueError, match="belum cukup"):
        require_time_resolution(claims)
    dense = pd.concat([claims.iloc[[0]]] * (MAX_EPISODE_ROWS + 1), ignore_index=True)
    with pytest.raises(ValueError, match="per peserta"):
        require_budget(dense)


def test_work_priority_preserves_model_scores():
    queue = sample()
    scores = queue["claims"].priority_score.copy()
    cid = queue["claims"].iloc[0].claim_id
    record(queue, cid, "Penjelasan layanan wajar", "Dokumen mendukung", "Petugas", "Tunda")
    pd.testing.assert_series_equal(scores, queue["claims"].priority_score)
    assert export(queue).iloc[0].work_priority == "Tunda"


def test_backup_is_consistent_and_refuses_overwrite(tmp_path):
    from scripts.storage_backup import backup
    import sqlite3
    source, output = tmp_path / "source.sqlite3", tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as db:
        db.execute("CREATE TABLE example(value TEXT)")
        db.execute("INSERT INTO example VALUES ('preserved')")
    assert len(backup(source, output)) == 64
    with sqlite3.connect(output) as db:
        assert db.execute("SELECT value FROM example").fetchone()[0] == "preserved"
    with pytest.raises(ValueError):
        backup(source, output)


def test_saved_predictions_remember_observations_and_delete_model():
    from components.external_lab import example_files
    data = load(example_files())
    model, _, _ = run_holdout(data, cutoff="2026-09-30")
    key = batch_store.save_model(model)
    template = data.tables["claims"].iloc[[0]].copy()
    def package(cid, day):
        claims = template.copy()
        claims["claim_id"] = cid
        claims["visit_ts"] = pd.Timestamp(f"2026-12-{day:02d} 09:00")
        claims["submit_ts"] = pd.Timestamp(f"2026-12-{day:02d} 10:00")
        return Dataset(dict(data.tables, claims=claims), None, data.tariff_caps, data.provenance)
    batch_store.predict_and_remember(package("NEW-A", 1), key)
    _, scores, report = batch_store.predict_and_remember(package("NEW-B", 2), key)
    assert report["n_previous_observations"] == 1
    evidence = json.loads(scores.comparison_evidence.iloc[0])
    assert evidence["comparisons"]["Klaim pembanding peserta dan diagnosis"]["records"][0]["claim_id"] == "NEW-A"
    _, repeated, _ = batch_store.predict_and_remember(package("NEW-B", 2), key)
    pd.testing.assert_frame_equal(scores, repeated)
    with pytest.raises(ValueError, match="lebih lama"):
        batch_store.predict_and_remember(package("NEW-C", 1), key)
    batch_store.delete_model(key)
    assert batch_store.list_models() == []
    with batch_store.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM batch_observations").fetchone()[0] == 0
