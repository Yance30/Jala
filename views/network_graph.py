import streamlit as st
import streamlit.components.v1 as components

from components import cards, charts, layout
from data.mock_data import (
    GRAPH_LEGEND_EDGES,
    GRAPH_LEGEND_NODES,
    RISK_LEVELS,
    TYPOLOGIES,
)


def render():
    layout.page_header(
        "", "teal", "Network Graph",
        "Interactive Heterogeneous Information Network (HIN) topology viewer with Louvain community "
        "detection and Heterogeneous Graph Attention Network (HAN) anomaly scoring.",
        right_html=(
            '<div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">'
            '<span class="j-chip"><span class="dot teal"></span>Graph Engine v2.4 Active</span>'
            '<span class="j-chip"><span class="ms">hub</span> Louvain Clusters: 42 Detected</span>'
            '<span class="j-chip"><span class="ms">schedule</span> Timestamped Edges Active</span></div>'
        ),
    )
    st.markdown(
        '<div style="margin:-6px 0 12px 0;"><span class="j-pill teal">HIN Topology</span></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        t1, t2, t3, t4 = st.columns([2, 1.4, 1.4, 1.6])
        with t1:
            query = st.text_input("search", placeholder="Search Entity (Faskes ID, Dokter SIP…)  ⌘K",
                                  label_visibility="collapsed")
        with t2:
            risk = st.selectbox("risk", RISK_LEVELS, index=1, label_visibility="collapsed")
        with t3:
            typo = st.selectbox("typo", TYPOLOGIES, index=1, label_visibility="collapsed")
        with t4:
            # ikon Material (bukan glyph unicode) supaya selalu terlihat di HP
            with st.container(key="net_zoom"):
                b1, b2, b3, b4, b5 = st.columns(5)
                if b1.button("", icon=":material/refresh:", help="Reset View", key="z_reset", width="stretch"):
                    st.session_state.zoom = 1.0
                    st.session_state.isolate = False
                    st.rerun()
                if b2.button("", icon=":material/add:", help="Zoom in", key="z_in", width="stretch"):
                    st.session_state.zoom = min(1.6, st.session_state.get("zoom", 1.0) + 0.2)
                    st.rerun()
                if b3.button("", icon=":material/remove:", help="Zoom out", key="z_out", width="stretch"):
                    st.session_state.zoom = max(0.8, st.session_state.get("zoom", 1.0) - 0.2)
                    st.rerun()
                if b4.button("", icon=":material/fit_screen:", help="Fit", key="z_fit", width="stretch"):
                    st.session_state.zoom = 1.0
                    st.rerun()
                if b5.button("", icon=":material/my_location:", help="Center on Critical Cluster", key="z_center", width="stretch"):
                    st.session_state.isolate = True
                    st.rerun()

    isolate = st.session_state.get("isolate", False)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Center on Critical Cluster", icon=":material/center_focus_strong:", key="center"):
            st.session_state.isolate = not isolate
            st.rerun()
    with c2:
        st.caption(f"Filter aktif: {risk} · {typo}" + (f" · query: “{query}”" if query else ""))

    st.markdown(
        """
        <div class="j-alert-red" style="display:flex;gap:10px;align-items:flex-start;margin:6px 0 12px;">
          <span><span class="ms">warning</span></span>
          <div><b>HAN ANOMALY ALERT #JALA-HAN-089</b>
            <span class="j-pill red-solid" style="margin-left:8px;">Score 0.94</span>
            <div style="margin-top:4px;">Spatial-temporal anomaly: hundreds of patients from different
            regions mobilized to one facility simultaneously</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    zoom = st.session_state.get("zoom", 1.0)
    graph_html = charts.network_animated_html(zoom=zoom, isolate=isolate)
    graph_h = int(620 * min(max(zoom, 0.8), 1.6))
    # container ber-key: di mobile kanvas dilebarkan (min-width) dan bisa digeser horizontal
    with st.container(key="network_chart"):
        if hasattr(st, "iframe"):  # Streamlit terbaru (components.v1.html sudah deprecated)
            st.iframe(graph_html, height=graph_h)
        else:  # Streamlit lama (mis. 1.57)
            components.html(graph_html, height=graph_h)

    l1, l2 = st.columns([1, 1])
    with l1:
        node_rows = "".join(
            f"""
            <div style="display:flex;align-items:center;gap:8px;background:#F8FAFC;border-radius:6px;
                        padding:6px 10px;margin-bottom:6px;">
              <span style="width:12px;height:12px;background:{color};display:inline-block;
                           border-radius:{ '9999px' if sym == 'circle' else ('0' if sym == 'square' else '2px')};
                           transform:{'rotate(45deg)' if sym == 'diamond' else 'none'};"></span>
              <span style="font-size:12.5px;">{label}</span>
            </div>
            """
            for label, sym, color in GRAPH_LEGEND_NODES
        )
        edge_rows = "".join(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;
                        padding:4px 2px;font-size:12.5px;">
              <span style="display:flex;align-items:center;gap:8px;">
                <span style="width:26px;border-top:2px {'solid' if s == 'solid' else ('dashed' if s == 'dash' else 'dotted')} #475569;"></span>
                {label}
              </span>
              <span class="j-sub">Timestamped</span>
            </div>
            """
            for label, s in GRAPH_LEGEND_EDGES
        )
        st.markdown(
            f"""
            <div class="j-card">
              <div class="j-h2"><span class="ms">hub</span> Graph Legend &amp; Metapath Schema</div>
              <div class="j-label" style="margin:10px 0 6px;">Node Types</div>
              {node_rows}
              <div class="j-label" style="margin:10px 0 6px;">Edge Metapaths</div>
              {edge_rows}
              <div style="display:flex;gap:16px;margin-top:8px;font-size:12.5px;">
                <span><span class="dot teal"></span>Normal Baseline</span>
                <span style="color:#C2410C;"><span class="dot amber"></span>Suspicious Anomaly</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with l2:
        st.markdown(
            f"""
            <div class="j-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="j-h2"><span class="dot red"></span>Flagged Cluster #JALA-HAN-089</div>
                {cards.badge('CRITICAL', 'red')}
              </div>
              <div class="j-sub" style="margin:4px 0 12px;">Identified via Heterogeneous Graph Attention
                Network</div>
              <div style="display:flex;gap:12px;">
                <div class="j-note" style="flex:1;flex-direction:column;gap:2px;">
                  <span class="j-label">HAN Attention Risk</span>
                  <span class="j-value red" style="font-size:24px;">0.94</span>
                  <span class="j-sub">Percentile: 99.8%</span>
                </div>
                <div class="j-note" style="flex:1;flex-direction:column;gap:2px;">
                  <span class="j-label">Louvain Modularity</span>
                  <span class="j-value dark" style="font-size:24px;">Q = 0.72</span>
                  <span class="j-sub">Dense Sub-clique</span>
                </div>
              </div>
              <div style="margin-top:12px;" class="j-sub">Anomaly Typology:</div>
              <div style="font-size:13px;font-weight:600;"><span class="ms">swap_horiz</span> Cross-Regional Influx &amp; Coordinated Referral</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        if b1.button("Isolate Subgraph", icon=":material/filter_alt:", width="stretch", key="iso"):
            st.session_state.isolate = not isolate
            st.rerun()
        if b2.button("Risk Ranking", icon=":material/analytics:", width="stretch", key="go_risk"):
            layout.goto("risk")
        if st.button("Initiate Audit Action", icon=":material/gavel:", width="stretch", type="primary", key="go_audit"):
            layout.goto("audit")

    layout.render_footer()