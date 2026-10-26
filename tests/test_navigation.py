"""Exercise navigation controls through Streamlit's real widget callbacks."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def open_page(page):
    app = AppTest.from_file(APP, default_timeout=120)
    app.session_state["intro_done"] = True
    app.session_state["tour_seen"] = True
    app.session_state["page"] = page
    return app.run()


def test_every_sidebar_destination():
    from components.sidebar import NAV_PAGES
    app = open_page("dashboard")
    for destination, label in NAV_PAGES:
        app.radio(key="nav_radio").set_value(label).run()
        assert not app.exception, destination
        assert app.session_state["page"] == destination
        assert app.radio(key="nav_radio").value == label


@pytest.mark.parametrize("source,label,destination", [
    ("dashboard", "Olah paket data", "data_prediction"),
    ("dashboard", "Coba demo sintetis", "risk"),
    ("about", "Buka Data & Prediksi", "data_prediction"),
    ("batch_review", "Mulai dari Data & Prediksi", "data_prediction"),
])
def test_operational_entry_buttons(source, label, destination):
    app = open_page(source)
    next(button for button in app.button if button.label == label).click().run()
    assert not app.exception
    assert app.session_state["page"] == destination


def test_primary_demo_journey_and_return():
    app = open_page("dashboard")
    app.button(key="dashboard_start_review").click().run()
    assert app.session_state["page"] == "claim"
    selected = app.session_state["selected_cluster"]
    next(b for b in app.button if b.label == "Buka Tindak Lanjut").click().run()
    assert app.session_state["page"] == "audit"
    app.button(key="open_graph").click().run()
    assert app.session_state["page"] == "network"
    app.button(key="go_audit").click().run()
    assert app.session_state["page"] == "audit"
    assert app.session_state["selected_cluster"] == selected
    app.button(key="audit_back_to_queue").click().run()
    assert app.session_state["page"] == "risk"
    assert not app.exception


def test_navigation_updates_link_and_link_can_open_new_session():
    app = open_page("dashboard")
    app.button(key="start_prediction").click().run()
    assert app.query_params["page"] == ["data_prediction"]
    fresh = AppTest.from_file(APP, default_timeout=120)
    fresh.session_state["intro_done"] = True
    fresh.session_state["tour_seen"] = True
    fresh.query_params["page"] = "data_prediction"
    fresh.run()
    assert not fresh.exception
    assert fresh.session_state["page"] == "data_prediction"


def test_invalid_session_route_recovers_to_dashboard():
    app = open_page("missing-page")
    assert not app.exception
    assert app.session_state["page"] == "dashboard"


def test_stepper_only_allows_backward_navigation():
    app = open_page("risk")
    assert not app.button(key="workflow_back_0").disabled
    assert all(app.button(key=f"workflow_back_{i}").disabled for i in (1, 2, 3))
    app.button(key="workflow_back_0").click().run()
    assert app.session_state["page"] == "dashboard"
    assert not app.exception


def test_planned_action_is_not_completed_review():
    from components.review_status import cluster_status
    assert cluster_status("field_audit")[2] is False
    assert cluster_status("freeze")[2] is False
    assert cluster_status(None)[2] is False
    assert cluster_status("dismiss")[2] is True


@pytest.mark.parametrize("step", [0, 1, 2])
def test_batch_stepper_returns_to_data_without_clearing_queue(step):
    app = open_page("batch_review")
    app.session_state["batch_review"] = "retained-queue"
    assert app.button(key="batch_workflow_back_3").disabled
    assert app.button(key="batch_workflow_back_4").disabled
    app.button(key=f"batch_workflow_back_{step}").click().run()
    assert app.session_state["page"] == "data_prediction"
    assert app.session_state["batch_review"] == "retained-queue"
    assert not app.exception
