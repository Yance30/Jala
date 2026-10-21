"""Case summary, graph and timeline drawn exclusively from the selected batch."""
from html import escape
import json

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from core.case_context import build, evidence

COLORS = {"Klaim": "#B45309", "Peserta": "#0F766E", "Dokter": "#2563EB",
          "Faskes": "#7C3AED", "Diagnosis": "#64748B"}


def figure(context):
    graph = nx.Graph()
    graph.add_nodes_from(context["nodes"])
    graph.add_edges_from((a, b) for a, b, _ in context["edges"])
    positions = nx.spring_layout(graph, seed=2026)
    x, y = [], []
    for a, b, _ in context["edges"]:
        x.extend([positions[a][0], positions[b][0], None])
        y.extend([positions[a][1], positions[b][1], None])
    fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line=dict(color="#CBD5E1", width=1),
                              hoverinfo="skip", showlegend=False))
    for kind, color in COLORS.items():
        keys = [key for key in graph if key[0] == kind]
        fig.add_trace(go.Scatter(
            x=[positions[k][0] for k in keys], y=[positions[k][1] for k in keys],
            mode="markers", name=kind,
            marker=dict(color=color, size=[20 if k == ("Klaim", context["focus"]) else 10 for k in keys],
                        line=dict(color="white", width=1)),
            text=[f"{kind}: {escape(k[1])}" for k in keys], hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(height=420, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor="white",
                      plot_bgcolor="white", legend=dict(orientation="h"),
                      xaxis=dict(visible=False), yaxis=dict(visible=False), dragmode="pan")
    return fig


def render(queue, claim_id):
    context = build(queue["claims"], claim_id)
    related = context["related"]
    with st.expander("Telusuri jaringan & riwayat kasus", expanded=False):
        st.write(f"**{len(related)} klaim terkait · {related.patient_id.nunique()} peserta · "
                 f"{related.faskes_id.nunique()} faskes**")
        st.write(f"Total nilai klaim terkait: **Rp{context['total_tariff']:,.0f}** — bukan estimasi kerugian.")
        st.caption("Hubungan berdasarkan peserta, dokter layanan, atau dokter rujukan dalam ±30 hari. "
                   "Hanya batch ini; bukan seluruh riwayat peserta atau atribusi model.")
        graph_tab, timeline_tab, evidence_tab = st.tabs(["Graf hubungan", "Linimasa klaim", "Bahan pemeriksaan"])
        with graph_tab:
            st.plotly_chart(figure(context), key=f"context_graph_{queue['id']}_{claim_id}", width="stretch",
                            config={"displaylogo": False, "scrollZoom": False})
            st.caption("Arahkan kursor untuk melihat ID. Simpul klaim terpilih berukuran lebih besar. "
                       "Garis menghubungkan klaim dengan entitas yang tercatat; bukan bukti kolusi.")
            if context["omitted"]:
                st.info(f"Graf menampilkan {context['graph_claims']} klaim terdekat; "
                        f"{context['omitted']} klaim lain tetap tersedia pada linimasa dan unduhan.")
            if not context["referral_available"]:
                st.caption("Batch lama tidak menyimpan kolom rujukan. Kirim ulang hasil prediksi untuk melengkapinya.")
        with timeline_tab:
            st.dataframe(related[["visit_ts", "submit_ts", "claim_id", "patient_id", "doctor_id",
                                  "faskes_id", "icd", "tarif", "keterkaitan"]], hide_index=True)
            st.caption("Urutan waktu layanan (UTC). Kunjungan berulang dapat merupakan layanan yang sah.")
        with evidence_tab:
            st.write("Cocokkan tanggal layanan dan rujukan dengan dokumen pendukung; "
                     "periksa penjelasan klinis sebelum menyimpulkan adanya klaim tidak wajar.")
            st.download_button("Unduh bahan pemeriksaan kasus", json.dumps(evidence(queue, context),
                               ensure_ascii=False, indent=2), file_name="jala-case-evidence.json",
                               mime="application/json", key=f"context_export_{queue['id']}_{claim_id}")
