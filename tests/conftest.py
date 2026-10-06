import hashlib
import os
import tempfile

import pytest

from core import live as L
from core.evaluate import benchmark
from core.synthetic import generate_world


def pytest_runtest_setup(item):
    """Isolasi demo SQLite per tes, termasuk proses Streamlit yang dipakai E2E."""
    digest = hashlib.sha256(item.nodeid.encode("utf-8")).hexdigest()[:12]
    os.environ["JALA_REVIEW_HISTORY_DB"] = os.path.join(
        tempfile.gettempdir(), f"jala-review-test-{os.getpid()}-{digest}.sqlite3"
    )


@pytest.fixture(scope="session")
def engine():
    """Dunia sintetis default + skor + klaster, dibangun sekali untuk seluruh sesi tes."""
    w = generate_world()
    bm = benchmark(world=w)
    return w, L.build(w, bm.scored)
