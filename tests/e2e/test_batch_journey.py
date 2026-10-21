"""Real upload, persisted review, safe export and anonymous-session isolation."""
from pathlib import Path
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def prepare_batch(page, app_url, tmp_path):
    expect.set_options(timeout=90_000)
    from components.external_lab import example_files
    paths = []
    for name, content in example_files().items():
        path = tmp_path / name
        path.write_bytes(content)
        paths.append(str(path))
    page.goto(app_url + "/?tour=0&page=data_prediction")
    page.locator('input[type="file"]').set_input_files(paths)
    page.get_by_role("button", name="Validasi paket unggahan", exact=True).click()
    expect(page.get_by_text("Paket aktif lolos validasi struktur", exact=False)).to_be_visible()
    page.get_by_role("button", name="Latih historis dan prediksi periode berikutnya", exact=True).click()
    expect(page.get_by_role("button", name="Buka antrean tinjauan", exact=True)).to_be_visible()


@pytest.mark.parametrize("app_url", ["local"], indirect=True)
def test_upload_review_reload_export_delete(app_url, page, tmp_path):
    prepare_batch(page, app_url, tmp_path)
    page.get_by_role("button", name="Simpan model terlatih ke basis data lokal", exact=True).click()
    page.get_by_role("button", name="Buka antrean tinjauan", exact=True).click()
    page.get_by_label("Catatan pemeriksa", exact=True).fill("=1+1")
    page.get_by_label("Nama pemeriksa", exact=True).fill("Pemeriksa sintetis")
    page.get_by_role("button", name="Simpan tinjauan", exact=True).click()
    expect(page.get_by_text("Hasil pemeriksaan berhasil disimpan.", exact=False)).to_be_visible()
    detail_heading = page.get_by_role("heading", name="Detail pemeriksaan", exact=False).last
    initial_detail = detail_heading.inner_text()
    page.get_by_role("button", name="Simpan & lanjut", exact=True).click()
    expect(detail_heading).not_to_have_text(initial_detail)
    expect(page.get_by_label("Nama pemeriksa", exact=True).last).to_have_value("Pemeriksa sintetis")
    page.get_by_label("Cari ID klaim atau faskes", exact=True).fill("klaim-yang-tidak-ada-xyz")
    page.get_by_label("Cari ID klaim atau faskes", exact=True).press("Enter")
    expect(page.get_by_role("button", name="Reset filter", exact=True)).to_be_visible()
    page.get_by_role("button", name="Reset filter", exact=True).click()
    expect(page.get_by_label("Cari ID klaim atau faskes", exact=True)).to_have_value("")
    page.goto(app_url + "/?tour=0&page=batch_review")
    expect(page.get_by_text("Keputusan tersimpan:", exact=False)).to_be_visible(timeout=90_000)
    expect(page.get_by_role("button", name="Unduh riwayat tinjauan", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Stop", exact=True)).not_to_be_visible()
    for width in (320, 390, 768, 1024, 1440):
        page.set_viewport_size({"width": width, "height": 900})
        page.wait_for_timeout(350)
        main_size = page.get_by_test_id("stMain").evaluate(
            "el => ({scroll:el.scrollWidth, client:el.clientWidth})")
        assert main_size["scroll"] <= main_size["client"] + 2, (width, main_size)
        if width <= 640:
            save_box = page.get_by_role("button", name="Simpan tinjauan", exact=True).bounding_box()
            assert save_box["width"] >= width - 80, (width, save_box)
        if width <= 900:
            columns = page.get_by_test_id("stMain").get_by_test_id("stColumn")
            boxes = columns.evaluate_all("els => els.slice(0, 3).map(e => e.getBoundingClientRect().toJSON())")
            assert len(boxes) == 3
            assert all(b["top"] >= a["bottom"] - 2 for a, b in zip(boxes, boxes[1:])), (width, boxes)
    page.set_viewport_size({"width": 1400, "height": 1000})
    page.screenshot(path=str(tmp_path / "review-desktop.png"), full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(800)  # Allow responsive CSS transitions to finish before visual capture.
    expect(page.get_by_role("button", name="Simpan tinjauan", exact=True)).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2")
    page.screenshot(path=str(tmp_path / "review-mobile.png"), full_page=True)
    page.get_by_label("Nama pemeriksa", exact=True).scroll_into_view_if_needed()
    page.locator('nav[aria-label="Pintasan tinjauan"]').get_by_role("link", name="Ke hasil tinjauan", exact=True).click()
    expect(page.locator("#hasil-tinjauan")).to_be_in_viewport()
    page.locator('nav[aria-label="Pintasan tinjauan"]').get_by_role("link", name="Kembali ke antrean", exact=True).click()
    expect(page.locator("#antrean-pemeriksaan")).to_be_in_viewport()
    page.get_by_label("Nama pemeriksa", exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(tmp_path / "review-mobile-form.png"))
    page.set_viewport_size({"width": 1400, "height": 1000})
    with page.expect_download() as result:
        page.get_by_role("button", name="Unduh antrean dan hasil tinjauan", exact=True).click()
    content = Path(result.value.path()).read_text(encoding="utf-8-sig")
    assert "'=1+1" in content
    assert "work_priority" in content and "comparison_evidence" in content
    page.goto(app_url + "/?tour=0&page=system_status")
    page.get_by_text("Penyimpanan dan penghapusan data", exact=True).click()
    page.get_by_text("Hapus seluruh model, riwayat observasi, antrean dan keputusan dalam ruang saya", exact=True).click()
    expect(page.get_by_label("Hapus seluruh model, riwayat observasi, antrean dan keputusan dalam ruang saya")).to_be_checked()
    page.get_by_role("button", name="Hapus seluruh data ruang saya", exact=True).click()
    expect(page.get_by_text("Belum ada antrean tinjauan tersimpan.", exact=True)).to_be_visible()


def test_demo_browser_sessions_do_not_share_queues(app_url, page, browser, tmp_path):
    prepare_batch(page, app_url, tmp_path)
    page.get_by_role("button", name="Buka antrean tinjauan", exact=True).click()
    expect(page.get_by_text("Klaim dalam batch", exact=True)).to_be_visible()
    other = browser.new_context()
    try:
        second = other.new_page()
        second.goto(app_url + "/?tour=0&page=batch_review")
        expect(second.get_by_text("Belum ada antrean.", exact=False)).to_be_visible(timeout=90_000)
        expect(page.get_by_text("Klaim dalam batch", exact=True)).to_be_visible()
    finally:
        other.close()
