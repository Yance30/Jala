"""Local single-user SQLite storage. Model blobs are trusted application outputs only.

Never expose pickle import/upload: checksums detect corruption, not malicious DB edits.
Keep this database private to the app's OS user. This is not an authenticated audit service.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import pickle
import platform
import sqlite3

import numpy as np
import pandas as pd
import sklearn

from core.batch import BatchModel, MODE_VERSION, feature_names
from core.review_queue import record
from core.access import scoped_path, expire_demo_sessions, mode, authenticated_owner


def database_path():
    return scoped_path(base_path())


def base_path():
    return Path(os.environ.get("JALA_BATCH_DB", str(Path(__file__).resolve().parents[1] / ".jala" / "batch.sqlite3")))


@contextmanager
def connect():
    if mode() == "demo":
        expire_demo_sessions(base_path())
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA secure_delete=ON")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS batch_models (
                id TEXT PRIMARY KEY, created TEXT NOT NULL, metadata TEXT NOT NULL,
                runtime TEXT NOT NULL, payload BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS batch_queues (
                id TEXT PRIMARY KEY, created TEXT NOT NULL, metadata TEXT NOT NULL, claims TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS batch_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT NOT NULL REFERENCES batch_queues(id),
                event TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS batch_observations (
                model_id TEXT PRIMARY KEY REFERENCES batch_models(id),
                revision INTEGER NOT NULL, payload TEXT NOT NULL);
        """)
        with db:
            yield db
    finally:
        db.close()
        path.touch(exist_ok=True)  # Sliding idle expiry for demo sessions.


def runtime():
    return dict(python=platform.python_version(), sklearn=sklearn.__version__, numpy=np.__version__, pandas=pd.__version__)


def validate_model(model):
    if not isinstance(model, BatchModel):
        raise ValueError("Format model tidak sesuai.")
    mode = model.metadata.get("feature_set", "base")
    if (mode not in MODE_VERSION or model.metadata.get("version") != MODE_VERSION[mode]
            or model.metadata.get("features") != feature_names(mode)
            or model.metadata.get("sklearn_version") != sklearn.__version__):
        raise ValueError("Versi model/fitur berbeda; latih dan simpan ulang.")


def save_model(model):
    validate_model(model)
    payload = pickle.dumps(model, protocol=5)
    key = hashlib.sha256(payload).hexdigest()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO batch_models VALUES (?, ?, ?, ?, ?)",
                   (key, pd.Timestamp.now(tz="UTC").isoformat(), json.dumps(model.metadata), json.dumps(runtime()), payload))
    return key


def list_models():
    with connect() as db:
        return [dict(id=k, created=t, metadata=json.loads(m)) for k, t, m in
                db.execute("SELECT id, created, metadata FROM batch_models ORDER BY created DESC")]


def load_model(key):
    with connect() as db:
        row = db.execute("SELECT runtime, payload, metadata FROM batch_models WHERE id=?", (key,)).fetchone()
    if row is None:
        raise ValueError("Model tersimpan tidak ditemukan.")
    versions, payload, metadata = row
    if json.loads(versions) != runtime():
        raise ValueError("Versi Python/library berbeda; gunakan lingkungan asal atau latih ulang.")
    if hashlib.sha256(payload).hexdigest() != key:
        raise ValueError("Integritas model gagal; model tidak dimuat.")
    model = pickle.loads(payload)  # Only blobs written by save_model in our local, trusted DB.
    validate_model(model)
    if model.metadata != json.loads(metadata):
        raise ValueError("Metadata model tidak cocok.")
    return model


def _load_queue(db, key):
    row = db.execute("SELECT metadata, claims FROM batch_queues WHERE id=?", (key,)).fetchone()
    if row is None:
        raise ValueError("Antrean tersimpan tidak ditemukan.")
    split = json.loads(row[1])
    claims = pd.DataFrame(split["data"], columns=split["columns"], index=split["index"])
    for name in ("visit_ts", "submit_ts"):
        claims[name] = pd.to_datetime(claims[name])
    events = [json.loads(e) for (e,) in db.execute(
        "SELECT event FROM batch_events WHERE batch_id=? ORDER BY id", (key,))]
    return dict(id=key, model=json.loads(row[0]), claims=claims, events=events,
                decisions={e["claim_id"]: e for e in events})


def save_queue(queue):
    with connect() as db:
        inserted = db.execute("INSERT OR IGNORE INTO batch_queues VALUES (?, ?, ?, ?)",
                              (queue["id"], pd.Timestamp.now(tz="UTC").isoformat(), json.dumps(queue["model"]),
                               queue["claims"].to_json(orient="split", date_format="iso", date_unit="ns", double_precision=15)))
        if inserted.rowcount:
            for event in queue["events"]:
                db.execute("INSERT INTO batch_events(batch_id, event) VALUES (?, ?)", (queue["id"], json.dumps(event)))
        # Existing persisted decisions win over stale session state.
        return _load_queue(db, queue["id"])


def list_queues():
    with connect() as db:
        return [dict(id=k, created=t, model=json.loads(m)) for k, t, m in
                db.execute("SELECT id, created, metadata FROM batch_queues ORDER BY created DESC")]


def load_queue(key):
    with connect() as db:
        return _load_queue(db, key)


def save_decision(key, claim_id, status, note, actor="", priority="Ikuti skor model"):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        queue = _load_queue(db, key)
        record(queue, claim_id, status, note, actor, priority)
        if authenticated_owner():
            queue["events"][-1]["authenticated_owner"] = authenticated_owner()
        db.execute("INSERT INTO batch_events(batch_id, event) VALUES (?, ?)",
                   (key, json.dumps(queue["events"][-1])))
        return queue


def model_details():
    with connect() as db:
        return [dict(id=key, created=created, metadata=json.loads(meta), runtime=json.loads(rt))
                for key, created, meta, rt in db.execute(
                    "SELECT id, created, metadata, runtime FROM batch_models ORDER BY created DESC")]


def queue_summary():
    with connect() as db:
        return [dict(id=key, created=created, model=json.loads(meta), events=n) for key, created, meta, n in
                db.execute("SELECT q.id, q.created, q.metadata, COUNT(e.id) FROM batch_queues q "
                           "LEFT JOIN batch_events e ON e.batch_id = q.id "
                           "GROUP BY q.id, q.created, q.metadata ORDER BY q.created DESC")]


def queue_events(key):
    with connect() as db:
        return [json.loads(event) for (event,) in
                db.execute("SELECT event FROM batch_events WHERE batch_id=? ORDER BY id", (key,))]


def delete_queue(key):
    with connect() as db:
        db.execute("DELETE FROM batch_events WHERE batch_id=?", (key,))
        db.execute("DELETE FROM batch_queues WHERE id=?", (key,))


def delete_model(key):
    with connect() as db:
        db.execute("DELETE FROM batch_observations WHERE model_id=?", (key,))
        db.execute("DELETE FROM batch_models WHERE id=?", (key,))


def clear_workspace():
    """Logical deletion in the current identity's database only."""
    with connect() as db:
        for table in ("batch_events", "batch_queues", "batch_observations", "batch_models"):
            db.execute(f"DELETE FROM {table}")


def predict_and_remember(dataset, key, *, capacity=100):
    """Serialize one owner's successive predictions; model weights remain fixed."""
    from core.import_data import predict_saved
    model = load_model(key)
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT payload FROM batch_observations WHERE model_id=?", (key,)).fetchone()
        prior = json.loads(row[0]) if row else None
        result = predict_saved(dataset, model, capacity=capacity, observations=prior, retain_observations=True)
        payload = result[2].pop("_observations")
        db.execute("INSERT INTO batch_observations VALUES (?, 1, ?) "
                   "ON CONFLICT(model_id) DO UPDATE SET revision=revision+1, payload=excluded.payload",
                   (key, json.dumps(payload)))
        return result
