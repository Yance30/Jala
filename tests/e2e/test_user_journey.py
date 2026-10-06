"""Alur pengguna nyata di browser: dashboard -> risk ranking -> claim details -> audit action,
unduh berkas bukti, dismiss lalu batalkan, tautan langsung, dan tutorial."""
import io
from pathlib import Path
import zipfile

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect  # noqa: E402

pytestmark = pytest.mark.e2e
expect.set_options(timeout=90_000)       # akses pertama menghitung mesin (sekitar 10 detik) + animasi pembuka


def _open(page, url, query="/?tour=0"):
    page.goto(url + query)
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()      # intro selesai


def _nav(page, label):
    page.locator('[data-testid="stSidebar"]').get_by_text(label, exact=True).click()


def _text(page, needle):
    return page.get_by_text(needle).first


def _go_to_audit(page):
    _nav(page, "Risk Ranking")
    expect(_text(page, "Prioritas Klaster")).to_be_visible()
    page.get_by_role("button", name="Buka Claim Details").click()
    page.get_by_role("button", name="Buka Audit Action").click()
    expect(_text(page, "bagaimana kalau dokter ini dikeluarkan")).to_be_visible()


def test_journey_dashboard_to_audit_with_dismiss_and_undo(app_url, page, js_errors):
    _open(page, app_url)
    expect(_text(page, "Ringkasan Prioritas Pemeriksaan")).to_be_visible()

    _go_to_audit(page)
    expect(page.get_by_text("UMPAN BALIK VERIFIKATOR")).to_have_count(0)        # belum ada keputusan

    page.get_by_role("button", name="Arsipkan & Turunkan Skor").click()
    expect(_text(page, "UMPAN BALIK VERIFIKATOR")).to_be_visible()
    expect(_text(page, "Riwayat pemeriksaan klaster")).to_be_visible()
    page.get_by_text("Riwayat pemeriksaan klaster").click()
    with page.expect_download() as download:
        page.get_by_role("button", name="Unduh riwayat kasus (.CSV)").click()
    csv_content = Path(download.value.path()).read_text(encoding="utf-8-sig")
    assert "JALA-F031" in csv_content and "Tandai sebagai pola wajar" in csv_content
    expect(page.get_by_text("→ 40%").first).to_be_visible()                     # skor turun ke 40% dari skor dasar

    _nav(page, "Risk Ranking")
    expect(_text(page, "UMPAN BALIK VERIFIKATOR AKTIF")).to_be_visible()        # peringkat berubah di layar
    page.get_by_role("button", name="Atur ulang umpan balik").click()
    expect(page.get_by_text("UMPAN BALIK VERIFIKATOR AKTIF")).to_have_count(0)
    assert not js_errors, js_errors


def test_undo_from_audit_page(app_url, page):
    _open(page, app_url)
    _go_to_audit(page)
    page.get_by_role("button", name="Arsipkan & Turunkan Skor").click()
    expect(_text(page, "UMPAN BALIK VERIFIKATOR")).to_be_visible()
    page.get_by_role("button", name="Batalkan umpan balik klaster ini").click()
    expect(page.get_by_text("UMPAN BALIK VERIFIKATOR")).to_have_count(0)


def test_evidence_pack_downloads_as_valid_zip(app_url, page):
    _open(page, app_url)
    _go_to_audit(page)
    with page.expect_download() as dl:
        page.get_by_text("Berkas Bukti Klaster (.zip)").first.click()
    name = dl.value.suggested_filename
    assert name.startswith("jala_bukti_JALA-") and name.endswith(".zip")
    z = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
    files = {n.split("/", 1)[1] for n in z.namelist()}
    assert files == {"ringkasan.md", "klaim_terkait.csv", "faskes.csv", "dokter.csv", "subgraf.svg", "subgraf.json"}
    md = z.read([n for n in z.namelist() if n.endswith("ringkasan.md")][0]).decode()
    assert "sintetis" in md and "Saran untuk pemeriksa dokumen" in md


def test_deep_link_about_shows_measured_evidence(app_url, page, js_errors):
    _open(page, app_url, "/?page=about&tour=0")
    expect(_text(page, "Hasil terukur, bukan angka ketikan")).to_be_visible()
    expect(_text(page, "Batasan yang perlu dibaca")).to_be_visible()
    assert not js_errors, js_errors


def test_tutorial_opens_navigates_and_reopens(app_url, page, js_errors):
    _open(page, app_url, "/")                                    # tanpa ?tour=0: terbuka otomatis
    expect(_text(page, "Selamat datang di JALA")).to_be_visible()
    page.get_by_role("button", name="Berikutnya").click()
    expect(_text(page, "1. Dashboard: lihat gambaran besar")).to_be_visible()
    page.get_by_role("button", name="Sebelumnya").click()
    expect(_text(page, "Selamat datang di JALA")).to_be_visible()
    for _ in range(3):
        page.get_by_role("button", name="Berikutnya").click()
        page.wait_for_timeout(700)
    expect(_text(page, "3. Network Graph: lihat hubungannya")).to_be_visible()

    page.get_by_role("button", name="Buka halaman ini").click()
    expect(page.get_by_text("3. Network Graph: lihat hubungannya")).to_have_count(0)    # dialog tertutup
    expect(_text(page, "PERINGATAN KLASTER")).to_be_visible()                         # sudah di Network Graph

    page.get_by_role("button", name="Cara Pakai").first.click()
    expect(_text(page, "3. Network Graph: lihat hubungannya")).to_be_visible()          # lanjut di langkah terakhir
    assert not js_errors, js_errors


def test_tour_zero_skips_dialog(app_url, page):
    _open(page, app_url, "/?tour=0")
    expect(_text(page, "Ringkasan Prioritas Pemeriksaan")).to_be_visible()
    expect(page.get_by_text("Selamat datang di JALA")).to_have_count(0)


def test_demo_case_opens_traceable_claim_review_on_mobile(app_url, page):
    _open(page, app_url)
    expect(page.get_by_role("button", name="Mulai tinjau kasus")).to_be_visible()
    page.set_viewport_size({"width": 390, "height": 844})
    page.get_by_role("button", name="Mulai tinjau kasus").click()
    expect(_text(page, "Detail Klaim")).to_be_visible()
    expect(_text(page, "Telusuri klaim sumber dan alasan per klaim")).to_be_visible()
    page.wait_for_timeout(500)
    width = page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
    assert width <= 392, f"Halaman melebar ke {width}px pada viewport 390px"


def test_dashboard_provenance_and_reset_demo(app_url, page):
    _open(page, app_url)
    page.get_by_text("Asal data dan cara menghitung skor").click()
    expect(_text(page, "Seed 2026")).to_be_visible()
    expect(_text(page, "Evaluasi dunia nyata belum tersedia")).to_be_visible()

    _go_to_audit(page)
    page.get_by_role("button", name="Arsipkan & Turunkan Skor").click()
    expect(_text(page, "UMPAN BALIK VERIFIKATOR")).to_be_visible()
    _nav(page, "Dashboard")
    page.get_by_role("button", name="Reset demo").click()
    _nav(page, "Risk Ranking")
    expect(page.get_by_text("UMPAN BALIK VERIFIKATOR AKTIF")).to_have_count(0)
