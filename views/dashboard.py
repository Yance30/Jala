from html import escape

import streamlit as st

from components import bench, cards, charts, guide, layout
from core.evaluate import N_FOLDS
from core.live import AUTO_FLAG, THRESH
from data.mock_data import QUARTER
from core.synthetic import SEED

# Kode diagnosis dialisis terjadwal; klaim berulang di sini sah secara klinis,
# sehingga dipakai sebagai contoh "pola mirip fraud padahal layanan terjadwal".
_DIALYSIS_ICD = "N18.6"


def _find_contrast_cluster(live):
    """Pilih klaster yang paling didominasi klaim dialisis terjadwal.

    Menggantikan ID klaster hardcoded agar tetap benar bila seed/data berubah.
    Return (cluster, claims, dialysis_share) atau None bila tidak ada klaim N18.6.
    """
    best = None
    best_share = 0.0
    for cluster in live.clusters:
        claims = live.flagged.loc[cluster["idx"]]
        if not len(claims):
            continue
        share = float((claims.icd == _DIALYSIS_ICD).mean())
        if share > best_share:
            best_share = share
            best = (cluster, claims, share)
    return best


def render():
    live = bench.get_live()
    col_sel, col_sync = st.columns([3, 1])
    with col_sel:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;">
              <span class="j-pill teal">Ringkasan pengawasan</span>
              <span class="j-sub"><span class="dot teal"></span>Lingkungan simulasi verifikator</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_sync:
        st.markdown(
            '<div style="display:flex;justify-content:flex-end;gap:6px;flex-wrap:wrap;">'
            '<span class="j-chip"><span class="dot amber"></span>Data sintetis · prototipe</span>'
            f'<span class="j-chip">Periode data: <b>{QUARTER}</b></span></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
        <div class="j-h1 j-dashboard-title">Ringkasan Prioritas Pemeriksaan</div>
        <div class="j-body" style="max-width:860px;">Ringkasan klaim yang perlu diperhatikan. Versi ini adalah prototipe yang memakai data buatan; rancangan akhirnya memakai model jaringan graf (HAN).</div>
        <div class="j-sub" style="margin-top:6px;">Semua angka dihitung dari skor prototipe pada data buatan; klaim masuk tinjauan awal bila skornya {THRESH:.0%} atau lebih. Ukuran evaluasi dan batasannya ada di halaman About.</div>
        <div style="height:10px"></div>
        """,
        unsafe_allow_html=True,
    )
    guide.render_page_guide("dashboard")
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # Satu kasus teratas menjadi pintu masuk demo; data tetap berasal dari klaster hasil model.
    featured = live.clusters[0] if live.clusters else None
    if featured:
        first_evidence = featured["evidence"][0][2] if featured["evidence"] else featured["why"]
        st.markdown(
            f'<div class="j-card j-demo-case"><div class="j-demo-case-copy">'
            f'<span class="j-pill amber">KASUS DEMO · DATA SINTETIS</span>'
            f'<div class="j-h2">Mulai dari {escape(featured["name"])}</div>'
            f'<div class="j-sub">{featured["n"]} klaim terkait · dugaan {escape(featured["typology"])} · '
            f'skor prioritas {featured["score"]}/100</div>'
            f'<div class="j-demo-evidence">{escape(first_evidence)}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        start_col, reset_col = st.columns([1.5, 1])
        with start_col:
            if st.button("Mulai tinjau kasus", type="primary", icon=":material/arrow_forward:",
                         key="dashboard_start_review", width="stretch"):
                layout.goto("claim", cluster=featured["id"])
        with reset_col:
            st.button("Reset demo", key="dashboard_reset", width="stretch",
                      help="Pulihkan status demo. Riwayat audit lokal tetap tersimpan.",
                      on_click=bench.reset_demo)
        st.caption("Alur demo: telusuri alasan → periksa klaim sumber → catat tindak lanjut. Skor hanya menentukan prioritas.")

    # Kasus kontras mengingatkan bahwa pola statistik serupa juga dapat muncul pada layanan terjadwal.
    contrast_match = _find_contrast_cluster(live)
    if contrast_match:
        contrast, contrast_claims, dialysis_share = contrast_match
        st.markdown(
            f'<div class="j-card j-demo-case j-demo-caution">'
            f'<span class="j-pill teal">KASUS PEMBANDING · DATA SINTETIS</span>'
            f'<div class="j-h2">{escape(contrast["name"])}</div>'
            f'<div class="j-sub">Dugaan {escape(contrast["typology"])} · {contrast["n"]} klaim terkait · '
            f'skor prioritas {contrast["score"]}/100</div>'
            f'<div class="j-demo-evidence">{dialysis_share:.0%} klaim terkait memakai kode diagnosis N18.6. '
            'Klaim berulang dapat mengikuti jadwal layanan yang sah; periksa konteks klinis sebelum menyimpulkan.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Buka kasus pembanding", key="dashboard_open_contrast", width="stretch"):
            layout.goto("claim", cluster=contrast["id"])

    with st.expander("Asal data dan cara menghitung skor"):
        started = live.df.visit_ts.min()
        ended = live.df.visit_ts.max()
        details = st.columns(3)
        with details[0]:
            st.markdown(
                f'<div class="j-card"><div class="j-label">Sumber data</div>'
                f'<div class="j-h2">Data sintetis</div><div class="j-sub">Seed {SEED} · '
                f'{len(live.df):,} klaim · {len(live.world.faskes)} faskes</div></div>',
                unsafe_allow_html=True,
            )
        with details[1]:
            st.markdown(
                f'<div class="j-card"><div class="j-label">Periode simulasi</div>'
                f'<div class="j-h2">{started:%d %b} – {ended:%d %b %Y}</div>'
                f'<div class="j-sub">Periode tampilan: {QUARTER}</div></div>',
                unsafe_allow_html=True,
            )
        with details[2]:
            st.markdown(
                f'<div class="j-card"><div class="j-label">Metode prototipe</div>'
                f'<div class="j-h2">Fitur graf + gradient boosting</div>'
                f'<div class="j-sub">Validasi silang {N_FOLDS}-fold per kelompok faskes</div></div>',
                unsafe_allow_html=True,
            )
        st.caption(
            f"Klaim masuk penandaan mulai skor {THRESH:.0%}; klaster {AUTO_FLAG}% ke atas diprioritaskan. "
            "Skor adalah urutan pemeriksaan, bukan probabilitas atau bukti. Evaluasi dunia nyata belum tersedia; "
            "arsitektur HAN masih rancangan."
        )

    cols = st.columns(3)
    for col, kpi in zip(cols, live.kpis()):
        with col:
            st.markdown(
                cards.metric_card(
                    kpi["label"].upper(),
                    kpi["value"],
                    badge_html=cards.badge(*kpi["badge"]),
                    note=kpi["note"],
                    icon=kpi["icon"],
                ),
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    with st.container(key="chart_panel_dashboard_trend"):
        st.markdown(
            """
            <div class="j-card j-eqhead">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div class="j-h2" style="color:#0F766E;">Tren klaim ditandai per jenis dugaan
                    (per minggu kunjungan)</div>
                  <div class="j-sub">Jumlah klaim ditandai per minggu menurut dugaan jenis kecurangan; W13 hanya sisa hari periode</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        weeks, series = live.trend()
        st.plotly_chart(
            charts.trend_chart(weeks, series),
            width="stretch",
            config={"displayModeBar": False},
        )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, item in zip(cols, live.dashboard_footer()):
        with col:
            tone = "red" if item["tone"] == "red" else "dark"
            extra = f' <span style="color:#C2410C;font-size:12px;">{item["extra"]}</span>' if item.get("extra") else ""
            st.markdown(
                f"""
                <div class="j-dashboard-summary-item" style="display:flex;gap:12px;align-items:center;">
                  <span class="j-iconbox {'red' if item['tone'] == 'red' else 'grey'}">{item['icon']}</span>
                  <div>
                    <div class="j-label">{item['label']}</div>
                    <div class="j-value {tone}" style="font-size:16px;font-weight:600;margin-top:2px;">
                      {item['value']}{extra}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    layout.render_footer()
