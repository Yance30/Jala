"""Persistence contract: a saved model must behave exactly like the trained one."""
from dataclasses import replace
import json

import pandas as pd
import pytest

from components.external_lab import example_files
from core import batch, batch_store
from core.import_data import load, predict_saved, run_holdout
from core.review_queue import prepare


@pytest.fixture(scope="module")
def trained():
    data = load(example_files())
    model, scores, report = run_holdout(data, cutoff="2026-09-30", capacity=30)
    return data, model, scores, report


def test_saved_model_reproduces_predictions(trained):
    data, model, _, _ = trained
    loaded = batch_store.load_model(batch_store.save_model(model))
    assert loaded.metadata == model.metadata
    incoming = data.tables["claims"].query("submit_ts > '2026-09-30'")
    as_of = incoming.submit_ts.max()
    pd.testing.assert_frame_equal(batch.predict(loaded, incoming, as_of=as_of),
                                  batch.predict(model, incoming, as_of=as_of))


def test_saving_same_model_twice_is_idempotent(trained):
    _, model, _, _ = trained
    key = batch_store.save_model(model)
    batch_store.save_model(model)
    rows = batch_store.list_models()
    assert [row["id"] for row in rows] == [key]
    assert rows[0]["metadata"]["version"] == model.metadata["version"]


def test_tampered_payload_is_refused(trained):
    _, model, _, _ = trained
    key = batch_store.save_model(model)
    with batch_store.connect() as db:
        db.execute("UPDATE batch_models SET payload=? WHERE id=?", (b"tampered", key))
    with pytest.raises(ValueError, match="Integritas"):
        batch_store.load_model(key)


def test_different_runtime_is_refused(trained):
    _, model, _, _ = trained
    key = batch_store.save_model(model)
    with batch_store.connect() as db:
        db.execute("UPDATE batch_models SET runtime=? WHERE id=?", (json.dumps(dict(python="0")), key))
    with pytest.raises(ValueError, match="Versi Python"):
        batch_store.load_model(key)


def test_stale_model_version_cannot_be_saved(trained):
    _, model, _, _ = trained
    with pytest.raises(ValueError, match="Versi model"):
        batch_store.save_model(replace(model, metadata={**model.metadata, "version": "batch-gbm-v1"}))
    with pytest.raises(ValueError, match="Format model"):
        batch_store.validate_model(object())
    with pytest.raises(ValueError, match="tidak ditemukan"):
        batch_store.load_model("absent")


def test_predict_saved_scores_new_batch_without_retraining(trained):
    data, model, scores, holdout = trained
    cutoff = pd.Timestamp(model.metadata["cutoff"])
    incoming = data.tables["claims"][data.tables["claims"].submit_ts > cutoff]
    package = load(example_files())
    package.tables["claims"] = incoming.copy()
    package.labels = data.labels[data.labels.claim_id.isin(incoming.claim_id)]
    _, saved, report = predict_saved(package, batch_store.load_model(batch_store.save_model(model)), capacity=30)
    pd.testing.assert_frame_equal(saved, scores)
    assert report["inference"] == "Saved model; no retraining"
    assert report["evaluation_available"]
    assert report["jala"] == holdout["jala"]


def test_predict_saved_rejects_changed_tariff_reference(trained):
    _, model, _, _ = trained
    package = load(example_files())
    package.tariff_caps["I10"] = 999_999
    with pytest.raises(ValueError, match="Referensi tarif"):
        predict_saved(package, batch_store.load_model(batch_store.save_model(model)))


def test_queue_and_decisions_survive_reconnect(trained):
    data, _, scores, report = trained
    queue = batch_store.save_queue(prepare(data.tables["claims"], scores, report["model"]))
    cid = queue["claims"].iloc[0].claim_id
    batch_store.save_decision(queue["id"], cid, "Perlu bukti tambahan", "Periksa dokumen layanan")
    fresh = batch_store.load_queue(queue["id"])
    assert fresh["decisions"][cid]["status"] == "Perlu bukti tambahan"
    assert len(fresh["events"]) == 1
    pd.testing.assert_frame_equal(fresh["claims"][["claim_id", "priority_score", "submit_ts"]],
                                  queue["claims"][["claim_id", "priority_score", "submit_ts"]])
    assert [row["id"] for row in batch_store.list_queues()] == [queue["id"]]


def test_resending_same_batch_keeps_persisted_decisions(trained):
    data, _, scores, report = trained
    first = batch_store.save_queue(prepare(data.tables["claims"], scores, report["model"]))
    cid = first["claims"].iloc[0].claim_id
    batch_store.save_decision(first["id"], cid, "Selesai ditinjau", "Bukti sudah diverifikasi")
    # A fresh session rebuilds the same queue with no decisions of its own.
    again = batch_store.save_queue(prepare(data.tables["claims"], scores, report["model"]))
    assert again["id"] == first["id"]
    assert len(again["events"]) == 1
    assert again["decisions"][cid]["status"] == "Selesai ditinjau"


def test_invalid_decisions_are_not_persisted(trained):
    data, _, scores, report = trained
    queue = batch_store.save_queue(prepare(data.tables["claims"], scores, report["model"]))
    cid = queue["claims"].iloc[0].claim_id
    with pytest.raises(ValueError):
        batch_store.save_decision(queue["id"], "unknown", "Selesai ditinjau", "catatan")
    with pytest.raises(ValueError):
        batch_store.save_decision(queue["id"], cid, "Selesai ditinjau", " ")
    assert batch_store.load_queue(queue["id"])["events"] == []
    with pytest.raises(ValueError, match="Antrean tersimpan"):
        batch_store.load_queue("absent")


def test_decision_records_actor_and_status_views_expose_it(trained):
    data, model, scores, report = trained
    key = batch_store.save_model(model)
    queue = batch_store.save_queue(prepare(data.tables["claims"], scores, report["model"]))
    cid = queue["claims"].iloc[0].claim_id
    batch_store.save_decision(queue["id"], cid, "Selesai ditinjau", "Bukti lengkap", "Pemeriksa Satu")
    assert batch_store.queue_events(queue["id"])[-1]["actor"] == "Pemeriksa Satu"
    summary = batch_store.queue_summary()
    assert summary[0]["id"] == queue["id"] and summary[0]["events"] == 1
    details = batch_store.model_details()
    assert details[0]["id"] == key and details[0]["runtime"] == batch_store.runtime()
    with pytest.raises(ValueError, match="pemeriksa"):
        batch_store.save_decision(queue["id"], cid, "Selesai ditinjau", "catatan", "x" * 121)
