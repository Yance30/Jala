import pandas as pd
import streamlit as st

from components import cards, layout, tables
from data.mock_data import RISK_CLUSTERS, RISK_FILTERS, RISK_STATS


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
    if chip.startswith(">85%"):
        out = [
            r for r in out
            if r["score"] > 85
        ]

    elif chip == "Phantom Billing":
        out = [
            r for r in out
            if r["typology"][0] == "Phantom Billing"
        ]

    elif chip == "Repeat Billing":
        out = [
            r for r in out
            if r["typology"][0] == "Repeat Billing"
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


# ==========================================================
# MAIN RENDER
# ==========================================================

def render():

    # ======================================================
    # CUSTOM CSS
    # ======================================================

    st.markdown(
        """
        <style>

        /* ==================================================
           SEARCH INPUT
           ================================================== */

        div[data-testid="stTextInput"] input {
            height: 48px !important;
            min-height: 48px !important;
            box-sizing: border-box !important;
            border-radius: 6px !important;
            font-size: 15px !important;
        }


        /* ==================================================
           FILTER BUTTON
           ================================================== */

        div[data-testid="stButton"] > button {
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;

            width: 100% !important;

            box-sizing: border-box !important;

            padding: 0 10px !important;

            border-radius: 6px !important;

            font-size: 16px !important;
            line-height: 1.2 !important;

            white-space: nowrap !important;

            overflow: hidden !important;
            text-overflow: ellipsis !important;

            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }


        /* ==================================================
           BUTTON CONTAINER
           ================================================== */

        div[data-testid="stButton"] {
            height: 48px !important;
            min-height: 48px !important;
        }


        /* ==================================================
           FILTER COLUMN
           ================================================== */

        div[data-testid="column"] {
            box-sizing: border-box !important;
        }


        /* ==================================================
           DOWNLOAD BUTTON
           ================================================== */

        div[data-testid="stDownloadButton"] > button {
            min-height: 42px !important;
        }


        /* ==================================================
           SELECTBOX
           ================================================== */

        div[data-testid="stSelectbox"] > div {
            min-height: 42px !important;
        }


        /* ==================================================
           REMOVE EXTRA SPACE AROUND FILTER
           ================================================== */

        div[data-testid="stHorizontalBlock"] {
            align-items: center !important;
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
        '<span class="j-chip">⚙ Threshold: &gt;85% High Impact</span>'
        '</div>'
    )

    layout.page_header(
        "",
        "teal",
        "Risk Ranking",
        "Ranked by Network Risk Score from graph cluster analysis — "
        "entities above 85% are auto-flagged for review.",
        right_html=right,
    )


    # ======================================================
    # PAGE LABEL
    # ======================================================

    st.markdown(
        """
        <div style="margin:-6px 0 14px 0;">
            <span class="j-pill teal">
                HIN Anomaly Prioritization
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        _all.to_csv(index=False).encode("utf-8"),
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
                <div class="j-card">
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
            "q",
            placeholder=(
                "Search Entity ID, Ring Name, Faskes…  ⌘K"
            ),
            label_visibility="collapsed",
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
                    label,
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

    rows = _filtered(
        RISK_CLUSTERS,
        chip,
        query,
    )


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
        """
        <div class="j-footer" style="margin-top:14px;">

            <div>
                ✅ Showing all prioritized clusters
                generated by Graph Engine v2.4
                Louvain partition
            </div>

            <div>
                Cycle ID: #2024Q3-LOUVAIN-08
                &nbsp;•&nbsp;
                Confidence Interval: 99.2%
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
            "Buka Claim Details",
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
            "Lihat Sub-Graph",
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
            df.to_csv(index=False).encode("utf-8"),
            file_name="jala_risk_ranking.csv",
            width="stretch",
        )


    # ======================================================
    # FOOTER
    # ======================================================

    layout.render_footer()