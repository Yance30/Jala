import streamlit as st

from components import cards, charts, layout, tables
from data.mock_data import CLAIM_DETAILS, DEFAULT_DETAIL, TRIAGE_QUEUE, TRIAGE_STATS


def render():
    selected = st.session_state.get("selected_cluster") or TRIAGE_QUEUE[0]["id"]
    detail = CLAIM_DETAILS.get(selected, DEFAULT_DETAIL)
    queue_row = next((q for q in TRIAGE_QUEUE if q["id"] == selected), TRIAGE_QUEUE[0])

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="j-label" style="color:#0F766E;">AUDIT TRIAGE QUEUE</span>
          <span class="j-sub"><span class="dot teal"></span>Model Inference: GNN-HAN v2.4</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    layout.page_header(
        "", "teal", "Daftar Prioritas Anomali Klaim BPJS",
        "Penyortiran klaster risiko multi-entitas terdeteksi sinkronisasi abnormal pada triwulan berjalan.",
        right_html=(
            '<div style="display:flex;gap:8px;">'
            '<span class="j-chip">⚙ Filter Heterogen (Aktif: 4)</span>'
            '<span class="j-chip">⇅ Skor Tertinggi (Desc)</span></div>'
        ),
    )

    cols = st.columns(4)
    for col, s in zip(cols, TRIAGE_STATS):
        with col:
            st.markdown(
                f'<div class="j-card">{cards.stat_card(s["label"], s["value"], s["note"], delta=s["delta"], value_tone=s["tone"])}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    left, right = st.columns([3, 2])

    with left:
        st.markdown(
            """
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div class="j-h2">Klaster Sindikat Terdeteksi</div>
              <span class="j-pill grey">Q3 2024 Periode</span>
            </div>
            <div class="j-sub" style="margin-bottom:8px;">Menampilkan 1-6 dari 42 ring</div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(tables.triage_table_html(TRIAGE_QUEUE, selected), unsafe_allow_html=True)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        names = {q["id"]: q["name"] for q in TRIAGE_QUEUE}
        pick = st.selectbox("Buka detail klaster", list(names.values()),
                            index=list(names.keys()).index(selected), label_visibility="collapsed")
        if st.button("Buka Claim Details →", type="primary", width="stretch"):
            st.session_state.selected_cluster = list(names.keys())[list(names.values()).index(pick)]
            st.rerun()

    with right:
        profile_html = "".join(
            cards.kv(item[0], item[1], item[2] if len(item) > 2 else "")
            for item in detail["profile"]
        )
        st.markdown(
            f"""
            <div class="j-card" style="box-shadow:0 10px 25px -5px rgba(19,42,28,.08), 0 0 0 1px #E2E8F0;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div class="j-label" style="color:#0F766E;">FORENSIC AUDIT PANEL · Triwulan 3</div>
                  <div class="j-h1" style="font-size:24px;margin:4px 0 8px;">Claim Details</div>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <b style="color:#0F766E;font-size:16px;">{detail.get('title', queue_row['name'])}</b>
                {cards.badge(*detail['typology'])}
              </div>
              <div style="margin:8px 0 14px;">{cards.badge(detail['flag'], 'red-solid')}</div>

              <div class="j-card tint" style="padding:14px;">
                <div class="j-label" style="margin-bottom:10px;"> PROFIL ENTITAS SINDIKAT</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                  {profile_html}
                </div>
              </div>

              <div class="j-h2" style="margin:16px 0 2px;">Claim Frequency Over Time</div>
              <div class="j-sub">Frekuensi lonjakan pengajuan klaim vs ambang batas normal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            charts.freq_chart(detail["freq_labels"], detail["freq_baseline"], detail["freq_spike"], detail["peak"]),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.markdown(
            f"""
            <div class="j-alert-red" style="background:#FDF1EC;">
              <b>🧠 Why was this flagged?</b>
              <div style="margin-top:6px;color:#475569;">{detail['why']}</div>
              <div style="margin-top:8px;color:#0F766E;font-size:12px;">🕸 {detail['why_note']}</div>
            </div>
            <div class="j-h2" style="margin:16px 0 8px;">Metapath Evidence Breakdown</div>
            """,
            unsafe_allow_html=True,
        )
        for icon, title, note, b in detail["evidence"]:
            st.markdown(
                f"""
                <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">
                  <span class="j-iconbox grey">{icon}</span>
                  <div style="flex:1;">
                    <div style="display:flex;justify-content:space-between;gap:8px;">
                      <b style="font-size:13px;">{title}</b>{cards.badge(*b)}
                    </div>
                    <div class="j-sub">{note}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if st.button("✕ Tutup panel (kembali ke Risk Ranking)", width="stretch"):
            layout.goto("risk")

    layout.render_footer()
