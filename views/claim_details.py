import streamlit as st

from components import cards, charts, guide, layout, tables, verifier_tools
from components import bench
from core import evidence as evidence_core
from core.privacy import mask_participant_id


def render():
    live = bench.get_live()
    TRIAGE_QUEUE = live.triage_rows()
    selected = st.session_state.get("selected_cluster")
    if selected not in live.by_id:
        selected = TRIAGE_QUEUE[0]["id"]
    detail = live.detail(selected)
    queue_row = next(q for q in TRIAGE_QUEUE if q["id"] == selected)
    auc = bench.get_metrics()["scorers"]["graph_gbm"]["auc"]
    review = bench.get_feedback().get(selected)
    if review and review.get("verdict") == "confirm":
        review_status, review_tone = "Dikonfirmasi untuk tindak lanjut", "teal"
        next_step = "Pilih tindakan pemeriksaan dan catat alasannya di Audit Action."
    elif review and review.get("verdict") == "dismiss":
        review_status, review_tone = "Ditandai sebagai pola wajar", "grey"
        next_step = "Jika keputusan ini perlu ditinjau ulang, batalkan umpan balik dari Audit Action."
    else:
        review_status, review_tone = "Belum ada keputusan verifikator", "amber"
        next_step = "Periksa klaim sumber dan konteksnya, lalu catat keputusan atau permintaan pemeriksaan."

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="j-label" style="color:#0F766E;">Antrean pemeriksaan</span>
          <span class="j-sub"><span class="dot teal"></span>Skor: prototipe fitur graf (data sintetis)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    layout.page_header(
        "", "teal", "Claim Details · Alasan Penandaan",
        "Penjelasan mengapa kelompok klaim ini ditandai, disertai bukti dan klaim yang paling mencurigakan.",
        right_html=(
            '<div style="display:flex;gap:8px;">'
            '<span class="j-chip">Skor ≥50: tinjauan awal</span>'
            '<span class="j-chip">Prioritas tertinggi ditinjau dahulu</span></div>'
        ),
    )
    guide.render_page_guide("claim")

    action_col, info_col = st.columns([1, 2])
    with action_col:
        st.markdown(
            f'<div class="j-card j-review-status">'
            f'<div class="j-label">STATUS PEMERIKSAAN · SESI INI</div>'
            f'<div style="margin-top:7px;"><span class="j-pill {review_tone}">{review_status}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with info_col:
        st.markdown(
            f'<div class="j-card j-review-next">'
            f'<div class="j-label">LANGKAH BERIKUTNYA</div>'
            f'<div class="j-sub" style="margin-top:7px;">{next_step}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if st.button("Buka Audit Action", type="primary", icon=":material/arrow_forward:",
                 key="claim_open_audit", width="stretch"):
        layout.goto("audit", cluster=selected)

    cols = st.columns(4)
    for col, s in zip(cols, live.triage_stats(auc)):
        with col:
            st.markdown(
                f'<div class="j-card">{cards.stat_card(s["label"], s["value"], s["note"], delta=s["delta"], value_tone=s["tone"])}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    left, right = st.columns([3, 2])

    with left:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div class="j-h2">Klaster Sindikat Terdeteksi</div>
              <span class="j-pill grey">Q3 2026 Periode</span>
            </div>
            <div class="j-sub" style="margin-bottom:8px;">Menampilkan {len(TRIAGE_QUEUE)} klaster, urut skor jaringan</div>
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
        verifier_tools.evidence_button(live, selected, key="evidence_claim")
        verifier_tools.modus_note(live.by_id[selected]["typology"])

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
                  <div class="j-label" style="color:#0F766E;">RINGKASAN PEMERIKSAAN · DATA SINTETIS</div>
                  <div class="j-h1" style="font-size:24px;margin:4px 0 8px;">Detail Klaim</div>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <b style="color:#0F766E;font-size:16px;">{detail.get('title', queue_row['name'])}</b>
                {cards.badge(*detail['typology'])}
              </div>
              <div style="margin:8px 0 14px;">{cards.badge(detail['flag'], 'red-solid')}</div>

              <div class="j-card tint" style="padding:14px;">
                <div class="j-label" style="margin-bottom:10px;">RINGKASAN ENTITAS DALAM KLASTER</div>
                <div class="j-detail-profile">
                  {profile_html}
                </div>
              </div>

              <div class="j-h2" style="margin:16px 0 2px;">Frekuensi Klaim dari Waktu ke Waktu</div>
              <div class="j-sub">Klaim ditandai per periode ±16 hari, dibanding klaim lain di faskes yang sama</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            charts.freq_chart(detail["timeline"]["labels"], detail["timeline"]["others"], detail["timeline"]["flagged"], detail["peak"]),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.markdown(
            f"""
            <div class="j-alert-red" style="background:#FDF1EC;">
              <b>🧠 Mengapa ditandai?</b>
              <div style="margin-top:6px;color:#475569;">{detail['why']}</div>
              <div style="margin-top:8px;color:#0F766E;font-size:12px;">🕸 {detail['why_note']}</div>
            </div>
            <div class="j-h2" style="margin:16px 0 8px;">Bukti Terukur (dari fitur klaim)</div>
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

    # Klaim sumber dapat diperiksa langsung; batasi tabel layar agar tetap ringan.
    with st.expander("Telusuri klaim sumber dan alasan per klaim"):
        claim_rows = evidence_core.claims_table(live, selected)
        if st.session_state.get("demo_role", "Verifikator") == "Verifikator":
            claim_rows["patient_id"] = claim_rows["patient_id"].map(mask_participant_id)
        st.caption(
            f"Menampilkan 25 dari {len(claim_rows)} klaim terkait, diurutkan menurut skor. "
            + ("ID peserta disamarkan pada tampilan Verifikator. "
               if st.session_state.get("demo_role", "Verifikator") == "Verifikator" else "")
            + "Ini simulasi peran; data peserta tetap sintetis dan ini bukan kontrol akses produksi."
        )
        visible = claim_rows.head(25)[
            ["claim_id", "faskes_id", "doctor_id", "visit_ts", "skor", "dugaan_tipologi", "alasan"]
        ].rename(columns={
            "claim_id": "ID klaim", "faskes_id": "ID faskes", "doctor_id": "ID dokter",
            "visit_ts": "Waktu layanan", "skor": "Skor model", "dugaan_tipologi": "Pola dugaan",
            "alasan": "Alasan terukur",
        })
        st.dataframe(visible, width="stretch", hide_index=True, height=420)
        st.download_button(
            "Unduh seluruh klaim sumber (.CSV)",
            claim_rows.to_csv(index=False).encode("utf-8"),
            file_name=f"jala_{selected}_klaim_sumber.csv",
            mime="text/csv",
            width="stretch",
            key=f"claim_trace_{selected}",
        )

    verifier_tools.review_timeline(selected, key=f"claim_history_{selected}")
    layout.render_footer()
