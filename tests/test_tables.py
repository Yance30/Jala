"""HTML builder tabel (components/tables.py): escaping field teks bebas + struktur.

Field yang di-interpolasi lewat badge()/score_bar() adalah konstanta internal tepercaya
dan sengaja tidak di-escape di sini; yang dijaga test ini adalah field teks bebas yang
WAJIB di-escape oleh tables.py agar data klaster tak bisa menyuntik markup.
"""
import pytest

from components import tables

PAYLOAD = '<b>"Tom & Jerry"</b>'
ESCAPED = "&lt;b&gt;&quot;Tom &amp; Jerry&quot;&lt;/b&gt;"


def _risk_row(**over):
    row = {"icon_tone": "grey", "icon": "🛡", "name": "Klaster A", "status": ("Auto-flagged", "red"),
           "subtitle": "3 faskes", "score": 92, "conf": "tinggi", "metric": "graf+aturan",
           "typology": ("Phantom Billing", "amber"), "why": "pola mencurigakan"}
    row.update(over)
    return row


def _triage_row(**over):
    row = {"id": "JALA-F001", "score": 92, "name": "Klaster A", "nodes": "3 faskes",
           "typology": "Phantom Billing", "faskes": "F1, F2", "volume": 120,
           "value": "Rp 1.000", "status": ("Auto-flagged", "red")}
    row.update(over)
    return row


@pytest.mark.parametrize("field", ["icon_tone", "icon", "name", "subtitle", "why"])
def test_risk_table_escapes_free_text(field):
    html = tables.risk_table_html([_risk_row(**{field: PAYLOAD})])
    assert "<b>" not in html and PAYLOAD not in html               # markup mentah tidak lolos
    assert ESCAPED in html                                          # ter-escape sebagai entitas


@pytest.mark.parametrize("field", ["name", "nodes", "faskes", "value"])
def test_triage_table_escapes_free_text(field):
    html = tables.triage_table_html([_triage_row(**{field: PAYLOAD})])
    assert "<b>" not in html and PAYLOAD not in html
    assert ESCAPED in html


@pytest.mark.parametrize("idx", [0, 1, 2, 5])
def test_audit_faskes_escapes_free_text(idx):
    base = ["KODE", "Region", "klinik", ("inti", "red"), 40, "Rp 1.000"]
    base[idx] = PAYLOAD
    html = tables.audit_faskes_html([tuple(base)])
    assert "<b>" not in html and PAYLOAD not in html
    assert ESCAPED in html


def test_risk_table_structure_and_one_row_per_cluster():
    rows = [_risk_row(name="A", score=92), _risk_row(name="B", score=70)]
    html = tables.risk_table_html(rows)
    assert "<table" in html and "<thead>" in html and "<tbody>" in html
    assert html.count("<tr") == 1 + len(rows)                       # 1 baris header + 1 per klaster
    assert "92%" in html and "70%" in html                          # skor numerik tampil apa adanya


def test_triage_table_renders_numbers_and_highlight():
    rows = [_triage_row(id="JALA-F001", volume=120, score=92), _triage_row(id="JALA-F002", volume=7)]
    html = tables.triage_table_html(rows, selected_id="JALA-F002")
    assert html.count("<tr") == 1 + len(rows)
    assert "120" in html                                            # volume numerik tidak di-escape
    assert html.count('style="background:#E6F4F2;"') == 1           # hanya baris terpilih yang di-highlight


def test_audit_faskes_renders_volume_number():
    html = tables.audit_faskes_html([("K1", "R1", "klinik", ("inti", "red"), 55, "Rp 2.000")])
    assert "<table" in html and html.count("<tr") == 2              # header + 1 baris
    assert "55" in html                                             # volume numerik apa adanya


def test_empty_rows_produce_empty_body():
    for html in (tables.risk_table_html([]), tables.triage_table_html([]), tables.audit_faskes_html([])):
        assert "<tbody></tbody>" in html and html.count("<tr") == 1  # hanya baris header
