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
    action_labels = {
        "freeze": ("Penangguhan simulasi dicatat", "red"),
        "field_audit": ("Rencana pemeriksaan dicatat", "teal"),
        "dismiss": ("Pola wajar (simulasi)", "grey"),
    }
    for row in RISK_CLUSTERS:
        action = st.session_state.get("audited", {}).get(row["id"])
        if action in action_labels and action != "dismiss":
            row["status"] = action_labels[action]
    RISK_STATS = live.risk_stats(audited=len(st.session_state.get("audited", {})))

    # ======================================================
    # CUSTOM CSS
    # ======================================================

    st.markdown(
        """
        <style>

        /* Semua aturan di-scope ke area konten utama halaman ini agar tidak
           bocor ke sidebar / halaman lain; !important tidak diperlukan karena
           spesifisitas [data-testid="stMain"] sudah mengalahkan chrome widget. */

        /* ==================================================
           SEARCH INPUT
           ================================================== */

        [data-testid="stMain"] div[data-testid="stTextInput"] input {
            height: 48px;
            min-height: 48px;
            box-sizing: border-box;
            border-radius: 6px !important;
            font-size: 15px;
        }


        /* ==================================================
           FILTER BUTTON
           ================================================== */

        [data-testid="stMain"] div[data-testid="stButton"] > button {
            height: 48px;
            min-height: 48px;
            max-height: 48px;
            width: 100%;
            box-sizing: border-box;
            padding: 0 10px;
            border-radius: 6px;
            font-size: 16px;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            align-items: center;
            justify-content: center;
        }


        /* ==================================================
           BUTTON CONTAINER
           ================================================== */

        [data-testid="stMain"] div[data-testid="stButton"] {
            height: 48px;
            min-height: 48px;
        }


        /* ==================================================
           FILTER COLUMN
           ================================================== */

        [data-testid="stMain"] div[data-testid="column"] {
            box-sizing: border-box;
        }


        /* ==================================================
           DOWNLOAD BUTTON
           ================================================== */

        [data-testid="stMain"] div[data-testid="stDownloadButton"] > button {
            min-height: 42px;
        }


        /* ==================================================
           SELECTBOX
           ================================================== */

        [data-testid="stMain"] div[data-testid="stSelectbox"] > div {
            min-height: 42px;
        }


        /* ==================================================
           REMOVE EXTRA SPACE AROUND FILTER
           ================================================== */

        [data-testid="stMain"] div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


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

    f1, f2 = st.columns(
        [2, 4],
        gap="small",
    )


    # ======================================================
    # SEARCH
    # ======================================================

    with f1:

        query = st.text_input(
            "Cari klaster",
            placeholder=(
                "Cari ID klaster, nama jaringan, atau faskes…"
            ),
            key="risk_query",
        )


    # ======================================================
    # FILTER BUTTONS
    # ======================================================

    with f2:

        # Ambil filter yang sedang aktif
        chip = st.session_state.get(
            "risk_chip",
            RISK_FILTERS[0],
        )


        # Buat 4 kolom dengan ukuran sama
        filter_cols = st.columns(
            len(RISK_FILTERS),
            gap="small",
        )


        # Render setiap tombol
        for col, label in zip(
            filter_cols,
            RISK_FILTERS,
        ):

            with col:

                is_active = label == chip

                if st.button(
                    ("Dipilih · " if is_active else "") + label,
                    key=f"chip_{label}",
                    width="stretch",
                    type=(
                        "primary"
                        if is_active
                        else "secondary"
                    ),
                ):

                    st.session_state.risk_chip = label

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
    shared_filter = st.session_state.get("case_search_filter", case_search.ALL_CASES)
    st.caption(f"Filter aktif: {shared_filter}; {chip} · {len(rows)} dari {len(RISK_CLUSTERS)} klaster")
    if global_query:
        st.caption(f"Pencarian bersama aktif: {global_query}")
    if query:
        st.caption(f"Pencarian aktif: {query}")
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


    # ======================================================
    # SPACING
    # ======================================================

    st.markdown(
        '<div style="height:16px"></div>',
        unsafe_allow_html=True,
    )


    # ======================================================
    # BOTTOM ACTION
    # ======================================================

    a1, a2, a3, a4 = st.columns(
        [2, 1, 1, 1],
        gap="small",
    )


    # ======================================================
    # SELECT CLUSTER
    # ======================================================

    with a1:

        names = {
            c["name"]: c["id"]
            for c in RISK_CLUSTERS
        }

        picked = st.selectbox(
            "Pilih klaster",
            list(names.keys()),
            label_visibility="collapsed",
            key="risk_pick",
        )


    # ======================================================
    # CLAIM DETAILS
    # ======================================================

    with a2:

        if st.button(
            "Buka alasan penandaan",
            width="stretch",
            type="primary",
        ):

            layout.goto(
                "claim",
                cluster=names[picked],
            )


    # ======================================================
    # NETWORK
    # ======================================================

    with a3:

        if st.button(
            "Lihat subgraf",
            width="stretch",
        ):

            layout.goto("network")


    # ======================================================
    # CSV EXPORT
    # ======================================================

    with a4:

        df = pd.DataFrame(
            [
                {
                    k: (
                        v[0]
                        if isinstance(v, tuple)
                        else v
                    )
                    for k, v in c.items()
                }
                for c in rows
            ]
        )

        st.download_button(
            "⬇ CSV",
            export_context.csv_bytes(df),
            file_name="jala_risk_ranking.csv",
            width="stretch",
        )


    # ======================================================
    # FOOTER
    # ======================================================

    layout.render_footer()
