"""Browser checks for the KPI row and chart header spacing."""
import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect  # noqa: E402

pytestmark = pytest.mark.e2e
expect.set_options(timeout=90_000)


def _open(page, url, target):
    page.goto(f"{url}/?page={target}&tour=0")
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()


def test_risk_kpi_cards_have_equal_heights(app_url, page):
    _open(page, app_url, "risk")
    cards = page.locator(".j-risk-kpi-card")
    expect(cards).to_have_count(4)
    heights = [box["height"] for box in cards.evaluate_all(
        "els => els.map(el => el.getBoundingClientRect().toJSON())")]
    assert max(heights) - min(heights) <= 1, heights


def test_about_chart_headers_keep_nonnegative_spacing(app_url, page):
    _open(page, app_url, "about")
    headers = page.locator(".j-eqhead")
    expect(headers.first).to_be_visible()
    measurements = headers.evaluate_all("""els => els.map(el => {
      const style = getComputedStyle(el);
      const parentStyle = getComputedStyle(el.parentElement);
      return {marginBottom: parseFloat(style.marginBottom),
              height: el.getBoundingClientRect().height,
              parentMarginBottom: parseFloat(parentStyle.marginBottom),
              parentTag: el.parentElement.tagName,
              parentClass: el.parentElement.className};
    })""")
    assert measurements, "About should render chart headings"
    for pair in measurements:
        assert pair["marginBottom"] >= 0, pair
        assert pair["parentMarginBottom"] >= 0, pair
        assert pair["height"] >= 94, pair


def test_operational_layout_at_phone_tablet_and_desktop_sizes(app_url, page):
    for route in ("data_prediction", "batch_review", "system_status", "dashboard", "risk", "network", "claim", "audit", "about"):
        page.goto(f"{app_url}/?page={route}&tour=0")
        expect(page.locator(".j-topbar")).to_be_visible()
        expect(page.get_by_role("button", name="Stop", exact=True)).not_to_be_visible()
        for width in (320, 390, 768, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 900})
            page.wait_for_timeout(350)  # Sidebar and column transitions.
            sizes = page.locator('[data-testid="stMain"]').evaluate(
                "el => ({scroll:el.scrollWidth, client:el.clientWidth})")
            assert sizes["scroll"] <= sizes["client"] + 2, (route, width, sizes)
            if width <= 640:
                buttons = page.locator('[data-testid="stMain"] button').evaluate_all(
                    "els => els.filter(e => e.offsetParent && e.closest('[data-testid=stButton]')).map(e => e.getBoundingClientRect().height)")
                assert all(height >= 44 for height in buttons), (route, width, buttons)


def test_weekly_capacity_axis_titles_fit_chart(app_url, page, tmp_path):
    page.goto(f"{app_url}/?page=about&tour=0")
    title = page.locator(".ytitle").filter(has_text="Total klaim fraud sintetis")
    expect(title).to_be_visible()
    chart = page.get_by_test_id("stPlotlyChart").filter(has=title)
    for width in (320, 390, 768, 1400):
        page.set_viewport_size({"width": width, "height": 900})
        chart.scroll_into_view_if_needed()
        page.wait_for_timeout(700)  # Plotly resizes after the responsive layout changes.
        bounds = chart.bounding_box()
        for label in (chart.locator(".ytitle"), chart.locator(".xtitle")):
            box = label.bounding_box()
            assert box and bounds
            assert box["x"] >= bounds["x"] - 1, (width, box, bounds)
            assert box["y"] >= bounds["y"] - 1, (width, box, bounds)
            assert box["x"] + box["width"] <= bounds["x"] + bounds["width"] + 1, (width, box, bounds)
            assert box["y"] + box["height"] <= bounds["y"] + bounds["height"] + 1, (width, box, bounds)
        chart.screenshot(path=str(tmp_path / f"capacity-{width}.png"))
