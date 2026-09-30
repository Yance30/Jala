import base64
from pathlib import Path

import streamlit as st

from data.mock_data import NAV_PAGES

# Ganti sesuai lokasi & nama file logo kamu (png / jpg / svg)
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.png"

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


@st.cache_data(show_spinner=False)
def _logo_data_uri(path_str: str) -> str:
    """Baca file logo lalu ubah jadi data URI (base64).

    Streamlit tidak bisa memuat file lokal lewat <img src="...">,
    jadi gambar harus di-embed sebagai base64.
    Return string kosong kalau file tidak ada (app tidak crash).
    """
    path = Path(path_str)
    if not path.exists():
        return ""

    mime = _MIME.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{encoded}"


def render_sidebar():
    """Render sidebar navigation and verifier information."""

    with st.sidebar:

        # =========================
        # BRAND
        # =========================
        logo_uri = _logo_data_uri(str(LOGO_PATH))

        logo_html = (
            f'<img src="{logo_uri}" alt="JALA logo" '
            'style="width:36px;height:36px;object-fit:contain;flex-shrink:0;" />'
            if logo_uri
            else ""
        )

        st.markdown(
            f"""
            <div class="j-brand" style="
                display:flex;
                align-items:center;
                gap:10px;
            ">
                {logo_html}

                <div>
                    <div style="
                        font-size:16px;
                        font-weight:600;
                        letter-spacing:-0.01em;
                        line-height:1.2;
                        color:#FFFFFF;
                    ">
                        JALA
                    </div>

                    <div style="
                        font-size:11px;
                        font-weight:500;
                        color:rgba(255,255,255,0.72);
                    ">
                        Fraud Analytics
                    </div>
                </div>
            </div>

            <div style="margin:12px 0 3.25rem 0;">
                <span class="j-pill">
                    Prototype / Proof of Concept
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # =========================
        # NAVIGATION
        # =========================
        labels = [label for _, label in NAV_PAGES]
        keys = [key for key, _ in NAV_PAGES]

        current = st.session_state.get("page", "dashboard")

        # Halaman lama "claim" diarahkan ke "risk"
        mapped = "risk" if current == "claim" else current
        index = keys.index(mapped) if mapped in keys else 0

        def _on_nav():
            selected_label = st.session_state.nav_radio

            if selected_label in labels:
                st.session_state.page = keys[labels.index(selected_label)]

            # Reset cluster ketika berpindah dari halaman risk
            if st.session_state.page != "risk":
                st.session_state.selected_cluster = None

        # Sinkronisasi radio dengan halaman aktif
        if st.session_state.get("nav_radio") != labels[index]:
            st.session_state["nav_radio"] = labels[index]

        st.radio(
            "Navigasi",
            labels,
            index=index,
            label_visibility="collapsed",
            key="nav_radio",
            on_change=_on_nav,
        )

        st.markdown(
            "<div style='height:2.25rem'></div>",
            unsafe_allow_html=True,
        )

        # =========================
        # VERIFIKATOR CARD
        # =========================
        st.markdown(
            """
            <div class="j-sidecard">

                <div style="
                    font-weight:600;
                    color:#FFFFFF;
                    display:flex;
                    align-items:center;
                ">
                    <span class="dot teal"></span>
                    BPJS VERIFIKATOR
                </div>

                <div style="margin-top:4px;">
                    PoC Node 04 · Aktif
                </div>

                <div>
                    Model GNN v2.4 (Sync OK)
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )