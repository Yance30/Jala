import pandas as pd
import streamlit as st

from components import bench, cards, case_search, export_context, guide, layout, tables, verifier_tools
from core.live import AUTO_FLAG, THRESH
from components.typology import LABELS


# ==========================================================
# FILTER DATA
# ==========================================================

def _filtered(rows, chip, query):
    """
    Filter data berdasarkan:
    - Semua Entitas
    - Score > 85%
    - Phantom Billing
    - Repeat Billing
    - Search Entity ID / Ring Name / Faskes
    """

    out = rows

    # Filter berdasarkan chip
    if chip.startswith("Prioritas otomatis"):
        out = [
            r for r in out
            if r["score"] >= AUTO_FLAG
        ]

    elif chip == LABELS["Phantom Billing"]:
        out = [
            r for r in out
            if r["typology"][0] == "Phantom Billing"
        ]

    elif chip == LABELS["Repeat Billing"]:
        out = [
            r for r in out
            if r["typology"][0] == "Repeat Billing"
        ]

    elif chip == LABELS["Self-Referral"]:
        out = [
            r for r in out
            if r["typology"][0] == "Self-Referral"
        ]

    # Filter berdasarkan search
    if query:
        q = query.lower().strip()

        out = [
            r for r in out
            if (
                q in r["name"].lower()
                or q in r["subtitle"].lower()
                or q in r["id"].lower()
            )
        ]

    return out


def _clear_local_filters(default_chip):
    st.session_state["risk_query"] = ""
    st.session_state["risk_chip"] = default_chip
    st.session_state["case_search_query"] = ""
    st.session_state["case_search_filter"] = case_search.ALL_CASES


# ==========================================================
# MAIN RENDER
# ==========================================================

def render():

    live = bench.get_live()
    RISK_CLUSTERS = live.risk_rows()
    if not RISK_CLUSTERS:
        layout.page_header("", "teal", "Prioritas Klaster", "Belum ada klaster untuk ditinjau pada data ini.")
        st.info("Tidak ada kasus pada antrean saat ini. Coba perbarui data demo atau hapus filter pencarian.")
        layout.render_footer()
        return
    RISK_FILTERS = [
        f"Semua Entitas ({len(RISK_CLUSTERS)})",
        f"Prioritas otomatis ({AUTO_FLAG}%+) · {sum(r['score'] >= AUTO_FLAG for r in RISK_CLUSTERS)}",
        LABELS["Phantom Billing"], LABELS["Repeat Billing"], LABELS["Self-Referral"],
    ]
    filter_options = [
        (RISK_FILTERS[0], f"Semua · {len(RISK_CLUSTERS)}"),
        (RISK_FILTERS[1], f"Prioritas ≥{AUTO_FLAG}% · {sum(r['score'] >= AUTO_FLAG for r in RISK_CLUSTERS)}"),
        (RISK_FILTERS[2], "Phantom Billing"),
        (RISK_FILTERS[3], "Repeat Billing"),
        (RISK_FILTERS[4], "Self-referral"),
    ]
    action_labels = {
        "freeze": ("Penangguhan simulasi dicatat", "red"),
        "field_audit": ("Rencana pemeriksaan dicatat", "teal"),
        "dismiss": ("Pola wajar (simulasi)", "grey"),
    }
    for row in RISK_CLUSTERS:
        action = st.session_state.get("audited", {}).get(row["id"])
        from components.review_status import cluster_status
        label, tone, completed = cluster_status(action, bench.get_feedback().get(row["id"]))
        row["status"] = (label, tone)
        row["review_completed"] = completed
    RISK_STATS = live.risk_stats(audited=len(st.session_state.get("audited", {})))

    # ======================================================
    # HEADER
    # ======================================================

    right = (
        '<div style="display:flex;gap:8px;justify-content:flex-end;">'
        f'<span class="j-chip">⚙ Prioritas klaster awal: ≥{AUTO_FLAG}/100 · ambang skor klaim: {THRESH:.0%}</span>'
        '</div>'
    )

    layout.page_header(
        "",
        "teal",
        "Prioritas Klaster",
        f"Kelompok klaim diurutkan untuk membantu menentukan urutan pemeriksaan. Skor {AUTO_FLAG}% ke atas "
        "masuk prioritas awal; skor bukan probabilitas atau bukti kecurangan.",
        right_html=right,
    )
    guide.render_page_guide("risk")
    guide.render_typology_glossary()


    # ======================================================
    # PAGE LABEL
    # ======================================================

    st.markdown(
        """
        <div style="margin:4px 0 16px 0;">
            <span class="j-pill teal">
                Prioritas Klaster · dihitung dari skor prototipe (data sintetis)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    verifier_tools.feedback_banner(live)


    # ======================================================
    # EXPORT AUDIT
    # ======================================================

    _all = pd.DataFrame(
        [
            {
                k: (
                    v[0]
                    if isinstance(v, tuple)
                    else v
                )
                for k, v in c.items()
            }
            for c in RISK_CLUSTERS
        ]
    )

    st.download_button(
        "⬇ Ekspor Bukti Audit",
        export_context.csv_bytes(_all),
        file_name="jala_bukti_audit.csv",
        type="primary",
        key="export_top",
    )


    # ======================================================
    # KPI CARDS
    # ======================================================

    cols = st.columns(4)

    for col, s in zip(cols, RISK_STATS):

        with col:

            # Jika note kosong, gunakan nbsp agar tinggi
            # semua card tetap sama
            note = s["note"] or "&nbsp;"

            st.markdown(
                f"""
                <div class="j-card j-risk-kpi-card">
                    {
                        cards.stat_card(
                            s["label"],
                            s["value"],
                            note,
                            s["icon"],
                            s["icon_tone"],
                            s["tone"],
                        )
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )


    # ======================================================
    # SPACING
    # ======================================================

    st.markdown(
        '<div style="height:14px"></div>',
        unsafe_allow_html=True,
    )


    # ======================================================
    # SEARCH + FILTER
    # ======================================================

    with st.container(key="risk_filters"):
        query = st.text_input(
            "Cari klaster",
            placeholder="Cari ID klaster, nama jaringan, atau faskes…",
            key="risk_query",
        )

        chip = st.session_state.get(
            "risk_chip",
            RISK_FILTERS[0],
        )

        st.markdown('<div class="j-filter-label">Filter antrean</div>', unsafe_allow_html=True)
        groups = (filter_options[:2], filter_options[2:])
        for group in groups:
            filter_cols = st.columns(len(group), gap="small")
            for col, (value, label) in zip(filter_cols, group):
                with col:
                    is_active = value == chip
                    if st.button(
                        label,
                        key=f"chip_{value}",
                        width="stretch",
                        type="primary" if is_active else "secondary",
                    ):
                        st.session_state.risk_chip = value
                        st.rerun()


    # ======================================================
    # FILTER DATA
    # ======================================================

    # Filter sidebar berlaku lintas halaman; kontrol lokal tetap dapat mempersempit antrean.
    global_query = st.session_state.get("case_search_query", "")
    rows = case_search.filter_rows(
        RISK_CLUSTERS,
        global_query,
        st.session_state.get("case_search_filter", case_search.ALL_CASES),
    )
    rows = _filtered(
        rows,
        chip,
        query,
    )
    order = st.selectbox("Urutan klaster", ["Skor tertinggi", "Belum selesai lebih dahulu"], key="risk_review_order")
    rows = sorted(rows, key=lambda row: ((row.get("review_completed", False) if order == "Belum selesai lebih dahulu" else False), -row["score"], row["id"]))
    shared_filter = st.session_state.get("case_search_filter", case_search.ALL_CASES)
    active_filter = next((label for value, label in filter_options if value == chip), chip)
    st.markdown(
        f'<div class="j-filter-summary"><span><b>{len(rows)}</b> dari '
        f'{len(RISK_CLUSTERS)} klaster ditampilkan</span><span>{shared_filter} · {active_filter}</span></div>',
        unsafe_allow_html=True,
    )
    if global_query or query:
        terms = []
        if global_query:
            terms.append(f"sidebar: {global_query}")
        if query:
            terms.append(f"antrean: {query}")
        st.caption("Pencarian aktif — " + " · ".join(terms))
    if query or chip != RISK_FILTERS[0] or shared_filter != case_search.ALL_CASES:
        st.button("Hapus filter antrean", key="risk_clear_filters",
                  on_click=_clear_local_filters, args=(RISK_FILTERS[0],))


    # ======================================================
    # RISK TABLE
    # ======================================================

    with st.container(border=True):

        if rows:

            st.markdown(
                tables.risk_table_html(rows),
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "Tidak ada klaster yang cocok "
                "dengan filter/pencarian."
            )


    # ======================================================
    # FOOTER TABLE
    # ======================================================

    st.markdown(
        f"""
        <div class="j-footer" style="margin-top:14px;">

            <div>
                ✅ Menampilkan klaster hasil partisi Louvain
                dari data sintetis (prototipe)
            </div>

            <div>
                Cycle ID: #2026Q3-LOUVAIN
                &nbsp;•&nbsp;
                Modularitas Q = {live.modularity:.2f}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    if rows:
        row_by_id = {row["id"]: row for row in rows}
        options = list(row_by_id)
        if st.session_state.get("risk_pick_id") not in row_by_id:
            st.session_state["risk_pick_id"] = options[0]

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        with st.container(key="risk_actions"):
            picked = st.selectbox(
                "Pilih klaster untuk melihat detail",
                options,
                key="risk_pick_id",
                format_func=lambda cluster_id: (
                    f"{row_by_id[cluster_id]['name']} · "
                    f"{row_by_id[cluster_id]['score']}/100"
                ),
            )
            st.caption("Alur: pilih klaster → buka detail → periksa bukti → catat tindak lanjut.")
            if st.button(
                "Buka detail kasus",
                width="stretch",
                type="primary",
                icon=":material/arrow_forward:",
                key="risk_open_detail",
            ):
                layout.goto("claim", cluster=picked)

            with st.expander("Aksi lainnya"):
                df = pd.DataFrame(
                    [
                        {
                            key: value[0] if isinstance(value, tuple) else value
                            for key, value in row.items()
                        }
                        for row in rows
                    ]
                )
                st.download_button(
                    "Unduh daftar terfilter (.CSV)",
                    export_context.csv_bytes(df),
                    file_name="jala_risk_ranking.csv",
                    mime="text/csv; charset=utf-8",
                    width="stretch",
                )


    # ======================================================
    # FOOTER
    # ======================================================

    layout.render_footer()
