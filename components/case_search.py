"""Pencarian kasus bersama yang tetap tersedia pada setiap halaman."""
import streamlit as st

from core.live import AUTO_FLAG

ALL_CASES = "Semua pola"
AUTO_CASES = f"Prioritas otomatis (≥{AUTO_FLAG}%)"


def filter_rows(rows: list[dict], query: str = "", filter_value: str = ALL_CASES) -> list[dict]:
    """Terapkan pencarian nama/ID/faskes dan kategori pada skema baris antrean."""
    q = (query or "").strip().casefold()
    out = []
    for row in rows:
        typology = row["typology"][0] if isinstance(row["typology"], tuple) else row["typology"]
        if filter_value == AUTO_CASES and row["score"] < AUTO_FLAG:
            continue
        if filter_value not in (ALL_CASES, AUTO_CASES) and typology != filter_value:
            continue
        searchable = " ".join(str(row.get(k, "")) for k in ("id", "name", "subtitle", "faskes", "nodes"))
        if q and q not in searchable.casefold():
            continue
        out.append(row)
    return out


def _clear_search() -> None:
    st.session_state["case_search_query"] = ""
    st.session_state["case_search_filter"] = ALL_CASES


def render_sidebar(live) -> None:
    """Render pencarian + filter klaster global dan pintasan ke detail kasus."""
    rows = live.risk_rows()
    typologies = sorted({r["typology"][0] for r in rows})
    options = [ALL_CASES, AUTO_CASES, *typologies]
    if st.session_state.get("case_search_filter") not in options:
        st.session_state["case_search_filter"] = ALL_CASES

    with st.expander("Cari & filter kasus", expanded=False):
        st.text_input(
            "Cari kasus",
            placeholder="ID, nama jaringan, atau faskes",
            key="case_search_query",
        )
        st.selectbox("Kategori kasus", options, key="case_search_filter")
        filtered = filter_rows(
            rows,
            st.session_state.get("case_search_query", ""),
            st.session_state.get("case_search_filter", ALL_CASES),
        )
        st.caption(f"{len(filtered)} dari {len(rows)} klaster cocok")
        if filtered:
            by_id = {row["id"]: row for row in filtered}
            ids = list(by_id)
            st.selectbox(
                "Pilih kasus",
                ids,
                format_func=lambda cid: f"{cid} · {by_id[cid]['name']} · {by_id[cid]['score']}%",
                key="case_search_result",
            )
            if st.button("Buka detail kasus", key="case_search_open", width="stretch"):
                from components import layout

                layout.goto("claim", cluster=st.session_state["case_search_result"])
        else:
            st.info("Tidak ada kasus yang cocok. Coba kata kunci atau kategori lain.")
        st.button("Hapus pencarian dan filter", key="case_search_clear", on_click=_clear_search, width="stretch")
