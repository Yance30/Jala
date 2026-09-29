import streamlit as st

from components import layout
from data.mock_data import ABOUT


def render():
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
    layout.render_footer()
