import streamlit as st

from components.theme import ICON_CALENDAR_SVG, ICON_USER_SVG, LOGO_SVG
from data.mock_data import FOOTER_CUTOFF, FOOTER_STATUS, PAGE_TITLES, QUARTER


def render_topbar(page: str):
    title = PAGE_TITLES.get(page, "Workspace")
    st.markdown(
        f"""
        <div class="j-topbar">
          <div style="display:flex;align-items:center;gap:12px;">
            <div class="j-logo" style="width:34px;height:34px;">{LOGO_SVG}</div>
            <div class="j-crumb">
              Tim Pencegahan Fraud <span class="sep">›</span> JALA Core <span class="sep">›</span> <b>{title}</b>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;">
            <span class="j-chip">{ICON_CALENDAR_SVG} {QUARTER}</span>
            <span class="j-avatar">{ICON_USER_SVG}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, eyebrow_tone: str, title: str, subtitle: str, right_html: str = ""):
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
          <div>
            <div style="margin-bottom:6px;">
              <span class="j-pill {eyebrow_tone}">{eyebrow}</span>
            </div>
            <div class="j-h1">{title}</div>
            <div class="j-body" style="max-width:860px;">{subtitle}</div>
          </div>
          <div style="text-align:right;">{right_html}</div>
        </div>
        <div style="height:18px"></div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    items = "".join(
        f'<span><span class="dot {tone}"></span>{text}</span>' for tone, text in FOOTER_STATUS
    )
    st.markdown(
        f"""
        <div class="j-footer">
          <div style="display:flex;gap:22px;flex-wrap:wrap;">{items}</div>
          <div>{FOOTER_CUTOFF}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def goto(page: str, cluster: str | None = None):
    st.session_state.page = page
    if cluster is not None:
        st.session_state.selected_cluster = cluster
    if page != "risk" and page != "claim":
        st.session_state.selected_cluster = None
    st.rerun()
