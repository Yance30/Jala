import streamlit as st

from components import cards, charts, layout
from data.mock_data import DASHBOARD_FOOTER, DASHBOARD_KPIS, QUARTERS


def render():
    col_sel, col_sync = st.columns([3, 1])
    with col_sel:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;">
              <span class="j-pill teal">FORENSIC TELEMETRY</span>
              <span class="j-sub"><span class="dot teal"></span>BPJS Unit Pengawasan Klaim Khusus</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_sync:
        st.markdown(
            '<div class="j-chip" style="float:right;margin-bottom:6px;"><span class="dot teal"></span>'
            'HIN Node Sync: <b style="color:#0F766E;">99.8%</b></div>',
            unsafe_allow_html=True,
        )
        quarter = st.selectbox("Periode", QUARTERS, index=0, label_visibility="collapsed")
    st.markdown(
        f"""
        <div class="j-h1" style="font-size:34px;color:#0F766E;">Fraud Intelligence Dashboard</div>
        <div class="j-body">Powered by Heterogeneous Graph Neural Network (HAN) on a Neo4j-based
        Heterogeneous Information Network (HIN)</div>
        <div class="j-sub" style="margin-top:6px;">Periode aktif: <b>{quarter}</b></div>
        <div style="height:16px"></div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, kpi in zip(cols, DASHBOARD_KPIS):
        with col:
            st.markdown(
                cards.metric_card(
                    kpi["label"].upper(),
                    kpi["value"],
                    badge_html=cards.badge(*kpi["badge"]),
                    note=kpi["note"],
                    icon=kpi["icon"],
                ),
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="j-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div class="j-h2" style="color:#0F766E;">Detection Trends Across Fraud Typologies
                (Weekly HIN Ingestion)</div>
              <div class="j-sub">Temporal variation of flagged anomalies captured by HAN attention layers</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(charts.trend_chart(), width="stretch", config={"displayModeBar": False})

    cols = st.columns(3)
    for col, item in zip(cols, DASHBOARD_FOOTER):
        with col:
            tone = "red" if item["tone"] == "red" else "dark"
            extra = f' <span style="color:#C2410C;font-size:12px;">{item["extra"]}</span>' if item.get("extra") else ""
            st.markdown(
                f"""
                <div style="display:flex;gap:12px;align-items:flex-start;">
                  <span class="j-iconbox {'red' if item['tone'] == 'red' else 'grey'}">{item['icon']}</span>
                  <div>
                    <div class="j-label">{item['label']}</div>
                    <div class="j-value {tone}" style="font-size:16px;font-weight:600;margin-top:2px;">
                      {item['value']}{extra}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    layout.render_footer()
