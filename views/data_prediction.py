"""Guided entry point for batch data and prediction."""
import streamlit as st

from components import external_lab, layout


def render():
    layout.page_header("Ruang kerja", "teal", "Data & Prediksi",
                       "Siapkan data, periksa kelengkapannya, lalu susun prioritas pemeriksaan.")
    from components.data_management import render as data_management
    data_management()
    external_lab.render(expanded=True)

    # Run after the target headings are rendered. Keep navigation inside this
    # Streamlit session so uploaded data, prediction results and queues survive.
    anchor = st.session_state.pop("batch_navigation_anchor", None)
    if anchor in ("siapkan-data", "validasi-paket", "jalankan-prediksi"):
        if anchor == "jalankan-prediksi" and st.session_state.get("external_dataset") is None:
            anchor = "siapkan-data"
            st.info("Siapkan dan validasi paket terlebih dahulu untuk membuka prediksi.")
        from components.batch_navigation import scroll_to_section
        scroll_to_section(anchor)
