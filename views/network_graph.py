import streamlit as st
import streamlit.components.v1 as components

from components import bench, cards, charts, guide, layout
from data.mock_data import GRAPH_LEGEND_EDGES, GRAPH_LEGEND_NODES
from core.live import AUTO_FLAG
from core.privacy import mask_graph
from components.typology import label as typology_label


def render():
    live = bench.get_live()
    layout.page_header(
        "", "teal", "Peta Jaringan",
        "Peta hubungan antara fasilitas kesehatan, dokter, pasien, dan diagnosis dalam satu kelompok klaim. "
        "Kelompok dibentuk dari data sintetis untuk membantu peninjauan; hubungan yang tampak bukan bukti pelanggaran.",
        right_html=(
            '<div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">'
            '<span class="j-chip"><span class="dot amber"></span>Data sintetis · prototipe</span>'
            f'<span class="j-chip"><span class="ms">hub</span> Klaster dalam data: {len(live.clusters)}</span>'
            '<span class="j-chip"><span class="ms">schedule</span> Garis menunjukkan waktu kunjungan</span></div>'
        ),
    )
    guide.render_page_guide("network")
    guide.render_typology_glossary()
    st.markdown(
        '<div style="margin:4px 0 14px 0;"><span class="j-pill teal">Peta hubungan</span></div>',
        unsafe_allow_html=True,
    )

    if not live.clusters:
        st.info("Belum ada klaster yang memenuhi syarat untuk divisualisasikan pada data ini.")
        layout.render_footer()
        return

    with st.container(border=True):
        t1, t2, t3, t4 = st.columns([2, 1.4, 1.4, 1.6])
        with t1:
            query = st.text_input("Cari entitas", placeholder="Nama faskes, dokter, atau ID klaster")
        hit = live.find(query)
        if hit:
            st.session_state.selected_cluster = hit
        elif query:
            st.info("Tidak ada hasil untuk pencarian ini. Periksa kata kunci atau hapus pencarian.")
            layout.render_footer()
            return
        typos = ["Semua tipologi"] + sorted({c["typology"] for c in live.clusters})
        with t3:
            typo = st.selectbox("Tipologi", typos, index=0, format_func=typology_label)
        pool = ([live.by_id[hit]] if hit else
                [c for c in live.clusters if typo == typos[0] or c["typology"] == typo])
        if not pool:
            st.info("Tidak ada klaster untuk filter ini. Pilih tipologi lain atau hapus filter pencarian.")
            return
        with t2:
            ids = [c["id"] for c in pool]
            cur = st.session_state.get("selected_cluster")
            sel = st.selectbox("Pilih klaster", ids, index=ids.index(cur) if cur in ids else 0,
                               format_func=lambda i: f"{live.by_id[i]['score']}% · {live.by_id[i]['name']}")
            st.session_state.selected_cluster = sel
        with t4:
            # ikon Material (bukan glyph unicode) supaya selalu terlihat di HP
            with st.container(key="net_zoom"):
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("", icon=":material/refresh:", help="Atur ulang tampilan", key="z_reset", width="stretch"):
                    st.session_state.zoom = 1.0
                    st.session_state.isolate = False
                    st.rerun()
                if b2.button("", icon=":material/add:", help="Perbesar", key="z_in", width="stretch"):
                    st.session_state.zoom = min(1.6, st.session_state.get("zoom", 1.0) + 0.2)
                    st.rerun()
                if b3.button("", icon=":material/remove:", help="Perkecil", key="z_out", width="stretch"):
                    st.session_state.zoom = max(0.8, st.session_state.get("zoom", 1.0) - 0.2)
                    st.rerun()
                if b4.button("", icon=":material/fit_screen:", help="Pas ke layar", key="z_fit", width="stretch"):
                    st.session_state.zoom = 1.0
                    st.rerun()

    isolate = st.session_state.get("isolate", False)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Fokus pada klaster", icon=":material/center_focus_strong:", key="center"):
            st.session_state.isolate = not isolate
            st.rerun()
    with c2:
        st.caption(f"Klaster: {sel} · {typo}" + (f" · pencarian: “{query}”" + ("" if hit else " (tidak ditemukan)") if query else ""))
        if query and not hit:
            st.info("Tidak ada kecocokan. Coba ID klaster, nama faskes, atau ID entitas lain.")

    cl = live.by_id[sel]
    st.markdown(
        f"""
        <div class="j-alert-red" style="display:flex;gap:10px;align-items:flex-start;margin:6px 0 12px;">
          <span><span class="ms">warning</span></span>
          <div><b>PERINGATAN KLASTER #{cl['id']}</b>
            <span class="j-pill red-solid" style="margin-left:8px;">Skor prioritas {cl['score']}/100</span>
            <div style="margin-top:4px;">{cl['why']}</div>
            <div class="j-sub" style="margin-top:6px;">Skor membantu mengurutkan tinjauan; bukan probabilitas atau bukti kecurangan.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    zoom = st.session_state.get("zoom", 1.0)
    graph_data = live.graph(sel)
    if st.session_state.get("demo_role", "Verifikator") == "Verifikator":
        graph_data = (*mask_graph(graph_data[0], graph_data[1]), *graph_data[2:])
        st.caption("ID peserta disamarkan pada tampilan Verifikator (simulasi). Ini bukan kontrol akses produksi.")
    graph_html = charts.network_animated_html(graph_data, zoom=zoom, isolate=isolate)
    graph_h = int(620 * min(max(zoom, 0.8), 1.6))
    # container ber-key: di mobile kanvas dilebarkan (min-width) dan bisa digeser horizontal
    with st.container(key="network_chart"):
        if hasattr(st, "iframe"):  # Streamlit terbaru (components.v1.html sudah deprecated)
            st.iframe(graph_html, height=graph_h)
        else:  # Streamlit lama (mis. 1.57)
            components.html(graph_html, height=graph_h)

    l1, l2 = st.columns([1, 1])
    with l1:
        node_rows = "".join(
            f"""
            <div style="display:flex;align-items:center;gap:8px;background:#F8FAFC;border-radius:6px;
                        padding:6px 10px;margin-bottom:6px;">
              <span style="width:12px;height:12px;background:{color};display:inline-block;
                           border-radius:{ '9999px' if sym == 'circle' else ('0' if sym == 'square' else '2px')};
                           transform:{'rotate(45deg)' if sym == 'diamond' else 'none'};"></span>
              <span style="font-size:12.5px;">{label}</span>
            </div>
            """
            for label, sym, color in GRAPH_LEGEND_NODES
        )
        edge_rows = "".join(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;
                        padding:4px 2px;font-size:12.5px;">
              <span style="display:flex;align-items:center;gap:8px;">
                <span style="width:26px;border-top:2px {'solid' if s == 'solid' else ('dashed' if s == 'dash' else 'dotted')} #475569;"></span>
                {label}
              </span>
              <span class="j-sub">Berwaktu</span>
            </div>
            """
            for label, s in GRAPH_LEGEND_EDGES
        )
        st.markdown(
            f"""
            <div class="j-card">
              <div class="j-h2"><span class="ms">hub</span> Keterangan Grafik Jaringan</div>
              <div class="j-label" style="margin:10px 0 6px;">Jenis Simpul</div>
              {node_rows}
              <div class="j-label" style="margin:10px 0 6px;">Jenis Hubungan</div>
              {edge_rows}
              <div style="display:flex;gap:16px;margin-top:8px;font-size:12.5px;">
                <span><span class="dot teal"></span>Pembanding normal</span>
                <span style="color:#C2410C;"><span class="dot amber"></span>Anomali dugaan</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with l2:
        st.markdown(
            f"""
            <div class="j-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="j-h2"><span class="dot red"></span>Klaster #{cl['id']}</div>
                {cards.badge('SANGAT TINGGI' if cl['score'] >= 90 else ('TINGGI' if cl['score'] >= AUTO_FLAG else 'TINJAU'), 'red' if cl['score'] >= AUTO_FLAG else 'amber')}
              </div>
              <div class="j-sub" style="margin:4px 0 12px;">Ditandai oleh prototipe fitur graf (arsitektur target: HAN)</div>
              <div style="display:flex;gap:12px;">
                <div class="j-note" style="flex:1;flex-direction:column;gap:2px;">
                  <span class="j-label">Skor Prioritas</span>
                  <span class="j-value red" style="font-size:24px;">{cl['score']}/100</span>
                  <span class="j-sub">{cl['n']} klaim ditandai</span>
                </div>
                <div class="j-note" style="flex:1;flex-direction:column;gap:2px;">
                  <span class="j-label">Modularitas Louvain</span>
                  <span class="j-value dark" style="font-size:24px;">Q = {live.modularity:.2f}</span>
                  <span class="j-sub">Kepadatan klaster {cl['density']:.2f}</span>
                </div>
              </div>
              <div style="margin-top:12px;" class="j-sub">Dugaan tipologi:</div>
              <div style="font-size:13px;font-weight:600;"><span class="ms">swap_horiz</span> {cl['typology']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        if b1.button("Sorot subgraf", icon=":material/filter_alt:", width="stretch", key="iso"):
            st.session_state.isolate = not isolate
            st.rerun()
        if b2.button("Buka prioritas klaster", icon=":material/analytics:", width="stretch", key="go_risk"):
            layout.goto("risk", cluster=sel)
        if st.button("Tindak lanjut audit", icon=":material/gavel:", width="stretch", type="primary", key="go_audit"):
            layout.goto("audit", cluster=sel)

    layout.render_footer()
