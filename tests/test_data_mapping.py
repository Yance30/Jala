"""Dokumen pemetaan data (docs/pemetaan-data.md) dan kontrak data minimal (core/contract.py) harus jujur dan sinkron."""
import re
from pathlib import Path

import pytest

from core import contract
from core.detect import build_features
from core.synthetic import generate_world

DOC = (Path(__file__).resolve().parent.parent / "docs" / "pemetaan-data.md").read_text(encoding="utf-8")
TABLES = ("claims", "faskes", "affiliations", "patients")


@pytest.fixture(scope="module")
def world():
    return generate_world(seed=7)


def test_every_synthetic_column_is_documented(world):
    for t in TABLES:
        for col in getattr(world, t).columns:
            assert f"`{col}`" in DOC, f"{t}.{col} belum ada di docs/pemetaan-data.md"


def test_label_columns_are_documented_as_evaluation_only(world):
    for col in world.labels.columns:
        if col != "claim_id":
            assert f"`{col}`" in DOC, col
    assert "hanya dipakai untuk menilai" in DOC


def test_doc_admits_official_schema_is_unknown():
    assert "tidak kami ketahui" in DOC and "belum dikonfirmasi" in DOC


def test_contract_matches_the_documented_minimal_table(world):
    section = DOC.split("## 2. Kontrak data minimal")[1].split("## 3.")[0]
    for table, cols in contract.MINIMAL.items():
        row = next(l for l in section.splitlines() if l.startswith(f"| `{table}`"))
        assert re.findall(r"`([a-z_]+)`", row)[1:] == cols, table


def test_synthetic_world_satisfies_contract(world):
    assert contract.missing(claims=world.claims, faskes=world.faskes, affiliations=world.affiliations,
                            patients=world.patients) == {}


def test_pipeline_runs_on_minimal_columns_only(world):
    """Kontrak jujur: kolom di luar kontrak (mis. faskes.name) tidak dibutuhkan, hasilnya identik."""
    full = build_features(world.claims, world.faskes, world.affiliations, world.patients)
    mini = build_features(world.claims[contract.MINIMAL["claims"]], world.faskes[contract.MINIMAL["faskes"]],
                          world.affiliations[contract.MINIMAL["affiliations"]],
                          world.patients[contract.MINIMAL["patients"]])
    assert full.equals(mini)


def test_missing_columns_give_clear_error(world):
    with pytest.raises(ValueError) as e:
        build_features(world.claims.drop(columns=["submit_ts"]), world.faskes.drop(columns=["capacity"]),
                       world.affiliations, world.patients)
    msg = str(e.value)
    assert "submit_ts" in msg and "capacity" in msg and "pemetaan-data.md" in msg


def test_doc_lists_missing_fields_and_panitia_questions():
    for needle in ("Nomor SEP", "kode INA-CBG", "Status verifikasi", "Kapabilitas", "ketelitian waktu", "Pertanyaan untuk panitia"):
        assert needle.lower() in DOC.lower(), needle
    assert len(re.findall(r"^\d+\. ", DOC.split("## 5.")[1], flags=re.M)) >= 7
