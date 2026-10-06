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
