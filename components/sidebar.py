import streamlit as st

from components.theme import LOGO_SVG
from data.mock_data import NAV_PAGES


def render_sidebar():
    """Brand header, nav radio (styled as the Stitch nav rail) and verifikator card."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="j-brand">
              <div class="j-logo">{LOGO_SVG}</div>
              <div>
                <div style="font-size:16px;font-weight:600;letter-spacing:-0.01em;line-height:1.2;color:#0F766E;">JALA</div>
                <div style="font-size:11px;font-weight:500;color:#64748B;">Fraud Analytics</div>
              </div>
            </div>
            <div style="margin:12px 0 3.25rem 0;"><span class="j-pill">Prototype / Proof of Concept</span></div>
            """,
            unsafe_allow_html=True,
        )

        labels = [label for _, label in NAV_PAGES]
        keys = [key for key, _ in NAV_PAGES]
        current = st.session_state.get("page", "dashboard")
        mapped = "risk" if current == "claim" else current
        index = keys.index(mapped) if mapped in keys else 0

        def _on_nav():
            st.session_state.page = keys[labels.index(st.session_state.nav_radio)]
            if st.session_state.page != "risk":
                st.session_state.selected_cluster = None

        # keep the widget in sync with page changes coming from deep links /
        # cross-link buttons; a stale widget value would otherwise override them
        if st.session_state.get("nav_radio") != labels[index]:
            st.session_state["nav_radio"] = labels[index]

        st.radio(
            "Navigasi",
            labels,
            index=index,
            label_visibility="collapsed",
            key="nav_radio",
            on_change=_on_nav,
        )

        st.markdown("<div style='height:2.25rem'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="j-sidecard">
              <div style="font-weight:600;color:#132A1C;display:flex;align-items:center;">
                <span class="dot teal"></span>BPJS VERIFIKATOR
              </div>
              <div style="margin-top:4px;">PoC Node 04 · Aktif</div>
              <div>Model GNN v2.4 (Sync OK)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
