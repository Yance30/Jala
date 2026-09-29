import streamlit as st

from components import cards, layout
from data.mock_data import (
    PIPELINE_FORMULAS,
    PIPELINE_HEALTH,
    PIPELINE_MAPPING,
    PIPELINE_STEPS,
)


def render():
    left, right = st.columns([3, 1])
    with left:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;">
              <span class="j-pill teal">HETEROGENEOUS GRAPH ARCHITECTURE</span>
              <span class="j-sub"><span class="dot teal"></span>Graph Engine v2.4 Active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        b1, b2 = st.columns(2)
        if b1.button("▶ Trigger Batch Ingestion", width="stretch"):
            st.toast("Batch ingestion dijadwalkan ulang (02:00 WIB).", icon="✅")
        if b2.button("⚙ Hyperparameters", width="stretch"):
            st.session_state.show_hyper = not st.session_state.get("show_hyper", False)

    layout.page_header(
        "", "teal", "Detection Pipeline",
        "Automated four-stage graph neural network pipeline. Converts high-frequency raw claims into a "
        "multidimensional clinical topology to expose organized collusion networks, systemic phantom "
        "billing, and upcoding clusters.",
        right_html=(
            '<div class="j-card tint" style="padding:12px 16px;text-align:left;">'
            '<div class="j-label">Audit Model State</div>'
            '<div style="font-weight:600;margin-top:2px;">✅ HAN-v4.1 · Fully Converged</div></div>'
        ),
    )

    if st.session_state.get("show_hyper"):
        with st.expander("Hyperparameters (HAN v4)", expanded=True):
            st.code(PIPELINE_FORMULAS, language=None)

    cols = st.columns(4)
    for col, step in zip(cols, PIPELINE_STEPS):
        with col:
            st.markdown(
                f"""
                <div class="j-card" style="height:100%;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
                    <div style="display:flex;gap:10px;align-items:center;">
                      <span class="j-iconbox teal">{step['icon']}</span>
                      <div>
                        <div class="j-label" style="color:#0F766E;">{step['step'].upper()}</div>
                        <div style="font-size:16px;font-weight:600;">{step['title']}</div>
                      </div>
                    </div>
                    {cards.badge(*step['tag'])}
                  </div>
                  <div class="j-body" style="font-size:12.5px;margin:12px 0;">{step['body']}</div>
                  <div class="j-note" style="flex-direction:column;align-items:stretch;gap:4px;">
                    <div style="display:flex;justify-content:space-between;gap:8px;">
                      <span class="j-label">{step['metric_label']}</span>
                      <b style="color:#0F766E;font-size:13px;">{step['metric_value']}</b>
                    </div>
                    <div class="j-sub">{step['metric_note']}</div>
                  </div>
                  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;">
                    {''.join(cards.badge(t, tone) for t, tone in step['chips'])}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        rows = "".join(
            f"""
            <div style="display:flex;justify-content:space-between;gap:10px;background:#F1F5F9;
                        border-radius:6px;padding:10px 12px;margin-bottom:8px;">
              <span class="j-sub">{a}</span><b style="font-size:13px;">{b}</b>
            </div>
            """
            for a, b in PIPELINE_MAPPING
        )
        st.markdown(
            f"""
            <div class="j-card" style="height:100%;">
              <div class="j-h2">Heterogeneous Graph Mapping</div>
              <div class="j-body" style="font-size:12.5px;margin:8px 0 12px;">
                Structured raw claim streams (TXT/JSON claims via BPJS VClaim API) are parsed into directed
                multi-relational graphs preserving temporal timestamps.</div>
              {rows}
              <div style="display:flex;justify-content:space-between;margin-top:12px;">
                <span class="j-label">Graph Store Engine</span>
                <b style="color:#0F766E;">Neo4j Enterprise Cluster</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="j-card" style="height:100%;">
              <div class="j-h2">Community &amp; HAN Formulation</div>
              <div class="j-body" style="font-size:12.5px;margin:8px 0 12px;">
                Dual-level attention computes weights across both intra-metapath neighbors and
                inter-metapath semantics to prevent false positives from benign clinics.</div>
              <div class="j-code">{PIPELINE_FORMULAS}</div>
              <div style="display:flex;justify-content:space-between;margin-top:12px;">
                <span class="j-label">Convergence Loss</span>
                <b style="color:#0F766E;">Cross-Entropy Loss: 0.0142</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="j-card tealwash" style="height:100%;">
              <span class="j-pill" style="background:#0F766E;color:#fff;">VERIFIKATOR PROTOCOL</span>
              <div class="j-body" style="font-size:12.5px;margin:12px 0;">
                Output clusters directly integrate into the Berita Acara Pemeriksaan Khusus (BAPK) system.
                Verifikators can inspect the interactive node tree before issuing payment holds.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explore Live Network Graph →", key="go_network"):
            layout.goto("network")

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    cells = "".join(
        f'<div><span class="j-sub">{label}</span> <b style="color:#0F766E;">{value}</b></div>'
        for label, value in PIPELINE_HEALTH
    )
    st.markdown(
        f"""
        <div class="j-card" style="display:flex;gap:28px;flex-wrap:wrap;align-items:center;">
          {cells}
          <div style="margin-left:auto;" class="j-sub">Last batch processed: 18 min ago</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⟳ Run Pipeline Diagnostic", key="diag"):
        st.toast("Diagnostic selesai: Pipeline Health Optimal (99.8% sync).", icon="✅")

    layout.render_footer()
