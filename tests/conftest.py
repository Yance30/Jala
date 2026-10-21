import hashlib
import os
import tempfile
from pathlib import Path

import pytest

from core import live as L
from core.evaluate import benchmark
from core.synthetic import generate_world


def _ensure_writable_tempdir() -> str:
    """Use a repo-local temp root to avoid Windows temp folders blocked by stale permissions."""
    candidates = [
        Path(__file__).resolve().parent.parent / ".pytest_tmp",
        Path.home() / ".jala-pytest",
    ]
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            marker = candidate / ".write-test-marker"
            marker.write_text("ok", encoding="utf-8")
            marker.unlink(missing_ok=True)
            return str(candidate)
        except OSError:
            continue
    return tempfile.gettempdir()


TEMP_ROOT = _ensure_writable_tempdir()
for env_name in ("TMP", "TEMP", "TMPDIR"):
    os.environ[env_name] = TEMP_ROOT

tempfile.tempdir = TEMP_ROOT


def pytest_runtest_setup(item):
    """Isolasi proses tes; server E2E mendapat environment eksplisit dari fixture-nya."""
    os.environ["JALA_MODE"] = "local"
    digest = hashlib.sha256(item.nodeid.encode("utf-8")).hexdigest()[:12]
    os.environ["JALA_REVIEW_HISTORY_DB"] = os.path.join(
        tempfile.gettempdir(), f"jala-review-test-{os.getpid()}-{digest}.sqlite3"
    )
    os.environ["JALA_BATCH_DB"] = os.path.join(
        tempfile.gettempdir(), f"jala-batch-test-{os.getpid()}-{digest}.sqlite3"
    )


@pytest.fixture(scope="session")
def engine():
    """Dunia sintetis default + skor + klaster, dibangun sekali untuk seluruh sesi tes."""
    w = generate_world()
    bm = benchmark(world=w)
    return w, L.build(w, bm.scored)
