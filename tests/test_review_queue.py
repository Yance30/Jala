import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from core.review_queue import prepare, record, export
from core.review_queue import progress
from core.independent_scenarios import generate
from core.unseen_evaluation import training_tables, FAMILIES


def sample():
    claims = generate(777, n_routine=10).claims.head(2)
    scores = pd.DataFrame(dict(claim_id=claims.claim_id, priority_score=[20., 90.], indicators=['{}', '{}']))
    return prepare(claims, scores, dict(version="test", cutoff="2026-10-01"))


def test_progress_uses_latest_status_not_saved_note_count():
    queue = sample()
    first, second = queue["claims"].claim_id.tolist()
    record(queue, first, "Belum ditinjau", "Catatan awal")
    assert progress(queue) == {"Belum ditinjau": 2, "Dalam pemeriksaan": 0, "Selesai": 0}
    for status in ("Perlu bukti tambahan", "Teruskan pemeriksaan", "Kesalahan data", "Data belum cukup"):
        record(queue, first, status, "Masih perlu tindak lanjut")
        assert progress(queue)["Dalam pemeriksaan"] == 1
    record(queue, first, "Selesai ditinjau", "Bukti lengkap")
    record(queue, second, "Penjelasan layanan wajar", "Bukti layanan sah")
    assert progress(queue)["Selesai"] == 2
    record(queue, first, "Perlu bukti tambahan", "Buka kembali")
    assert progress(queue) == {"Belum ditinjau": 0, "Dalam pemeriksaan": 1, "Selesai": 1}


def test_decisions_preserve_scores_and_history():
    q = sample()
    cid = q["claims"].iloc[0].claim_id
    before = q["claims"].copy()
    record(q, cid, "Perlu bukti tambahan", "Periksa dokumen layanan")
    record(q, cid, "Selesai ditinjau", "Dokumen sudah diperiksa")
    pd.testing.assert_frame_equal(before, q["claims"])
    assert len(q["events"]) == 2
    assert export(q).iloc[0].review_status == "Selesai ditinjau"
    with pytest.raises(ValueError):
        record(q, "unknown", "Selesai ditinjau", "catatan")
    with pytest.raises(ValueError):
        record(q, cid, "Selesai ditinjau", " ")


@pytest.mark.parametrize("family", FAMILIES)
def test_family_removed_before_graph_features(family):
    case = generate(777, n_routine=10)
    tables, labels = training_tables([case], family)
    removed = set(case.labels.loc[case.labels.scenario.eq(family), "claim_id"])
    assert removed
    assert not removed.intersection(tables["claims"].claim_id)
    assert not labels.scenario.eq(family).any()
    assert set(tables["claims"].claim_id) == set(labels.claim_id)
    assert set(labels.is_fraud) == {0, 1}


def test_review_page_saves_decision():
    from core import batch_store
    queue = batch_store.save_queue(sample())
    app = AppTest.from_string("from views.batch_review import render\nrender()")
    app.session_state["batch_review"] = queue["id"]
    app.run(timeout=30)
    assert not app.exception
    app.selectbox[3].set_value("Perlu bukti tambahan")
    app.text_area[0].set_value("Mohon dokumen layanan")
    next(w for w in app.text_input if w.label == "Nama pemeriksa").set_value("Pemeriksa Uji")
    app.button[0].click().run(timeout=30)
    assert not app.exception
    loaded = batch_store.load_queue(queue["id"])
    assert len(loaded["events"]) == 1
    assert loaded["events"][0]["actor"] == "Pemeriksa Uji"
    cid = queue["claims"].iloc[0].claim_id
    assert export(loaded).set_index("claim_id").loc[cid, "review_actor"] == "Pemeriksa Uji"


def test_review_page_refuses_decision_without_actor():
    from core import batch_store
    queue = batch_store.save_queue(sample())
    app = AppTest.from_string("from views.batch_review import render\nrender()")
    app.session_state["batch_review"] = queue["id"]
    app.run(timeout=30)
    app.text_area[0].set_value("Mohon dokumen layanan")
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert not batch_store.load_queue(queue["id"])["events"]
    assert any("Nama pemeriksa wajib diisi" in e.value for e in app.error)


def test_review_page_reads_persisted_queue_without_session_state():
    from core import batch_store
    queue = batch_store.save_queue(sample())
    cid = queue["claims"].iloc[0].claim_id
    batch_store.save_decision(queue["id"], cid, "Selesai ditinjau", "Dokumen lengkap")
    app = AppTest.from_string("from views.batch_review import render\nrender()")
    app.run(timeout=30)
    assert not app.exception
    assert app.session_state["batch_review"] == queue["id"]
    assert any("1 keputusan tersimpan" in caption.value for caption in app.caption)
