from dataclasses import replace

from streamlit.testing.v1 import AppTest


def test_train_save_predict_and_open_review():
    from core import batch_store
    app = AppTest.from_string("from components.external_lab import render\nrender(expanded=True)", default_timeout=120)
    app.run()
    app.button(key="external_example").click().run()
    app.button(key="external_run").click().run()
    assert not app.exception and not app.error
    model, _, _ = app.session_state["external_result"]
    app.button(key="external_save_model").click().run()
    assert len(batch_store.list_models()) == 1
    data = app.session_state["external_dataset"]
    incoming = data.tables["claims"]
    incoming = incoming[incoming.submit_ts >= model.history.submit_ts.max()].copy()
    incoming = incoming[~incoming.claim_id.isin(model.history.claim_id)]
    assert len(incoming)
    app.session_state["external_dataset"] = replace(data, tables={**data.tables, "claims": incoming}, labels=None)
    app.radio(key="prediction_purpose").set_value("Gunakan model tersimpan").run()
    app.button(key="saved_predict").click().run()
    assert not app.exception and not app.error
    app.button(key="saved_to_review").click().run()
    assert app.session_state["page"] == "batch_review"
    queue = batch_store.load_queue(app.session_state["batch_review"])
    assert len(queue["claims"]) == len(incoming)
