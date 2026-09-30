import streamlit as st

from components import layout
from data.mock_data import ABOUT
from views import comparison


def _divider(anchor: str):
    st.markdown(
        f'<div id="{anchor}" class="j-anchor j-section-gap"></div>',
        unsafe_allow_html=True,
    )


def _hero():
    st.markdown(
        """
        <div style="text-align:center;margin:14px 0 8px;">
          <span class="j-pill teal">TENTANG JALA</span>
          <div class="j-h1" style="font-size:32px;margin:14px 0 6px;">JALA — Jaringan Analitik Lintas Aktor</div>
          <div class="j-body" style="max-width:760px;margin:0 auto;">Platform analitik graf untuk mendeteksi
            kecurangan klaim BPJS Kesehatan: dari perbandingan dengan pendekatan lama,
            hingga catatan privasi data prototipe.</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:16px;">
            <a class="j-pill teal" href="#comparison" target="_self">Perbandingan Paradigma</a>
            <a class="j-pill teal" href="#privacy" target="_self">Privasi &amp; Sumber Data</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _privacy():
    st.markdown(
        f"""
        <div style="text-align:center;margin:14px 0 24px;">
          <span class="j-pill teal">DATA INTEGRITY &amp; STATUTORY COMPLIANCE</span>
          <div class="j-h1" style="font-size:30px;margin:14px 0 6px;">{ABOUT['title']}</div>
          <div class="j-body">{ABOUT['subtitle']}</div>
        </div>
        <div class="j-card tealwash" style="max-width:860px;margin:0 auto;text-align:center;padding:1.75rem;">
          <div style="font-size:15px;font-style:italic;color:#132A1C;">{ABOUT['quote']}</div>
        </div>
        <div style="height:16px"></div>
        <div class="j-card" style="max-width:860px;margin:0 auto;">
          <div class="j-h2">⚖ Landasan Yuridis</div>
          <div class="j-body" style="margin-top:6px;">{ABOUT['law']}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;">
            {''.join(f'<span class="j-pill {tone}">{label}</span>' for label, tone in ABOUT['chips'])}
          </div>
        </div>
        <div style="height:16px"></div>
        <div class="j-sub" style="text-align:center;">{ABOUT['owner']}</div>
        """,
        unsafe_allow_html=True,
    )


def render():
    _hero()
    _divider("comparison")
    comparison.render_content()
    _divider("privacy")
    _privacy()
    layout.render_footer()