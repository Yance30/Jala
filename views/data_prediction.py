"""Guided entry point for batch data and prediction."""
import streamlit as st

from components import external_lab, layout


def render():
    layout.page_header("Ruang kerja", "teal", "Data & Prediksi",
                       "Siapkan data, periksa kelengkapannya, lalu susun prioritas pemeriksaan.")
    from components.data_management import render as data_management
    data_management()
    external_lab.render(expanded=True)
