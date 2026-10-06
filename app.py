import streamlit as st
from pathlib import Path

from components import intro, layout, sidebar, theme, tutorial
from views import about, audit_action, claim_details, dashboard, network_graph, risk_ranking

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo.png"

st.set_page_config(
    page_title="JALA Fraud Analytics",
    page_icon=str(LOGO_PATH),
    layout="wide"
)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "zoom" not in st.session_state:
    st.session_state.zoom = 1.0

ROUTES = {
    "dashboard": dashboard.render,
    "network": network_graph.render,
    "risk": risk_ranking.render,
    "claim": claim_details.render,
    "audit": audit_action.render,
    "about": about.render,
}

# Comparison sekarang menjadi section di halaman About
ALIASES = {"comparison": "about"}

requested = st.query_params.get("page")
requested = ALIASES.get(requested, requested)

if requested in ROUTES and requested != st.session_state.get("qp_seen"):
    st.session_state.page = requested
    st.session_state.qp_seen = requested

theme.patch_markdown()
theme.inject_theme()

# Animasi pembuka: tampil sekali per sesi,
# lalu otomatis lanjut ke halaman tujuan (default: dashboard)
if not st.session_state.intro_done:
    intro.render()
    st.stop()

sidebar.render_sidebar()
layout.render_topbar(st.session_state.page)
layout.render_demo_notice()
layout.render_workflow_stepper(st.session_state.page)

ROUTES[st.session_state.page]()

# Tutorial: terbuka otomatis sekali per sesi (matikan dengan ?tour=0); dibuka lagi lewat tombol di sidebar
tutorial.maybe_auto_show()
