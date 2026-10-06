"""Tutorial penggunaan (components/tutorial.py). Navigasi di dalam dialog diuji di browser (Playwright),
karena AppTest menjalankan ulang seluruh skrip, bukan hanya fragmen dialog."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from components import tutorial

APP = str(Path(__file__).resolve().parent.parent / "app.py")
ROUTES = {"dashboard", "network", "risk", "claim", "audit", "about"}


def _text(at):
    return " ".join(m.value for m in at.markdown)


def test_steps_are_well_formed():
    assert len(tutorial.STEPS) == 7
    titles = [s["title"] for s in tutorial.STEPS]
    assert len(set(titles)) == len(titles)
    for s in tutorial.STEPS:
        assert s["page"] is None or s["page"] in ROUTES
        assert s["lead"] and s["tip"] and len(s["do"]) >= 3
        assert not s["cluster"] or s["page"] in {"network", "claim", "audit"}


def test_steps_follow_the_demo_flow():
    pages = [s["page"] for s in tutorial.STEPS if s["page"]]
    assert pages == ["dashboard", "risk", "network", "claim", "audit", "about"]


def test_step_texts_have_no_hardcoded_numbers_that_go_stale():
    import re
    for s in tutorial.STEPS:
        body = " ".join(s["do"]) + s["lead"] + s["tip"]
        assert not re.search(r"\d+\s?%|Rp\s?\d|\d{3,}", body), s["title"]


def test_opens_automatically_once_per_session():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["intro_done"] = True
    at.run()
    assert not at.exception and "Selamat datang di JALA" in _text(at)
    assert at.session_state["tour_seen"] is True
    assert any(b.key == "tour_open" for b in at.button)           # tombol sidebar tersedia


def test_tour_zero_disables_auto_open():
    at = AppTest.from_file(APP, default_timeout=120)
    at.query_params["tour"] = "0"
    at.session_state["intro_done"] = True
    at.run()
    assert not at.exception and "Selamat datang di JALA" not in _text(at)
    assert at.session_state["tour_seen"] is True


def test_sidebar_button_opens_dialog_on_demand():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["intro_done"] = True
    at.session_state["tour_seen"] = True
    at.run()
    assert "Selamat datang di JALA" not in _text(at)
    next(b for b in at.button if b.key == "tour_open").click().run()
    assert not at.exception and "Selamat datang di JALA" in _text(at)


def test_example_cluster_is_top_base_cluster():
    from components import bench
    cid, name, score = tutorial._example()
    top = bench.get_live_base().clusters[0]
    assert (cid, score) == (top["id"], top["score"])


def test_go_clamps_step_index(monkeypatch):
    state = {"tour_step": 0}
    monkeypatch.setattr(tutorial.st, "session_state", state)
    tutorial._go(-1)
    assert state["tour_step"] == 0
    for _ in range(20):
        tutorial._go(1)
    assert state["tour_step"] == len(tutorial.STEPS) - 1
