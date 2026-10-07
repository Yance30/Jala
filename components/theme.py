"""
Design tokens + global CSS for the JALA Fraud Analytics dashboard.

Source of truth: DESIGN.md (Precision Graph & Forensic Intelligence).
"""

TOKENS = {
    "primary": "#0F766E",
    "primary_hover": "#0D6861",
    "core": "#132A1C",
    "amber": "#F97316",
    "amber_dark": "#C2410C",
    "red": "#DC2626",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "canvas": "#F8FAFC",
    "white": "#FFFFFF",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "container_2": "#F1F5F9",
}


# =========================================================
# LOGO
# =========================================================

LOGO_SVG = (
    '<svg viewBox="0 0 1024 1024" role="img" aria-label="JALA logo" '
    'style="width:100%;height:100%;display:block;">'
    '<rect width="1024" height="1024" rx="252" fill="#0F766E"/>'
    '<circle cx="512" cy="676" r="108" fill="#F97316"/>'
    '<path d="M340 382 L512 664 L684 382" fill="none" '
    'stroke="#F8FAFC" stroke-width="44"/>'
    '<rect x="424" y="360" width="46" height="44" fill="#F8FAFC"/>'
    '<rect x="512" y="360" width="46" height="44" fill="#F8FAFC"/>'
    '<circle cx="340" cy="382" r="84" fill="#F8FAFC"/>'
    '<circle cx="684" cy="382" r="84" fill="#F8FAFC"/>'
    "</svg>"
)


# =========================================================
# ICONS
# =========================================================

ICON_CALENDAR_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" style="width:15px;height:15px;flex:none;">'
    '<rect x="3" y="5" width="18" height="16" rx="2"/>'
    '<line x1="3" y1="10" x2="21" y2="10"/>'
    '<line x1="8" y1="3" x2="8" y2="7"/>'
    '<line x1="16" y1="3" x2="16" y2="7"/>'
    "</svg>"
)


ICON_USER_SVG = (
    '<svg viewBox="0 0 24 24" fill="currentColor" '
    'aria-hidden="true" style="width:18px;height:18px;flex:none;">'
    '<circle cx="12" cy="8" r="4"/>'
    '<path d="M4 21v-1c0-4.4 3.6-7 8-7s8 2.6 8 7v1z"/>'
    "</svg>"
)


# =========================================================
# GLOBAL CSS
# =========================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');


/* =========================================================
   BASE
   ========================================================= */

html,
body,
[class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont,
        'Segoe UI', sans-serif;
    color: #132A1C;
}

body {
    background: #F8FAFC;
}

#MainMenu,
footer {
    visibility: hidden;
}

[data-testid="stAppDeployButton"] {
    display: none !important;
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1560px;
}


/* =========================================================
   STREAMLIT HEADER
   ========================================================= */

[data-testid="stHeader"],
[data-testid="stHeader"] [data-testid="stToolbar"] {
    height: 2.25rem !important;
    min-height: 2.25rem !important;
    max-height: 2.25rem !important;
}

[data-testid="stHeader"] button {
    height: 2rem !important;
    min-height: 2rem !important;
}


/* =========================================================
   TABULAR NUMBERS
   ========================================================= */

.tnum,
[data-testid="stMetric"] {
    font-feature-settings: "tnum", "cv02", "cv03", "cv04";
}


/* =========================================================
   SIDEBAR  (latar gelap, tulisan menu putih)
   ========================================================= */

section[data-testid="stSidebar"] {
    width: 264px !important;
    min-width: 264px !important;
    background: linear-gradient(180deg, #0B3F3B 0%, #132A1C 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
}


section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding: 1.75rem 1.25rem 2.5rem;
}


/* jarak napas antar blok sidebar (brand, nav, peran, tombol, pencarian) */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > * {
    margin-bottom: 1rem;
}


/* tombol tutup sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
    color: #FFFFFF;
}


section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] svg,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
    color: #FFFFFF;
    fill: currentColor;
}


section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}


section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 13px 14px;
    border-radius: 8px;
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    color: #FFFFFF;
    cursor: pointer;
    transition: background 0.15s ease;
}


section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.10);
    color: #FFFFFF;
}


section[data-testid="stSidebar"] div[role="radiogroup"]
label:has(input:checked) {
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
    font-weight: 600;
    box-shadow: inset 3px 0 0 #5EEAD4;
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(> input) > div:first-child {
    display: none;
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(> span > input) > div > div:first-child {
    display: none;
}


section[data-testid="stSidebar"]
div[role="radiogroup"] label p {
    margin: 0;
    color: #FFFFFF;
    font: inherit;
}


section[data-testid="stSidebar"]
div[role="radiogroup"] label::before {
    font-family: 'Material Symbols Outlined';
    font-size: 18px;
    line-height: 1;
    width: 18px;
    height: 18px;
    flex: none;
    color: currentColor;

    font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
}


/* Ikon menu, urutan sesuai NAV_PAGES:
   0 Dashboard, 1 Network Graph, 2 Risk Ranking, 3 Audit Action, 4 About */

section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input[value="0"])::before {
    content: 'dashboard';
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input[value="1"])::before {
    content: 'hub';
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input[value="2"])::before {
    content: 'analytics';
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input[value="3"])::before {
    content: 'gavel';
}


section[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input[value="4"])::before {
    content: 'info';
}


/* elemen lain di dalam sidebar mengikuti latar gelap */

section[data-testid="stSidebar"] .j-pill {
    background: rgba(255, 255, 255, 0.14);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.18);
}


section[data-testid="stSidebar"] .j-sidecard {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.85);
}


section[data-testid="stSidebar"] .dot.teal {
    background: #5EEAD4;
}


/* =========================================================
   GENERIC INPUTS
   ========================================================= */

.stTextInput input,
.stSelectbox select,
div[data-baseweb="select"] > div {
    border: 1px solid #DCE6E4 !important;

    border-radius: 8px !important;

    background: #FFFFFF;

    min-height: 40px;

    font-size: 13px;

    transition:
        border-color .18s ease,
        box-shadow .18s ease;
}

.stTextInput input:hover,
div[data-baseweb="select"] > div:hover {
    border-color: #B9DED9 !important;
}

.stTextInput input:focus,
div[data-baseweb="select"]:focus-within > div {
    border-color: #0F766E !important;

    box-shadow:
        0 0 0 3px rgba(15, 118, 110, 0.10) !important;
}

.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible {
    outline: 3px solid #0F766E !important;
    outline-offset: 2px !important;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
    border: 1px solid #DCE6E4;

    background: #FFFFFF;

    color: #132A1C;

    border-radius: 8px;

    font-size: 13px;
    font-weight: 600;

    min-height: 40px;

    padding: 7px 14px;

    transition:
        background .18s ease,
        border-color .18s ease,
        box-shadow .18s ease,
        transform .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #F8FAFC;

    border-color: #B9DED9;

    box-shadow:
        0 5px 14px rgba(15, 118, 110, 0.07);

    transform: translateY(-1px);
}


/* Primary */

.stButton > button[kind="primary"],
.stButton > button.primary {
    background:
        linear-gradient(
            135deg,
            #0F766E 0%,
            #0D6861 100%
        );

    border-color: transparent;

    color: #FFFFFF;

    box-shadow:
        0 5px 14px rgba(15, 118, 110, 0.15);
}

.stButton > button[kind="primary"]:hover,
.stButton > button.primary:hover {
    background:
        linear-gradient(
            135deg,
            #0D6861 0%,
            #095C56 100%
        );

    box-shadow:
        0 7px 18px rgba(15, 118, 110, 0.20);
}


/* Orange */

.stButton > button.tertiary {
    background: #F97316;
    border-color: transparent;
    color: #FFFFFF;
}


/* Danger */

.stButton > button.danger {
    background: #DC2626;
    border-color: transparent;
    color: #FFFFFF;
}


/* Focus */

div.stButton > button:focus {
    box-shadow:
        0 0 0 2px #FFFFFF,
        0 0 0 4px rgba(15, 118, 110, .35);
}


/* =========================================================
   CHIPS
   ========================================================= */

div[data-testid="stHorizontalBlock"]
.stButton > button.chip {
    min-height: 30px;

    border-radius: 9999px;

    font-size: 12px;
    font-weight: 600;

    background: #FFFFFF;

    color: #475569;

    border: 1px solid #DCE6E4;

    padding: 4px 14px;
}

.stButton > button.chip-on {
    background: #0F766E !important;

    color: #FFFFFF !important;

    border-color: #0F766E !important;
}


/* =========================================================
   JALA BRAND
   ========================================================= */

.j-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.j-logo {
    width: 38px;
    height: 38px;

    border-radius: 10px;

    overflow: hidden;

    flex: none;

    display: flex;
    align-items: center;
    justify-content: center;

    box-shadow:
        0 4px 12px rgba(15, 118, 110, 0.12);
}

.j-logo svg {
    width: 100%;
    height: 100%;

    display: block;
}


/* =========================================================
   PILLS
   ========================================================= */

.j-pill {
    display: inline-block;

    background: #E2E8F0;

    color: #334155;

    border-radius: 9999px;

    font-size: 11px;
    font-weight: 600;

    letter-spacing: .04em;

    padding: 4px 10px;
}

.j-pill.teal {
    background: rgba(15,118,110,.08);

    color: #0F766E;

    border: 1px solid rgba(15,118,110,.20);
}

.j-pill.amber {
    background: rgba(249,115,22,.10);

    color: #C2410C;

    border: 1px solid rgba(249,115,22,.30);
}

.j-pill.red {
    background: #FEE2E2;
    color: #B91C1C;
}

.j-pill.red-solid {
    background: #DC2626;
    color: #FFFFFF;
}

.j-pill.green {
    background: #DCFCE7;
    color: #15803D;
}

.j-pill.grey {
    background: #E2E8F0;
    color: #475569;
}

.j-pill.brown {
    background: #9A3412;
    color: #FFFFFF;
}


/* =========================================================
   CARDS
   ========================================================= */

.j-card {
    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    border-radius: 12px;

    padding: 1.25rem;

    box-shadow:
        0 3px 12px rgba(15, 23, 42, 0.025);

    transition:
        transform .18s ease,
        box-shadow .18s ease,
        border-color .18s ease;
}

.j-card:hover {
    border-color: #D4E3E1;

    box-shadow:
        0 8px 24px rgba(15, 23, 42, 0.055);

    transform: translateY(-1px);
}

.j-card.tint {
    background: #F8FAFC;

    border-color: #CBD5E1;
}

.j-card.tealwash {
    background:
        linear-gradient(
            180deg,
            #E8F6F3 0%,
            #F7FCFB 100%
        );

    border-color: #B9DED9;

    box-shadow:
        0 8px 24px rgba(15, 118, 110, 0.055);
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

.j-metric-card {
    min-height: 145px;

    position: relative;

    overflow: hidden;
}

.j-metric-card::after {
    content: "";

    position: absolute;

    width: 120px;
    height: 120px;

    right: -42px;
    bottom: -50px;

    border-radius: 50%;

    background:
        rgba(15, 118, 110, 0.045);

    pointer-events: none;
}


/* =========================================================
   TYPOGRAPHY
   ========================================================= */

.j-label {
    font-size: 11px;

    font-weight: 600;

    letter-spacing: .05em;

    text-transform: uppercase;

    color: #64748B;
}

.j-value {
    font-size: 34px;

    font-weight: 700;

    color: #0F766E;

    letter-spacing: -0.025em;

    font-feature-settings:
        "tnum",
        "cv02",
        "cv03",
        "cv04";

    line-height: 1.15;
}

.j-value.dark {
    color: #132A1C;
}

.j-value.red {
    color: #DC2626;
}

.j-value.amber {
    color: #C2410C;
}

.j-sub {
    font-size: 12px;

    color: #64748B;
}

.j-note {
    background: #F8FAFC;

    border-radius: 8px;

    padding: 10px 12px;

    font-size: 12px;

    color: #475569;

    display: flex;

    gap: 8px;

    align-items: flex-start;
}

.j-h1 {
    font-size: 32px;

    font-weight: 700;

    letter-spacing: -0.025em;

    color: #132A1C;

    margin: 2px 0 7px 0;

    line-height: 1.15;
}

.j-h2 {
    font-size: 19px;

    font-weight: 650;

    letter-spacing: -0.018em;

    color: #132A1C;

    margin: 0 0 5px 0;
}

.j-body {
    font-size: 14px;

    color: #475569;

    line-height: 1.6;
}


/* =========================================================
   PAGE HEADER
   ========================================================= */

.j-pagehead {
    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    gap: 24px;

    padding: 2px 0 8px;
}

.j-pagehead-main {
    flex: 1;

    min-width: 0;
}

.j-pagehead-right {
    flex: none;
}


/* =========================================================
   BREADCRUMB
   ========================================================= */

.j-crumb {
    font-size: 13px;

    color: #64748B;
}

.j-crumb b {
    color: #132A1C;

    font-weight: 600;
}

.j-crumb .sep {
    margin: 0 6px;

    color: #CBD5E1;
}


/* =========================================================
   TOPBAR
   ========================================================= */

.j-topbar {
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 14px;

    padding: 7px 0 12px 0;

    border-bottom: 1px solid #E2E8F0;

    margin-bottom: 18px;
}

.j-chip {
    display: inline-flex;

    align-items: center;

    gap: 8px;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    border-radius: 8px;

    padding: 7px 11px;

    font-size: 13px;

    font-weight: 500;

    color: #132A1C;

    box-shadow:
        0 2px 8px rgba(15, 23, 42, 0.025);
}

.j-chip svg {
    color: #475569;
}


/* =========================================================
   AVATAR
   ========================================================= */

.j-avatar {
    width: 34px;
    height: 34px;

    border-radius: 9999px;

    background: #0F766E;

    color: #FFFFFF;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    flex: none;

    box-shadow:
        0 4px 10px rgba(15, 118, 110, 0.15);
}

.j-avatar svg {
    width: 16px;
    height: 16px;
}


/* =========================================================
   TABLE
   ========================================================= */

.j-table {
    width: 100%;

    border-collapse: separate;

    border-spacing: 0;

    font-size: 13px;

    overflow: hidden;

    border: 1px solid #E2E8F0;

    border-radius: 10px;
}

.j-table th {
    text-align: left;

    font-size: 11px;

    font-weight: 600;

    letter-spacing: .04em;

    text-transform: uppercase;

    color: #64748B;

    padding: 11px 12px;

    background:
        linear-gradient(
            180deg,
            #F8FAFC 0%,
            #F4F7F9 100%
        );

    border-bottom: 1px solid #E2E8F0;
}

.j-table td {
    padding: 11px 12px;

    border-bottom: 1px solid #F1F5F9;

    vertical-align: top;

    color: #334155;

    font-feature-settings:
        "tnum",
        "cv02",
        "cv03",
        "cv04";
}

.j-table tr:last-child td {
    border-bottom: none;
}

.j-table tr:hover td {
    background:
        linear-gradient(
            90deg,
            #F8FCFB,
            #FFFFFF
        );
}

.j-table td.num {
    text-align: right;
}

/* Tables inside comparison cards keep the same spacing and can scroll on phones. */
.j-inline-table-wrap {
    width: 100%;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    margin-top: 10px;
}

.j-inline-table {
    width: 100%;
    min-width: 520px;
    border-collapse: collapse;
    font-size: 13px;
}

.j-inline-table th,
.j-inline-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #E2E8F0;
    text-align: right;
    vertical-align: top;
    line-height: 1.45;
}

.j-inline-table th:first-child,
.j-inline-table td:first-child {
    text-align: left;
}

.j-inline-table th {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
    background: #F8FAFC;
}

.j-inline-table tr:last-child td {
    border-bottom: 0;
}


/* =========================================================
   BARS
   ========================================================= */

.j-bar {
    height: 7px;

    border-radius: 9999px;

    background: #E2E8F0;

    overflow: hidden;
}

.j-bar > span {
    display: block;

    height: 100%;

    border-radius: 9999px;
}


/* =========================================================
   KEY VALUE
   ========================================================= */

.j-kv {
    display: flex;

    flex-direction: column;

    gap: 2px;
}

.j-kv .k {
    font-size: 12px;

    color: #64748B;
}

.j-kv .v {
    font-size: 14px;

    font-weight: 600;

    color: #132A1C;
}


/* =========================================================
   CODE
   ========================================================= */

.j-code {
    background: #F1F5F9;

    border-radius: 8px;

    padding: 10px 12px;

    font-family:
        'JetBrains Mono',
        ui-monospace,
        monospace;

    font-size: 12px;

    color: #334155;

    white-space: pre-wrap;

    border: 1px solid #E2E8F0;
}


/* =========================================================
   ALERT
   ========================================================= */

.j-alert-red {
    background:
        linear-gradient(
            135deg,
            #FEF2F2,
            #FFF8F8
        );

    border: 1px solid #FECACA;

    border-radius: 10px;

    padding: 12px 16px;

    color: #991B1B;

    font-size: 13px;
}

.j-alert-teal {
    background:
        linear-gradient(
            135deg,
            #E6F4F2,
            #F5FBFA
        );

    border: 1px solid #B9DED9;

    border-radius: 10px;

    padding: 12px 16px;

    color: #0F5B54;

    font-size: 13px;
}


/* =========================================================
   ROW SEPARATOR
   ========================================================= */

.j-rowsep {
    border: 0;

    border-top: 1px solid #F1F5F9;

    margin: 16px 0;
}


/* =========================================================
   WHY BOX
   ========================================================= */

.j-why {
    background: #F8FAFC;

    border: 1px solid #E8EDF2;

    border-radius: 8px;

    padding: 10px 12px;

    font-size: 12px;

    color: #475569;

    line-height: 1.5;
}


/* =========================================================
   ICON BOX
   ========================================================= */

.j-iconbox {
    width: 36px;
    height: 36px;

    border-radius: 9px;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    font-size: 15px;
}

.j-iconbox.teal {
    background: #D7EDEA;

    color: #0F766E;
}

.j-iconbox.amber {
    background: #FFEDD5;

    color: #C2410C;
}

.j-iconbox.red {
    background: #FEE2E2;

    color: #B91C1C;
}

.j-iconbox.green {
    background: #DCFCE7;

    color: #15803D;
}

.j-iconbox.grey {
    background: #E2E8F0;

    color: #475569;
}


/* =========================================================
   FOOTER
   ========================================================= */

.j-footer {
    display: flex;

    gap: 18px;

    align-items: center;

    justify-content: space-between;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    border-radius: 10px;

    padding: 11px 16px;

    font-size: 12px;

    color: #475569;

    margin-top: 20px;

    box-shadow:
        0 3px 12px rgba(15, 23, 42, 0.025);
}


/* =========================================================
   SIDE CARD
   ========================================================= */

.j-sidecard {
    background: #F8FAFC;

    border: 1px solid #E2E8F0;

    border-radius: 10px;

    padding: 12px;

    font-size: 12px;

    color: #475569;
}


/* =========================================================
   STATUS DOT
   ========================================================= */

.dot {
    display: inline-block;

    width: 8px;
    height: 8px;

    border-radius: 9999px;

    margin-right: 6px;
}

.dot.teal {
    background: #0F766E;
}

.dot.amber {
    background: #F97316;
}

.dot.red {
    background: #DC2626;
}

.dot.green {
    background: #16A34A;
}


/* =========================================================
   NETWORK GRAPH
   ========================================================= */

.network-canvas {
    background:
        radial-gradient(
            circle at center,
            rgba(230,244,242,.80),
            rgba(248,250,252,.95) 72%
        );

    border: 1px solid #D7EDEA;

    border-radius: 14px;

    padding: 8px;

    box-shadow:
        inset 0 0 40px rgba(15,118,110,.025);
}


/* =========================================================
   COMPARISON
   ========================================================= */

.comparison-panel {
    min-height: 500px;

    position: relative;

    overflow: hidden;
}

.comparison-panel.legacy {
    border-top: 4px solid #94A3B8;
}

.comparison-panel.han {
    border-top: 4px solid #0F766E;

    box-shadow:
        0 10px 28px rgba(15,118,110,.07);
}


/* =========================================================
   CLAIM PROFILE
   ========================================================= */

.claim-profile-card {
    position: relative;

    overflow: hidden;
}

.claim-profile-card::before {
    content: "";

    position: absolute;

    left: 0;
    top: 0;
    bottom: 0;

    width: 4px;

    background: #0F766E;
}


/* =========================================================
   AUDIT RISK
   ========================================================= */

.audit-risk-card {
    border-left: 4px solid #DC2626 !important;

    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #FFF8F5
        );

    box-shadow:
        0 8px 24px rgba(220,38,38,.055);
}


/* =========================================================
   AUDIT SCORE
   ========================================================= */

.audit-score {
    display: flex;

    align-items: center;

    justify-content: center;

    width: 96px;
    height: 96px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            #FFFFFF 58%,
            #FEE2E2 59%,
            #FEE2E2 100%
        );

    border: 6px solid #FECACA;

    color: #DC2626;

    font-size: 24px;

    font-weight: 700;
}


/* =========================================================
   TOPBAR RESPONSIVE
   ========================================================= */

.j-demo-notice {
    display: flex;
    align-items: center;
    gap: 8px 14px;
    flex-wrap: wrap;
    margin: 8px 0 10px;
    padding: 9px 12px;
    border: 1px solid #B9DED9;
    border-radius: 9px;
    background: #F0FDFA;
    color: #334155;
    font-size: 12px;
}

.j-demo-notice b { color: #0F766E; }

.j-workflow { margin: 0 0 18px; }
.j-workflow ol {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    list-style: none;
    margin: 0;
    padding: 0;
}
.j-workflow li {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    padding: 8px 10px;
    border-bottom: 2px solid #E2E8F0;
    color: #64748B;
    font-size: 12px;
}
.j-workflow li.done { color: #0F766E; border-color: #99D5CE; }
.j-workflow li.active { color: #132A1C; border-color: #0F766E; font-weight: 700; }
.j-step-number {
    display: inline-flex;
    flex: 0 0 22px;
    width: 22px;
    height: 22px;
    align-items: center;
    justify-content: center;
    border: 1px solid currentColor;
    border-radius: 50%;
    font-size: 11px;
}

@media (max-width: 560px) {
    .j-workflow ol { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .j-workflow li { padding: 7px 4px; }
}

.j-q-short {
    display: none;
}

@media (max-width: 640px) {

    .j-q-full {
        display: none;
    }

    .j-q-short {
        display: inline;
    }

    .j-crumb-hide {
        display: none;
    }
}


/* =========================================================
   MATERIAL SYMBOLS
   ========================================================= */

.ms {
    font-family: 'Material Symbols Outlined';

    font-weight: normal;

    font-style: normal;

    font-size: 18px;

    line-height: 1;

    vertical-align: middle;

    display: inline-block;

    letter-spacing: normal;

    white-space: nowrap;

    -webkit-font-smoothing: antialiased;

    font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
}


/* =========================================================
   RESPONSIVE PAGE
   ========================================================= */

.j-dashboard-title {
    color: #0F766E;
    font-size: 34px;
    line-height: 1.15;
    letter-spacing: -.025em;
}

.j-demo-case {
    border-left: 4px solid #F97316;
    background: linear-gradient(120deg, #FFF7ED 0%, #FFFFFF 58%);
    margin: 8px 0 10px;
}

.j-demo-caution {
    border-left-color: #0F766E;
    background: linear-gradient(120deg, #F0FDFA 0%, #FFFFFF 58%);
}

.j-review-status,
.j-review-next {
    min-height: 92px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.j-demo-case .j-h2 {
    margin: 10px 0 4px;
}

.j-demo-evidence {
    margin-top: 9px;
    padding: 9px 11px;
    border-radius: 8px;
    background: rgba(255, 255, 255, .8);
    color: #475569;
    font-size: 13px;
    line-height: 1.5;
}

.j-detail-profile {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

@media (max-width: 900px) {

    .j-pagehead {
        flex-direction: column;
    }

    .j-pagehead-right {
        width: 100%;
    }

    .j-h1 {
        font-size: 27px;
    }

    .j-metric-card {
        min-height: 130px;
    }
}

@media (max-width: 640px) {

    .j-dashboard-title {
        font-size: 27px;
    }

    .j-demo-case {
        padding: 14px;
    }

    .j-detail-profile {
        grid-template-columns: 1fr;
    }

    .st-key-dashboard_start_review button {
        min-height: 48px;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .j-footer {
        flex-direction: column;

        align-items: flex-start;
    }

    .j-card {
        padding: 1rem;
    }

    .j-value {
        font-size: 30px;
    }
}


/* =========================================================
   TABEL: SCROLL HORIZONTAL (desktop & mobile)
   ========================================================= */

.j-table-wrap {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior-x: contain;
}


.j-table-wrap::-webkit-scrollbar {
    height: 8px;
}


.j-table-wrap::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 9999px;
}


.j-table-wrap::-webkit-scrollbar-track {
    background: #F1F5F9;
    border-radius: 9999px;
}


/* cegah kolom Streamlit melebar mengikuti isi tabel */
[data-testid="stElementContainer"]:has(.j-table-wrap),
[data-testid="stMarkdownContainer"]:has(.j-table-wrap),
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .j-table-wrap) {
    min-width: 0;
    max-width: 100%;
}


.j-table {
    min-width: 640px;
}


.j-table-risk {
    min-width: 900px;
}


.j-table-triage {
    min-width: 980px;
}


.j-table-faskes {
    min-width: 720px;
}


.j-table th,
.j-table td.num {
    white-space: nowrap;
}


.j-table-risk td:first-child {
    min-width: 300px;
}


.j-table-risk td:last-child {
    min-width: 260px;
}


.j-scrollhint {
    display: none;
    font-size: 11px;
    color: #64748B;
    text-align: right;
    margin: 0 2px 6px 0;
}


@media (max-width: 900px) {
    .j-scrollhint {
        display: block;
    }
}


@media (max-width: 640px) {
    .j-table th,
    .j-table td {
        padding: 8px 10px;
    }
}


/* =========================================================
   AUDIT ACTION: kartu seragam
   ========================================================= */

.j-grid4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    align-items: stretch;
}


.j-grid4 > .j-card {
    margin: 0;
    height: 100%;
    box-sizing: border-box;
    overflow-wrap: anywhere;
}

/* Kartu simulasi tampil di kolom Streamlit yang lebih sempit. */
.j-whatif-card {
    padding: 1rem;
    min-height: 220px;
}

.j-whatif-card .j-value {
    font-size: 28px;
    white-space: nowrap;
    overflow-wrap: normal;
    word-break: keep-all;
}

.j-whatif-card .j-note {
    line-height: 1.5;
    overflow-wrap: anywhere;
}


@media (max-width: 1100px) {
    .j-grid4 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}


@media (max-width: 520px) {
    .j-grid4 {
        grid-template-columns: 1fr;
    }
}


.j-actcard {
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    min-height: 250px;
}


.j-actcard-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}


.j-actcard-title {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.35;
    color: #132A1C;
    margin: 14px 0 6px 0;
}


.j-actcard-body {
    font-size: 12.5px;
    line-height: 1.6;
    color: #475569;
}


.j-actcard-note {
    font-size: 12px;
    line-height: 1.4;
    color: #64748B;
    text-align: center;
    margin-top: 8px;
    min-height: 2.8em;
}


/* tinggi tombol tindakan sama, teks panjang boleh turun baris */
.st-key-audit_actions button {
    min-height: 46px;
    height: auto;
    white-space: normal;
    line-height: 1.25;
}


@media (max-width: 900px) {
    .j-actcard {
        min-height: 0;
    }

    .j-actcard-note {
        min-height: 0;
    }
}

@media (max-width: 900px) {
    .st-key-audit_actions [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 12px;
    }

    .st-key-audit_actions [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 calc(50% - 12px);
        min-width: min(100%, 260px);
    }
}

@media (max-width: 560px) {
    .st-key-audit_actions [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex-basis: 100%;
    }
}


/* =========================================================
   PERBANDINGAN PARADIGMA (halaman About): judul & panel rapi
   ========================================================= */

.j-cmp-title {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.015em;
    line-height: 1.3;
    color: #132A1C;
    margin: 16px 0 8px 0;
    min-height: 2.6em;
    text-wrap: balance;
}


.j-cmp-sub {
    min-height: 3.2em;
}


.j-cmp-diagram {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
}


.j-cmp-diagram > div {
    padding: 0 !important;
}


.j-cmp-diagram svg {
    max-width: 100%;
    height: auto;
}


.j-cmp-note {
    text-align: center;
    line-height: 1.5;
    min-height: 3em;
}


.j-cmp-points {
    min-height: 190px;
}


/* kartu memenuhi tinggi kolom, footer menempel di dasar */
.j-cmp-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}


.j-cmp-foot {
    margin-top: auto;
}


[data-testid="stColumn"]:has(.j-cmp-card) [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.j-cmp-card) [data-testid="stElementContainer"],
[data-testid="stColumn"]:has(.j-cmp-card) [data-testid="stMarkdown"],
[data-testid="stColumn"]:has(.j-cmp-card) [data-testid="stMarkdownContainer"] {
    height: 100%;
}


@media (max-width: 900px) {
    .j-cmp-title,
    .j-cmp-sub,
    .j-cmp-diagram,
    .j-cmp-note,
    .j-cmp-points {
        min-height: 0;
    }
}


/* =========================================================
   HALAMAN ABOUT: jarak antar section
   ========================================================= */

.j-anchor {
    scroll-margin-top: 72px;
}


.j-section-gap {
    height: 40px;
}


/* =========================================================
   KESEJAJARAN KARTU
   - Kolom dalam satu baris setinggi baris itu, kartu mengisi penuh.
   - Kartu judul grafik + grafiknya menyatu menjadi satu kotak,
     dan judul menyerap selisih tinggi agar grafik sejajar.
   ========================================================= */

div[data-testid="stHorizontalBlock"] {
    align-items: stretch;
}

/* kolom yang isinya hanya satu kartu */
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) > [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) > [data-testid="stVerticalBlock"] > *,
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) [data-testid="stMarkdown"],
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) [data-testid="stMarkdown"] > div,
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) [data-testid="stMarkdownContainer"] {
    height: 100%;
}

[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) .j-card {
    height: 100%;
    box-sizing: border-box;
}

/* judul grafik yang menyatu dengan grafiknya */
.j-card.j-eqhead {
    margin: 0 !important;
    border-bottom: 0;
    border-radius: 12px 12px 0 0;
    box-sizing: border-box;
    transform: none !important;
    min-height: 94px;
}

[data-testid="stElementContainer"]:has(.j-eqhead),
[data-testid="stMarkdownContainer"]:has(.j-eqhead) {
    margin-bottom: 0 !important;
}

/* Collapse spacing only inside explicitly keyed chart panels. */
[class*="st-key-chart_panel_"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Dashboard summary items need breathing room below the chart. */
.j-dashboard-summary-item {
    min-height: 64px;
    box-sizing: border-box;
    padding: 8px 10px;
    border-radius: 10px;
}

[data-testid="stElementContainer"]:has(.j-eqhead) + [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]),
[data-testid="stColumn"]:has(.j-eqhead) [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 0;
    border-radius: 0 0 12px 12px;
    padding: 0 10px 10px;
    box-sizing: border-box;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.025);
}

/* di layar sempit kolom bertumpuk: tidak perlu menyamakan tinggi */
@media (max-width: 640px) {
    [data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > :only-child .j-card) .j-card,
    .j-card.j-eqhead {
        height: auto;
        min-height: 0;
    }
}

/* Risk Ranking KPI: reserve equal card height and anchor note text at the bottom. */
.j-risk-kpi-card {
    height: 136px;
    min-height: 136px;
    box-sizing: border-box;
}

.j-risk-kpi-card > div {
    height: 100%;
}

.j-risk-kpi-card > div > div:first-child {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-width: 0;
}

.j-risk-kpi-card .j-sub {
    margin-top: auto !important;
    padding-top: 3px;
}
"""


# =========================================================
# THEME FUNCTIONS
# =========================================================

def inject_theme():
    import streamlit as st

    st.markdown(
        f"<style>{CSS}</style>",
        unsafe_allow_html=True,
    )


def patch_markdown():
    """
    Strip whitespace-only lines from raw-HTML markdown payloads.

    Streamlit renders unsafe HTML through markdown-it:
    a blank line terminates an HTML block and the following
    indented lines would be emitted as a code block.
    """

    import streamlit as st

    if getattr(st.markdown, "_jala_patched", False):
        return

    original = st.markdown

    def _markdown(body, *args, **kwargs):
        if isinstance(body, str) and kwargs.get("unsafe_allow_html"):
            body = "\n".join(
                line
                for line in body.split("\n")
                if line.strip()
            )

        return original(body, *args, **kwargs)

    _markdown._jala_patched = True

    st.markdown = _markdown
