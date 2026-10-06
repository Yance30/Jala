"""Posisi modus Healthkathon 2026 dan kejujuran teks layar: JALA = prioritas pemeriksaan, bukan pembuktian."""
import io
import re
import zipfile
from pathlib import Path

from streamlit.testing.v1 import AppTest

from core import evidence, modus

ROOT = Path(__file__).resolve().parent.parent
APP = str(ROOT / "app.py")


def test_numbers_and_names_match_guidebook():
    assert {k: v["no"] for k, v in modus.MODUS.items()} == {"Phantom Billing": 6, "Self-Referral": 10, "Repeat Billing": 11}
    assert modus.MODUS["Phantom Billing"]["nama"].startswith("Phantom billing")
    assert modus.MODUS["Self-Referral"]["nama"].startswith("Self-referral")
    assert modus.MODUS["Repeat Billing"]["nama"].startswith("Repeat billing")


def test_every_cluster_typology_has_a_modus_entry(engine):
    assert {c["typology"] for c in engine[1].clusters} <= set(modus.MODUS)


def test_each_modus_states_a_limit_of_proof():
    for t, m in modus.MODUS.items():
        assert m["definisi"] and m["ditangkap"] and len(m["batas"]) > 40, t
    assert "tidak memuat status pembayaran" in modus.MODUS["Repeat Billing"]["batas"]
    assert "tidak memuat kapabilitas faskes" in modus.MODUS["Self-Referral"]["batas"]
    assert "pemeriksaan lapangan" in modus.MODUS["Phantom Billing"]["batas"]
    assert "bukan pembuktian" in modus.PRINSIP


def test_evidence_pack_states_modus_and_limit_for_every_cluster(engine):
    lv = engine[1]
    for c in lv.clusters:
        z = zipfile.ZipFile(io.BytesIO(evidence.build_pack(lv, c["id"])))
        md = z.read(f"{c['id']}/ringkasan.md").decode()
        m = modus.MODUS[c["typology"]]
        assert f"no. {m['no']}" in md and "Batas pembuktian" in md and m["batas"] in md, c["id"]
        assert modus.PRINSIP in md, c["id"]


def _page(page, cid):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["intro_done"] = True
    at.session_state["tour_seen"] = True
    at.session_state["page"] = page
    at.session_state["selected_cluster"] = cid
    return at.run()


def test_claim_details_and_audit_show_modus_note(engine):
    for page in ("claim", "audit"):
        c = engine[1].by_id["JALA-F006"]
        at = _page(page, "JALA-F006")
        txt = " ".join(m.value for m in at.markdown)
        assert not at.exception
        assert modus.headline(c["typology"]) in txt and "Batas pembuktian" in txt and modus.PRINSIP in txt, page


def test_no_invented_integrations_or_regulations_in_ui_copy():
    """Teks layar tidak boleh mengklaim integrasi sistem atau regulasi yang tidak ada/terverifikasi."""
    banned = ["BAPK", "SP-Audit", "Form 04", "perbendaharaan", "Standar BPJS", "nomor SEP terkait", "e-Klaim INA-CBG",
              "dieksekusi & ditandatangani", "Konfirmasi & Tandatangani", "terintegrasi otomatis"]
    for f in [*(ROOT / "views").glob("*.py"), *(ROOT / "components").glob("*.py"), ROOT / "data" / "mock_data.py"]:
        text = f.read_text(encoding="utf-8")
        for b in banned:
            assert b not in text, f"{f.name}: '{b}'"


def test_freeze_is_labelled_simulation_everywhere():
    from data.mock_data import AUDIT_ACTIONS
    freeze = AUDIT_ACTIONS[0]
    assert "Simulasi" in freeze["button"] and "belum terhubung" in freeze["body"]
    src = (ROOT / "views" / "audit_action.py").read_text(encoding="utf-8")
    assert "(Simulasi)" in src and "tidak ada sistem BPJS yang dihubungi" in src
    assert re.search(r"FREEZE dicatat \(simulasi", src)
