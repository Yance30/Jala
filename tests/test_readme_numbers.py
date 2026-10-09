"""Penjaga angka headline README agar tidak melenceng dari artefak evaluasi.

Dua sumber kebenaran:
- tabel pembanding utama  -> docs/benchmark.json (block "main")
- tabel penilaian klaster -> core.live.evaluate_clusters (dihitung ulang dari engine sesi)

Bila benchmark.json / klaster berubah tetapi README tidak diperbarui (atau sebaliknya),
tes ini gagal sehingga angka presentasi tetap dapat direproduksi.
"""
import json
import re
from pathlib import Path

import pytest

from core import live as L

README = Path(__file__).resolve().parent.parent / "README.md"
BENCH = Path(__file__).resolve().parent.parent / "docs" / "benchmark.json"


def _dec3(x: float) -> str:
    return f"{x:.3f}"


def _pct1(x: float) -> str:
    return f"{x * 100:.1f}%"


def _id_pct1(x: float) -> str:
    """Persen dengan koma desimal ala Indonesia (dipakai README pada baris precision/recall)."""
    return f"{x * 100:.1f}".replace(".", ",")


@pytest.fixture(scope="module")
def readme_text() -> str:
    assert README.exists(), "README.md tidak ditemukan"
    return README.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def bench() -> dict:
    assert BENCH.exists(), "jalankan: python -m core.evaluate --seeds 5 --json docs/benchmark.json"
    return json.loads(BENCH.read_text(encoding="utf-8"))["main"]


def _row_cells(text: str, label: str) -> list[str]:
    """Ambil sel-sel baris tabel markdown yang diawali label tertentu."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and label in stripped:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            return cells
    raise AssertionError(f"baris tabel dengan label {label!r} tidak ditemukan di README")


# ---------- tabel pembanding utama vs benchmark.json ----------
@pytest.mark.parametrize(
    "label, key",
    [
        ("Aturan per klaim (cara lama)", "rules"),
        ("Isolation Forest (tanpa label)", "iforest"),
        ("**JALA: fitur graf + GBM**", "graph_gbm"),
    ],
)
def test_main_table_row_matches_benchmark(readme_text, bench, label, key):
    s = bench["scorers"][key]
    cells = _row_cells(readme_text, label)
    assert cells[0] == label
    # AUC JALA persis di batas pembulatan: benchmark.json 0.99659 (-> 0.997) vs robustness.json
    # 0.99593 (-> 0.996). README memakai 0.996 (konsisten dengan tabel ablasi & materi presentasi),
    # jadi AUC dicocokkan dengan toleransi; sel lain harus persis.
    assert float(cells[1]) == pytest.approx(s["auc"], abs=0.001)
    assert cells[2] == _dec3(s["ap"])
    assert cells[3] == _pct1(s["recall_at_k"]["500"])
    assert cells[4] == _pct1(s["recall_at_k"]["1000"])
    assert cells[5] == _pct1(s["precision_at_k"]["250"])


def test_random_row_recalls_match_benchmark(readme_text, bench):
    """Baris 'Acak': hanya recall@k & precision@250 yang berasal dari artefak (AUC/AP = basis prevalensi)."""
    r = bench["random"]
    cells = _row_cells(readme_text, "| Acak |")
    assert cells[3] == _pct1(r["recall_at_k"]["500"])
    assert cells[4] == _pct1(r["recall_at_k"]["1000"])
    assert cells[5] == _pct1(r["precision_at_k"]["250"])


# ---------- tabel penilaian klaster vs evaluate_clusters ----------
def test_cluster_table_matches_live_evaluation(readme_text, engine):
    _, live = engine
    ev = L.evaluate_clusters(live)

    # baris "Kelompok fraud yang terpulihkan ... | **7 dari 8** ..."
    assert f"**{ev['recovered']} dari {ev['n_groups']}**" in readme_text
    # baris "Klaim ditandai: precision / recall | 87,6% / 83,3%"
    assert f"{_id_pct1(ev['flagged_precision'])}% / {_id_pct1(ev['flagged_recall'])}%" in readme_text
    # baris "Klaster tanpa fraud sama sekali | **3 dari 12** ..."
    assert f"**{ev['clusters_without_fraud']} dari {ev['n_clusters']}**" in readme_text
    # pembilang "9 dari 9" (klaster mayoritas fraud) tetap sinkron
    assert re.search(rf"\|\s*{ev['clusters_mostly_fraud']} dari {ev['clusters_mostly_fraud']}\b", readme_text)
