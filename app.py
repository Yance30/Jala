import streamlit as st
from pathlib import Path

from components import layout, sidebar, theme
from views import about, audit_action, claim_details, comparison, dashboard, network_graph, pipeline, risk_ranking

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo.png"

st.set_page_config(page_title="JALA Fraud Analytics", page_icon=str(LOGO_PATH), layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "zoom" not in st.session_state:
    st.session_state.zoom = 1.0

ROUTES = {
    "dashboard": dashboard.render,
    "pipeline": pipeline.render,
    "network": network_graph.render,
    "risk": risk_ranking.render,
    "claim": claim_details.render,
    "comparison": comparison.render,
    "audit": audit_action.render,
    "about": about.render,
}

requested = st.query_params.get("page")
if requested in ROUTES and requested != st.session_state.get("qp_seen"):
    st.session_state.page = requested
    st.session_state.qp_seen = requested

theme.patch_markdown()
theme.inject_theme()
sidebar.render_sidebar()
layout.render_topbar(st.session_state.page)

ROUTES[st.session_state.page]()
