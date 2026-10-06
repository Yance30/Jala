import base64

import streamlit as st

from components.theme import ICON_CALENDAR_SVG, ICON_USER_SVG, LOGO_SVG  # BARU
from data.mock_data import (
    FOOTER_CUTOFF,
    FOOTER_STATUS,
    PAGE_TITLES,
    QUARTER,
    QUARTER_SHORT,
)


# =========================================================
# LATAR BELAKANG JARINGAN
# =========================================================

_BG_NODES = [
    (120, 120),
    (300, 60),
    (520, 140),
    (760, 80),
    (940, 170),
    (200, 320),
    (430, 300),
    (680, 280),
    (880, 360),
    (330, 470),
    (600, 460),
    (820, 500),
]

_BG_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (1, 6),
    (2, 6),
    (3, 7),
    (4, 8),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (6, 9),
    (6, 10),
    (7, 10),
    (8, 11),
    (10, 11),
]

# Node anomali
_BG_RISK = 6


_BG_SVG_STYLE = (
    "<style>"
    ".e{stroke:#0F766E;stroke-opacity:.14;stroke-width:1.2}"
    ".e.r{stroke:#F97316;stroke-opacity:.25}"
    ".n{fill:#0F766E;fill-opacity:.22}"
    ".n.r{fill:#F97316;fill-opacity:.7}"
    ".g{fill:none;stroke:#F97316;stroke-width:1.4;stroke-opacity:.5;"
    "transform-box:fill-box;"
    "transform-origin:center;"
    "animation:ring 7s ease-out infinite}"
    "@keyframes ring{"
    "0%{transform:scale(.7);opacity:.7}"
    "100%{transform:scale(3);opacity:0}"
    "}"
    "@media (prefers-reduced-motion:reduce){"
    ".g{animation:none}"
    "}"
    "</style>"
)


def _bg_svg() -> str:
    edges = []

    for a, b in _BG_EDGES:
        (x1, y1), (x2, y2) = _BG_NODES[a], _BG_NODES[b]

        risk = _BG_RISK in (a, b)

        edges.append(
            f'<line class="e{" r" if risk else ""}" '
            f'x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}"/>'
        )

    nodes = []

    for i, (x, y) in enumerate(_BG_NODES):
        risk = i == _BG_RISK

        if risk:
            nodes.append(
                f'<circle class="g" cx="{x}" cy="{y}" r="8"/>'
            )

        nodes.append(
            f'<circle class="n{" r" if risk else ""}" '
            f'cx="{x}" cy="{y}" '
            f'r="{7 if risk else 4}"/>'
        )

    defs = (
        '<defs>'
        '<radialGradient id="fade" cx="50%" cy="50%" r="60%">'
        '<stop offset="0" stop-color="#000"/>'
        '<stop offset=".5" stop-color="#222"/>'
        '<stop offset="1" stop-color="#fff"/>'
        '</radialGradient>'
        '<mask id="m">'
        '<rect width="1000" height="560" fill="url(#fade)"/>'
        '</mask>'
        '</defs>'
    )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="1000" height="560" '
        'viewBox="0 0 1000 560" '
        'preserveAspectRatio="xMidYMid slice">'
        + _BG_SVG_STYLE
        + defs
        + '<g mask="url(#m)">'
        + "".join(edges)
        + "".join(nodes)
        + "</g>"
        "</svg>"
    )


_BG_B64 = base64.b64encode(
    _bg_svg().encode("utf-8")
).decode("ascii")


# =========================================================
# SIDEBAR CSS
# =========================================================

_SIDEBAR_CSS = (
    ".block-container, "
    "[data-testid='stMainBlockContainer']"
    "{transition:max-width .25s ease;}"

    "section[data-testid='stSidebar'][aria-expanded='false']"
    "{"
    "width:0 !important;"
    "min-width:0 !important;"
    "margin-left:0 !important;"
    "border-right:0 !important;"
    "overflow:hidden !important;"
    "}"

    ".stApp:has("
    "section[data-testid='stSidebar'][aria-expanded='false']"
    ") .block-container,"

    ".stApp:has("
    "section[data-testid='stSidebar'][aria-expanded='false']"
    ") [data-testid='stMainBlockContainer']"
    "{"
    "max-width:100% !important;"
    "width:100% !important;"
    "padding-left:2rem !important;"
    "padding-right:2rem !important;"
    "}"
)


# =========================================================
# BACKGROUND CSS
# =========================================================

BG_CSS = (
    "<style>"

    ".stApp{"
    "background:"
    "url('data:image/svg+xml;base64,__B64__') "
    "center / cover no-repeat fixed,"
    "radial-gradient("
    "circle at 20% 10%, "
    "#E6F4F2 0%, "
    "#F8FAFC 60%"
    ") !important;"
    "}"

    '[data-testid="stAppViewContainer"], '
    '[data-testid="stMain"], '
    '[data-testid="stHeader"], '
    '.main'
    "{background:transparent !important;}"

    + _SIDEBAR_CSS

    + "</style>"
).replace(
    "__B64__",
    _BG_B64,
)


# =========================================================
# TOPBAR
# =========================================================

def render_topbar(page: str):
    title = PAGE_TITLES.get(page, "Workspace")

    topbar = (
        '<div class="j-topbar">'

        # Kiri: logo + breadcrumb
        '<div style="display:flex;align-items:center;gap:12px;">'
        f'<div class="j-logo">{LOGO_SVG}</div>'                      # BARU: logo
        '<div class="j-crumb">'
        '<span class="j-crumb-hide">'
        'Tim Pencegahan Fraud '
        '<span class="sep">›</span> '
        'JALA Core '
        '<span class="sep">›</span> '
        '</span>'
        f'<b>{title}</b>'
        '</div>'
        '</div>'

        # Kanan: kuartal + avatar
        '<div style="display:flex;align-items:center;gap:10px;">'
        f'<span class="j-chip">{ICON_CALENDAR_SVG}'                  # BARU: ikon kalender
        f'<span class="j-q-full">{QUARTER}</span>'
        f'<span class="j-q-short">{QUARTER_SHORT}</span>'
        '</span>'
        f'<span class="j-avatar" title="User">{ICON_USER_SVG}</span>'  # BARU: ikon user
        '</div>'

        '</div>'
    )

    st.markdown(
        BG_CSS + topbar,
        unsafe_allow_html=True,
    )


def render_demo_notice():
    """Persistent, plain-language scope notice for the synthetic demo."""
    st.markdown(
        '<div class="j-demo-notice" role="status" aria-label="Batas lingkungan demo">'
        '<b>Mode demo</b><span>Data sintetis</span><span>Tindakan tidak dikirim ke sistem BPJS</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_workflow_stepper(page: str):
    """Show the user's place in the review flow; Network is supporting evidence."""
    if page == "about":
        return
    steps = ["Ringkasan", "Prioritas", "Bukti", "Tindak lanjut"]
    active = {"dashboard": 0, "risk": 1, "claim": 2, "network": 2, "audit": 3}.get(page, 0)
    items = []
    for i, label in enumerate(steps):
        state = "active" if i == active else ("done" if i < active else "")
        current = ' aria-current="step"' if i == active else ""
        items.append(
            f'<li class="{state}"{current}><span class="j-step-number">{i + 1}</span>'
            f'<span>{label}</span></li>'
        )
    st.markdown(
        f'<nav class="j-workflow" aria-label="Tahap pemeriksaan"><ol>{"".join(items)}</ol></nav>',
        unsafe_allow_html=True,
    )


# =========================================================
# PAGE HEADER
# =========================================================

def page_header(
    eyebrow: str,
    eyebrow_tone: str,
    title: str,
    subtitle: str,
    right_html: str = "",
):
    pill = (
        f'<div style="margin-bottom:6px;"><span class="j-pill {eyebrow_tone}">{eyebrow}</span></div>'
        if eyebrow
        else ""
    )
    st.markdown(
        f"""
        <div
            class="j-pagehead"
            style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:16px;
            "
        >

            <div>

                {pill}

                <div class="j-h1">
                    {title}
                </div>

                <div
                    class="j-body"
                    style="max-width:860px;"
                >
                    {subtitle}
                </div>

            </div>

            <div
                class="j-pagehead-right"
                style="text-align:right;"
            >
                {right_html}
            </div>

        </div>

        <div style="height:18px"></div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

def render_footer():
    items = "".join(
        f'<span>'
        f'<span class="dot {tone}"></span>'
        f'{text}'
        f'</span>'
        for tone, text in FOOTER_STATUS
    )

    st.markdown(
        f"""
        <div class="j-footer">

            <div
                style="
                    display:flex;
                    gap:22px;
                    flex-wrap:wrap;
                "
            >
                {items}
            </div>

            <div>
                {FOOTER_CUTOFF}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# NAVIGATION
# =========================================================

def goto(page: str, cluster: str | None = None):
    st.session_state.page = page

    if cluster is not None:
        st.session_state.selected_cluster = cluster

    if page not in ("risk", "claim", "network", "audit"):
        st.session_state.selected_cluster = None

    st.rerun()
