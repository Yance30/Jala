"""Berkas bukti per klaster (core/evidence.py)."""
import io
import json
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import pytest

from core import evidence, feedback

FILES = {"metadata.json", "ringkasan.md", "klaim_terkait.csv", "faskes.csv", "dokter.csv", "subgraf.svg", "subgraf.json"}


def _open(lv, cid, **kw):
    return zipfile.ZipFile(io.BytesIO(evidence.build_pack(lv, cid, generated_at="2026-10-03 10:00", **kw)))


@pytest.fixture(scope="module")
def selfref(engine):
    return next(c["id"] for c in engine[1].clusters if c["typology"] == "Self-Referral")


def test_pack_contains_all_files(engine, selfref):
    z = _open(engine[1], selfref)
    assert {n.split("/", 1)[1] for n in z.namelist()} == FILES
    assert all(n.startswith(selfref + "/") for n in z.namelist())


def test_claims_csv_matches_cluster(engine, selfref):
    lv = engine[1]
    z = _open(lv, selfref)
    df = pd.read_csv(z.open(f"{selfref}/klaim_terkait.csv"))
    assert len(df) == lv.by_id[selfref]["n"] and set(df.claim_id) == set(lv.by_id[selfref]["idx"])
    assert df.skor.is_monotonic_decreasing and (df.alasan.fillna("") != "").any()


def test_no_label_columns_leak_into_pack(engine, selfref):
    z = _open(engine[1], selfref)
    for name in ("klaim_terkait.csv", "faskes.csv", "dokter.csv"):
        cols = set(pd.read_csv(z.open(f"{selfref}/{name}")).columns)
        assert not ({"is_fraud", "typology", "group", "legit_kind", "label"} & cols)


def test_summary_is_honest_and_complete(engine, selfref):
    md = _open(engine[1], selfref).read(f"{selfref}/ringkasan.md").decode()
    for needle in (selfref, "sintetis", "bukan temuan", "Saran untuk pemeriksa dokumen", "Self-Referral",
                   "Simulasi struktural", "Belum ada keputusan", "Batasan"):
        assert needle in md, needle
    assert "klaim, total tarif Rp" in md          # pemisah ribuan tidak boleh merusak koma kalimat
    assert "bukan ketentuan regulasi" in md


def test_summary_records_verifier_decision(engine, selfref):
    lv = engine[1]
    fb = feedback.record({}, selfref, "dismiss", note="UGD terkonfirmasi", at="2026-10-03 09:00")
    md = _open(feedback.adjust(lv, fb), selfref, feedback=fb).read(f"{selfref}/ringkasan.md").decode()
    assert "dismiss" in md and "UGD terkonfirmasi" in md and "skor dasar" in md


def test_doctor_csv_includes_whatif_impact(engine, selfref):
    df = pd.read_csv(_open(engine[1], selfref).open(f"{selfref}/dokter.csv"))
    assert {"peran_struktur", "bobot_hubungan_hilang_pct", "jika_dikeluarkan"} <= set(df.columns)
    assert df.iloc[0].peran_struktur == "inti"


def test_subgraph_svg_is_valid_xml_with_labels(engine, selfref):
    lv = engine[1]
    z = _open(lv, selfref)
    root = ET.fromstring(z.read(f"{selfref}/subgraf.svg"))
    assert root.tag.endswith("svg")
    text = " ".join(t.text or "" for t in root.iter() if t.tag.endswith("text"))
    assert selfref in text and lv.world.faskes.set_index("faskes_id").name[lv.by_id[selfref]["faskes"][0]] in text
    g = json.loads(z.read(f"{selfref}/subgraf.json"))
    assert g["nodes"] and g["edges"]


def test_pack_is_deterministic_for_fixed_timestamp(engine, selfref):
    a = evidence.build_pack(engine[1], selfref, generated_at="x")
    b = evidence.build_pack(engine[1], selfref, generated_at="x")
    za, zb = zipfile.ZipFile(io.BytesIO(a)), zipfile.ZipFile(io.BytesIO(b))
    assert all(za.read(n) == zb.read(n) for n in za.namelist())


def test_every_cluster_builds(engine):
    for c in engine[1].clusters:
        assert len(evidence.build_pack(engine[1], c["id"])) > 2000


def test_rupiah_helper():
    assert evidence._rp(73626503) == "73.626.503"


def test_svg_escapes_markup_in_labels():
    nodes = [{"id": "f_1", "type": "faskes", "label": "A&B <x>", "sub": "", "risk": True, "x": 1, "y": 1}]
    ET.fromstring(evidence.subgraph_svg(nodes, [], "t & <u>"))
