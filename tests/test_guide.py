"""Panduan berbahasa sederhana (components/guide.py)."""
import re

from components import guide, tutorial

PAGES = {"dashboard", "risk", "network", "claim", "audit", "about"}


def test_every_page_has_a_guide():
    assert set(guide.PAGES) == PAGES
    for g in guide.PAGES.values():
        assert g["purpose"] and g["next"] and len(g["read"]) >= 3


def test_guide_text_has_no_hardcoded_numbers():
    for g in guide.PAGES.values():
        body = g["purpose"] + g["next"] + " ".join(g["read"])
        assert not re.search(r"\d+\s?%|Rp\s?\d|\d{3,}", body)


def test_glossary_covers_terms_used_in_tutorial():
    terms = {t for t, _ in guide.GLOSSARY}
    assert {"Klaster", "Skor risiko", "Verifikator", "Dismiss", "Data sintetis"} <= terms
    assert all(d.strip() for _, d in guide.GLOSSARY)


def test_tutorial_avoids_hard_jargon():
    body = " ".join(s["lead"] + " ".join(s["do"]) + s["tip"] for s in tutorial.STEPS).lower()
    for word in ("gradient boosting", "subgraf", "triase", "tipologi", "auc", "louvain"):
        assert word not in body, word


def test_page_header_skips_empty_eyebrow(monkeypatch):
    from components import layout
    seen = []
    monkeypatch.setattr(layout.st, "markdown", lambda html, **kw: seen.append(html))
    layout.page_header("", "teal", "Judul", "Sub")
    assert "j-pill" not in seen[0]
    layout.page_header("Label", "teal", "Judul", "Sub")
    assert "j-pill teal" in seen[1]
