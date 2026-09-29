"""Design tokens + global CSS for the JALA Fraud Analytics dashboard.

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

# Vectorized rendition of assets/logo.png (teal squircle, linked white nodes,
# orange convergence node) so the mark stays crisp at 34-38px.
LOGO_SVG = (
    '<svg viewBox="0 0 1024 1024" role="img" aria-label="JALA logo" '
    'style="width:100%;height:100%;display:block;">'
    '<rect width="1024" height="1024" rx="252" fill="#0F766E"/>'
    '<circle cx="512" cy="676" r="108" fill="#F97316"/>'
    '<path d="M340 382 L512 664 L684 382" fill="none" stroke="#F8FAFC" stroke-width="44"/>'
    '<rect x="424" y="360" width="46" height="44" fill="#F8FAFC"/>'
    '<rect x="512" y="360" width="46" height="44" fill="#F8FAFC"/>'
    '<circle cx="340" cy="382" r="84" fill="#F8FAFC"/>'
    '<circle cx="684" cy="382" r="84" fill="#F8FAFC"/>'
    "</svg>"
)

ICON_CALENDAR_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'style="width:15px;height:15px;flex:none;">'
    '<rect x="3" y="5" width="18" height="16" rx="2"/>'
    '<line x1="3" y1="10" x2="21" y2="10"/>'
    '<line x1="8" y1="3" x2="8" y2="7"/>'
    '<line x1="16" y1="3" x2="16" y2="7"/>'
    "</svg>"
)

ICON_USER_SVG = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" '
    'style="width:18px;height:18px;flex:none;">'
    '<circle cx="12" cy="8" r="4"/>'
    '<path d="M4 21v-1c0-4.4 3.6-7 8-7s8 2.6 8 7v1z"/>'
    "</svg>"
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #132A1C;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stAppDeployButton"] { display: none !important; }
.block-container { padding-top: 2.75rem; padding-bottom: 2rem; max-width: 1560px; }

/* keep the fixed Streamlit/Cloud toolbar band compact so it never covers the JALA topbar */
[data-testid="stHeader"], [data-testid="stHeader"] [data-testid="stToolbar"] {
    height: 2.25rem !important; min-height: 2.25rem !important; max-height: 2.25rem !important;
}
[data-testid="stHeader"] button { height: 2rem !important; min-height: 2rem !important; }

/* tabular numbers for all metrics / tables */
.tnum, [data-testid="stMetric"] { font-feature-settings: "tnum", "cv02", "cv03", "cv04"; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { width: 264px !important; min-width: 264px !important; background: #F8FAFC; border-right: 1px solid #E2E8F0; }
section[data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem; }

/* radio rendered as the Stitch nav rail (Material Symbols glyphs via ligatures).
   Selectors avoid child combinators on the option list: Streamlit <=1.57 puts labels
   directly in the radiogroup, newer builds wrap each label in a div (react-aria). */
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 12px; border-radius: 8px; margin: 0;
    font-size: 14px; font-weight: 500; color: #334155; cursor: pointer;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: #ECEFF2; color: #132A1C; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #0F766E; color: #FFFFFF; font-weight: 600;
    box-shadow: 0 1px 2px rgba(19, 42, 28, 0.12);
}
/* hide the native radio circle: direct-input layout (<=1.57) vs sr-only span layout (newer) */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(> input) > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(> span > input) > div > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] label p { margin: 0; color: inherit; font: inherit; }
section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    font-family: 'Material Symbols Outlined'; font-size: 18px; line-height: 1;
    width: 18px; height: 18px; flex: none; color: currentColor;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="0"])::before { content: 'dashboard'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="1"])::before { content: 'account_tree'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="2"])::before { content: 'hub'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="3"])::before { content: 'analytics'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="4"])::before { content: 'compare_arrows'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="5"])::before { content: 'gavel'; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="6"])::before { content: 'shield'; }

/* ---------- generic widgets ---------- */
.stTextInput input, .stSelectbox select, div[data-baseweb="select"] > div {
    border: 1px solid #E2E8F0 !important; border-radius: 4px !important;
    background: #FFFFFF; min-height: 36px; font-size: 13px;
}
.stTextInput input:focus, div[data-baseweb="select"]:focus-within > div {
    border-color: #0F766E !important; box-shadow: 0 0 0 1px #0F766E !important;
}
.stButton > button, .stDownloadButton > button {
    border: 1px solid #E2E8F0; background: #FFFFFF; color: #132A1C;
    border-radius: 4px; font-size: 13px; font-weight: 500; min-height: 36px;
    padding: 6px 12px;
}
.stButton > button:hover, .stDownloadButton > button:hover { background: #F8FAFC; border-color: #CBD5E1; }
.stButton > button[kind="primary"], .stButton > button.primary {
    background: #0F766E; border-color: transparent; color: #FFFFFF;
}
.stButton > button.primary:hover { background: #0D6861; }
.stButton > button.tertiary { background: #F97316; border-color: transparent; color: #FFFFFF; }
.stButton > button.danger { background: #DC2626; border-color: transparent; color: #FFFFFF; }
div.stButton > button:focus { box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px #0F766E; }

/* chips (filter pills) */
div[data-testid="stHorizontalBlock"] .stButton > button.chip {
    min-height: 30px; border-radius: 9999px; font-size: 12px; font-weight: 600;
    background: #FFFFFF; color: #475569; border: 1px solid #E2E8F0; padding: 4px 14px;
}
.stButton > button.chip-on { background: #0F766E !important; color: #FFFFFF !important; border-color: #0F766E !important; }

/* ---------- JALA building blocks ---------- */
.j-brand { display: flex; align-items: center; gap: 10px; }
.j-logo { width: 38px; height: 38px; border-radius: 8px; overflow: hidden; flex: none;
          display: flex; align-items: center; justify-content: center; }
.j-logo svg { width: 100%; height: 100%; display: block; }
.j-pill { display: inline-block; background: #E2E8F0; color: #334155; border-radius: 9999px;
          font-size: 11px; font-weight: 600; letter-spacing: .04em; padding: 3px 10px; }
.j-pill.teal { background: rgba(15,118,110,.08); color: #0F766E; border: 1px solid rgba(15,118,110,.2); }
.j-pill.amber { background: rgba(249,115,22,.1); color: #C2410C; border: 1px solid rgba(249,115,22,.3); }
.j-pill.red { background: #FEE2E2; color: #B91C1C; }
.j-pill.red-solid { background: #DC2626; color: #fff; }
.j-pill.green { background: #DCFCE7; color: #15803D; }
.j-pill.grey { background: #E2E8F0; color: #475569; }
.j-pill.brown { background: #9A3412; color: #fff; }

.j-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; }
.j-card.tint { background: #F8FAFC; border-color: #CBD5E1; }
.j-card.tealwash { background: linear-gradient(180deg, #E6F4F2 0%, #F2FAF8 100%); border-color: #B9DED9; }
.j-label { font-size: 11px; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; color: #64748B; }
.j-value { font-size: 34px; font-weight: 700; color: #0F766E; letter-spacing: -0.02em;
           font-feature-settings: "tnum", "cv02", "cv03", "cv04"; line-height: 1.15; }
.j-value.dark { color: #132A1C; }
.j-value.red { color: #DC2626; }
.j-value.amber { color: #C2410C; }
.j-sub { font-size: 12px; color: #64748B; }
.j-note { background: #F8FAFC; border-radius: 6px; padding: 10px 12px; font-size: 12px; color: #475569;
          display: flex; gap: 8px; align-items: flex-start; }
.j-h1 { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; color: #132A1C; margin: 2px 0 6px 0; }
.j-h2 { font-size: 18px; font-weight: 600; letter-spacing: -0.015em; color: #132A1C; margin: 0 0 4px 0; }
.j-body { font-size: 14px; color: #475569; line-height: 1.55; }
.j-crumb { font-size: 13px; color: #64748B; }
.j-crumb b { color: #132A1C; font-weight: 600; }
.j-crumb .sep { margin: 0 6px; color: #CBD5E1; }

.j-topbar { display: flex; align-items: center; justify-content: space-between; gap: 12px;
            padding: 6px 0 10px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px; }
.j-chip { display: inline-flex; align-items: center; gap: 8px; background: #EEF1F4; border-radius: 6px;
          padding: 6px 10px; font-size: 13px; font-weight: 500; color: #132A1C; }
.j-chip svg { color: #475569; }
.j-avatar { width: 32px; height: 32px; border-radius: 9999px; background: #0F766E; color: #fff;
            display: inline-flex; align-items: center; justify-content: center; flex: none; }
.j-avatar svg { width: 16px; height: 16px; }

.j-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.j-table th { text-align: left; font-size: 11px; font-weight: 600; letter-spacing: .04em; text-transform: uppercase;
              color: #64748B; padding: 10px 12px; background: #F8FAFC; border-bottom: 1px solid #E2E8F0; }
.j-table td { padding: 10px 12px; border-bottom: 1px solid #F1F5F9; vertical-align: top; color: #334155;
              font-feature-settings: "tnum", "cv02", "cv03", "cv04"; }
.j-table tr:hover td { background: #F8FAFC; }
.j-table td.num { text-align: right; }

.j-bar { height: 6px; border-radius: 9999px; background: #E2E8F0; overflow: hidden; }
.j-bar > span { display: block; height: 100%; border-radius: 9999px; }

.j-kv { display: flex; flex-direction: column; gap: 2px; }
.j-kv .k { font-size: 12px; color: #64748B; }
.j-kv .v { font-size: 14px; font-weight: 600; color: #132A1C; }

.j-code { background: #F1F5F9; border-radius: 6px; padding: 10px 12px; font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-size: 12px; color: #334155; white-space: pre-wrap; }
.j-alert-red { background: #FEE2E2; border-radius: 8px; padding: 12px 16px; color: #991B1B; font-size: 13px; }
.j-alert-teal { background: #E6F4F2; border-radius: 8px; padding: 12px 16px; color: #0F5B54; font-size: 13px; }
.j-rowsep { border: 0; border-top: 1px solid #F1F5F9; margin: 14px 0; }
.j-why { background: #F8FAFC; border-radius: 6px; padding: 10px 12px; font-size: 12px; color: #475569; line-height: 1.5; }
.j-iconbox { width: 34px; height: 34px; border-radius: 6px; display: inline-flex; align-items: center;
             justify-content: center; font-size: 15px; }
.j-iconbox.teal { background: #D7EDEA; color: #0F766E; }
.j-iconbox.amber { background: #FFEDD5; color: #C2410C; }
.j-iconbox.red { background: #FEE2E2; color: #B91C1C; }
.j-iconbox.green { background: #DCFCE7; color: #15803D; }
.j-iconbox.grey { background: #E2E8F0; color: #475569; }

.j-footer { display: flex; gap: 18px; align-items: center; justify-content: space-between;
            background: #EEF1F4; border-radius: 8px; padding: 10px 16px; font-size: 12px; color: #475569; margin-top: 18px; }
.j-sidecard { background: #EEF1F4; border-radius: 8px; padding: 12px; font-size: 12px; color: #475569; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 9999px; margin-right: 6px; }
.dot.teal { background: #0F766E; } .dot.amber { background: #F97316; } .dot.red { background: #DC2626; }
.dot.green { background: #16A34A; }
"""


def inject_theme():
    import streamlit as st
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def patch_markdown():
    """Strip whitespace-only lines from raw-HTML markdown payloads.

    Streamlit renders unsafe HTML through markdown-it: a blank line terminates an
    HTML block and the following indented lines would be emitted as a code block.
    """
    import streamlit as st

    if getattr(st.markdown, "_jala_patched", False):
        return
    original = st.markdown

    def _markdown(body, *args, **kwargs):
        if isinstance(body, str) and kwargs.get("unsafe_allow_html"):
            body = "\n".join(line for line in body.split("\n") if line.strip())
        return original(body, *args, **kwargs)

    _markdown._jala_patched = True
    st.markdown = _markdown
