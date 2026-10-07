"""Smoke test: setiap layar dirender tanpa exception dan tanpa placeholder grafik.

Menangkap bug seperti grafik yang memanggil fungsi chart yang tidak ada. Dijalankan
dengan streamlit.testing.v1.AppTest (tanpa browser).
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
PAGES = ["dashboard", "network", "risk", "claim", "audit", "about"]
TIMEOUT = 120


def _open(page: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.session_state["intro_done"] = True
    at.session_state["tour_seen"] = True            # tutorial otomatis diuji terpisah
    at.session_state["page"] = page
    return at.run()


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_without_exception(page):
    at = _open(page)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("page", PAGES)
def test_page_has_no_missing_chart_placeholder(page):
    at = _open(page)
    text = " ".join(str(m.value) for m in at.markdown)
    assert "belum tersedia" not in text


def test_dashboard_reset_restores_demo_session():
    at = _open("dashboard")
    at.session_state["feedback"] = {
        "JALA-F006": {"verdict": "dismiss", "note": "uji", "at": "2026-10-05 10:00"}
    }
    at.session_state["audited"] = {"JALA-F006": "dismiss"}
    at.session_state["audit_log"] = ["aksi uji"]
    at.session_state["review_history"] = [{"case_id": "JALA-F006", "action": "uji"}]
    at.session_state["note_draft"] = "catatan uji"
    at.session_state["selected_cluster"] = "JALA-F044"
    at.session_state["zoom"] = 1.4
    at.session_state["isolate"] = True
    at.session_state["risk_chip"] = "Phantom Billing"
    at.run()

    next(button for button in at.button if button.key == "dashboard_reset").click().run()

    assert at.session_state["feedback"] == {}
    assert at.session_state["audited"] == {}
    assert at.session_state["audit_log"] == []
    assert at.session_state["review_history"][0] == {"case_id": "JALA-F006", "action": "uji"}
    assert at.session_state["review_history"][-1]["action"] == "Umpan balik sesi diatur ulang"
    assert at.session_state["note_draft"] == ""
    assert at.session_state["selected_cluster"] is None
    assert at.session_state["zoom"] == 1.0 and at.session_state["isolate"] is False
    assert "risk_chip" not in at.session_state


def test_dashboard_contrast_case_opens_claim_review():
    at = _open("dashboard")
    text = _text(at)
    assert "KASUS PEMBANDING" in text
    assert "Klaim berulang dapat mengikuti jadwal layanan yang sah" in text

    next(button for button in at.button if button.key == "dashboard_open_contrast").click().run()

    assert not at.exception
    assert at.session_state["page"] == "claim"

    # Klaster pembanding dipilih dinamis (yang paling didominasi klaim dialisis
    # terjadwal N18.6), bukan hardcoded; pastikan klaster yang dibuka memang
    # memuat klaim N18.6 sesuai niat kartu "kasus pembanding".
    from components import bench

    selected = at.session_state["selected_cluster"]
    assert selected is not None
    live = bench.get_live()
    claims = live.flagged.loc[live.by_id[selected]["idx"]]
    assert (claims.icd == "N18.6").any()


def test_claim_details_frequency_chart_is_real():
    from components import charts

    fig = charts.freq_chart(["A", "B", "C"], [2, 2, 2], [1, 9, 3], "B")
    assert len(fig.data) == 2 and fig.layout.annotations


def test_comparison_alias_opens_about():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.session_state["intro_done"] = True
    at.query_params["page"] = "comparison"
    at.run()
    assert not at.exception
    assert at.session_state["page"] == "about"


def test_about_shows_robustness_section():
    at = _open("about")
    text = " ".join(str(m.value) for m in at.markdown)
    assert "UJI KETAHANAN" in text and "Perbaikan Repeat Billing" in text


def _text(at):
    return " ".join(str(m.value) for m in at.markdown)


def test_screens_show_computed_clusters_not_illustrative_ones():
    from components import bench

    names = [c["name"] for c in bench.get_live().clusters]
    for page in ("risk", "claim", "audit"):
        t = _text(_open(page))
        assert any(n in t for n in names), page
        for stale in ("HAN-089", "42 ring", "98.1%", "Confidence Interval: 99.2%", "2.4M Entities", "1,284"):
            assert stale not in t, (page, stale)


def test_selected_cluster_carries_across_screens():
    from components import bench

    lv = bench.get_live()
    cid = lv.clusters[3]["id"]
    for page in ("claim", "network", "audit"):
        at = AppTest.from_file(APP, default_timeout=TIMEOUT)
        at.session_state["intro_done"] = True
        at.session_state["page"] = page
        at.session_state["selected_cluster"] = cid
        at.run()
        assert not at.exception, page
        assert lv.by_id[cid]["name"] in _text(at) or cid in _text(at), page


def test_claim_review_status_and_audit_action_route():
    at = _open("claim")
    assert "Belum ada keputusan verifikator" in _text(at)
    assert "Periksa klaim sumber dan konteksnya" in _text(at)

    next(button for button in at.button if button.key == "claim_open_audit").click().run()

    assert not at.exception
    assert at.session_state["page"] == "audit"
    assert at.session_state["selected_cluster"] is not None


def test_global_case_search_opens_selected_cluster_from_sidebar():
    from components import bench

    cid = bench.get_live().clusters[0]["id"]
    at = _open("dashboard")
    at.session_state["case_search_query"] = cid
    at.run()

    next(button for button in at.button if button.key == "case_search_open").click().run()

    assert not at.exception
    assert at.session_state["page"] == "claim"
    assert at.session_state["selected_cluster"] == cid


def test_shared_case_filter_matches_typology_and_faskes():
    from components import bench, case_search

    rows = bench.get_live().risk_rows()
    target = rows[0]
    typology = target["typology"][0]
    assert target in case_search.filter_rows(rows, target["id"], typology)
    faskes_name = target["subtitle"].split(" ·")[0]
    assert target in case_search.filter_rows(rows, faskes_name, "Semua pola")
    assert all(r["typology"][0] == typology for r in case_search.filter_rows(rows, "", typology))


# ---- loop verifikator di layar (dismiss -> skor/peringkat berubah -> batal) ----
def _audit_with(cid: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.session_state["intro_done"] = True
    at.session_state["tour_seen"] = True
    at.session_state["page"] = "audit"
    at.session_state["selected_cluster"] = cid
    return at.run()


def _text(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def test_audit_page_shows_whatif_panel():
    at = _audit_with("JALA-F006")
    assert not at.exception and "bagaimana kalau dokter ini dikeluarkan" in _text(at)
    assert "UMPAN BALIK VERIFIKATOR" not in _text(at)            # belum ada keputusan


def test_dismiss_flow_lowers_score_shows_banner_and_can_be_undone():
    at = _audit_with("JALA-F006")
    next(b for b in at.button if b.key and "Dismiss" in b.key).click().run()
    assert not at.exception
    assert {k: v["verdict"] for k, v in at.session_state["feedback"].items()} == {"JALA-F006": "dismiss"}
    assert at.session_state["review_history"][-1]["action"] == "Tandai sebagai pola wajar"
    assert any(b.key == "audit_history_JALA-F006_download" for b in at.download_button)
    txt = _text(at)
    assert "UMPAN BALIK VERIFIKATOR" in txt and "JALA-F044" in txt and "→ <b>40%</b>" in txt
    assert any(e.label == "Riwayat pemeriksaan klaster" for e in at.expander)

    at.session_state["page"] = "risk"
    at.run()
    assert not at.exception and "UMPAN BALIK VERIFIKATOR AKTIF" in _text(at)

    at.session_state["page"] = "audit"
    at.run()
    next(b for b in at.button if b.key == "undo_JALA-F006").click().run()
    assert at.session_state["feedback"] == {} and "UMPAN BALIK VERIFIKATOR" not in _text(at)
    assert at.session_state["review_history"][-1]["action"] == "Umpan balik dibatalkan"


def test_feedback_reset_button_clears_everything():
    at = _audit_with("JALA-F006")
    next(b for b in at.button if b.key and "Dismiss" in b.key).click().run()
    at.session_state["page"] = "risk"
    at.run()
    next(b for b in at.button if b.key == "fb_reset").click().run()
    assert at.session_state["feedback"] == {} and not at.session_state["audited"]
    assert at.session_state["review_history"][-1]["action"] == "Umpan balik sesi diatur ulang"
