"""Fondasi tes end-to-end: menjalankan aplikasi Streamlit sungguhan dan mengendalikannya lewat browser.

Dilewati otomatis bila Playwright atau Chromium belum terpasang:
    pip install -r requirements-dev.txt && playwright install chromium
"""
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
START_TIMEOUT = 90


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def app_url():
    port = _free_port()
    log = tempfile.NamedTemporaryFile("w+", suffix="_streamlit.log", delete=False)
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
         "--server.port", str(port), "--browser.gatherUsageStats", "false"],
        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + START_TIMEOUT
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                if urllib.request.urlopen(f"{url}/_stcore/health", timeout=2).status == 200:
                    break
            except OSError:
                time.sleep(0.5)
        else:
            raise RuntimeError("Streamlit tidak siap tepat waktu")
        if proc.poll() is not None:
            log.seek(0)
            raise RuntimeError("Streamlit berhenti saat start:\n" + log.read()[-2000:])
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


@pytest.fixture(scope="session")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:     # Chromium belum diunduh
            pytest.skip(f"Chromium belum terpasang (jalankan `playwright install chromium`): {type(e).__name__}")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, accept_downloads=True)
    p = ctx.new_page()
    p.set_default_timeout(90_000)
    yield p
    ctx.close()


@pytest.fixture
def js_errors(page):
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    return errors
