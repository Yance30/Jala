import streamlit as st
import numpy as np
from statistics import median

from components import bench, cards, charts, layout
from data.mock_data import COMPARISON


def _panel(side, tone):
    data = COMPARISON[side]
    points = "".join(
        f"""
        <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">
          <span style="color:{'#64748B' if side == 'legacy' else '#0F766E'};font-size:15px;">
            {'⊖' if side == 'legacy' else '✔'}</span>
          <span class="j-body" style="font-size:13px;">{p}</span>
        </div>
        """
        for p in data["points"]
    )
    card_cls = "j-card" if side == "legacy" else "j-card tealwash"
    icon = "📋" if side == "legacy" else "🕸"
    tag_cls = "j-pill grey" if side == "legacy" else "j-pill"
    tag_style = "" if side == "legacy" else ' style="background:#0F766E;color:#fff;"'
    diagram = (
        """
        <div class="j-cmp-diagram">
          <div style="display:flex;gap:14px;justify-content:center;padding:26px 0;">
            <div style="width:84px;height:96px;background:#E2E8F0;border-radius:4px;position:relative;">
              <div style="margin:14px 12px;height:4px;background:#94A3B8;border-radius:2px;"></div>
              <div style="margin:8px 12px;height:4px;background:#CBD5E1;border-radius:2px;"></div>
              <div style="margin:8px 12px;height:4px;background:#CBD5E1;border-radius:2px;"></div>
              <div style="position:absolute;right:8px;bottom:8px;color:#475569;">✓</div>
            </div>
            <div style="width:84px;height:96px;background:#E2E8F0;border-radius:4px;position:relative;">
              <div style="margin:14px 12px;height:4px;background:#94A3B8;border-radius:2px;"></div>
              <div style="margin:8px 12px;height:4px;background:#CBD5E1;border-radius:2px;"></div>
              <div style="position:absolute;right:8px;bottom:8px;color:#475569;">✓</div>
            </div>
            <div style="width:84px;height:96px;background:#E2E8F0;border-radius:4px;position:relative;">
              <div style="margin:14px 12px;height:4px;background:#94A3B8;border-radius:2px;"></div>
              <div style="margin:8px 12px;height:4px;background:#CBD5E1;border-radius:2px;"></div>
              <div style="position:absolute;right:8px;bottom:8px;color:#475569;">✓</div>
            </div>
          </div>
        </div>
        """
        if side == "legacy"
        else """
        <div class="j-cmp-diagram">
          <div style="padding:18px 0;text-align:center;">
            <svg width="260" height="150" viewBox="0 0 260 150">
              <line x1="130" y1="30" x2="40" y2="90" stroke="#0F766E" stroke-width="2"/>
              <line x1="130" y1="30" x2="220" y2="90" stroke="#0F766E" stroke-width="2"/>
              <line x1="40" y1="90" x2="220" y2="90" stroke="#94A3B8" stroke-width="1.5"/>
              <line x1="40" y1="90" x2="130" y2="128" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="4 3"/>
              <line x1="220" y1="90" x2="130" y2="128" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="4 3"/>
              <circle cx="130" cy="30" r="16" fill="#0F766E"/>
              <circle cx="40" cy="90" r="14" fill="#E6F4F2" stroke="#0F766E" stroke-width="2"/>
              <circle cx="220" cy="90" r="14" fill="#E6F4F2" stroke="#0F766E" stroke-width="2"/>
              <circle cx="130" cy="128" r="14" fill="#9A3412"/>
              <text x="130" y="34" text-anchor="middle" fill="#fff" font-size="9" font-family="Inter">FKRTL</text>
              <text x="40" y="93" text-anchor="middle" fill="#0F766E" font-size="8" font-family="Inter">Dokter</text>
              <text x="220" y="93" text-anchor="middle" fill="#0F766E" font-size="8" font-family="Inter">Pasien</text>
              <text x="130" y="131" text-anchor="middle" fill="#fff" font-size="8" font-family="Inter">ICD-10</text>
            </svg>
          </div>
        </div>
        """
    )
    return f"""
    <div class="{card_cls} j-cmp-card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span class="j-iconbox {'grey' if side == 'legacy' else 'teal'}" style="width:44px;height:44px;">{icon}</span>
        <span class="{tag_cls}"{tag_style}>{data['tag']}</span>
      </div>

      <div class="j-cmp-title j-h1" style="font-size:22px;margin:16px 0 6px;">{data['title']}</div>
      <div class="j-body j-cmp-sub">{data['sub']}</div>

      <div class="j-card {'tint' if side == 'legacy' else ''}" style="margin:16px 0;background:#FFFFFF;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="j-label">{data['panel_label']}</span>
          <span>{'🚫' if side == 'legacy' else '🕸'}</span>
        </div>

        {diagram}

        <div class="j-sub j-cmp-note">{data['panel_note']}</div>
      </div>

      <div class="j-cmp-points">
        {points}
      </div>

      <div class="j-cmp-foot" style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;
                  border-top:1px solid #E2E8F0;padding-top:12px;">
        <span class="j-label">Cakupan Audit</span>
        <b style="color:{'#475569' if side == 'legacy' else '#0F766E'};">{data['coverage']}</b>
      </div>
    </div>
    """


def render_content():
    st.markdown(
        """
        <div style="text-align:center;margin:8px 0 22px;">
          <span class="j-pill grey">ARSITEKTUR AUDIT FORENSIK KLAIM</span>
          <div class="j-h1" style="font-size:32px;margin:12px 0 8px;">Perbandingan Paradigma Deteksi
            Kecurangan</div>
          <div class="j-body" style="max-width:760px;margin:0 auto;">Transformasi analitik dari validasi
            dokumen silo menjadi pemetaan relasional multi-entitas secara terpadu.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(_panel("legacy", "grey"), unsafe_allow_html=True)
    with c2:
        st.markdown(_panel("han", "teal"), unsafe_allow_html=True)
    _evidence()
    _temporal_impact()
    _robustness()
    _human_error_scenarios()


def _human_error_scenarios():
    report = bench.get_error_dismissal_report()
    st.markdown("### Jika pola fraud keliru ditandai wajar")
    st.caption("Simulasi Monte Carlo 100 kali. Persentase salah adalah peluang klaster fraud yang ditinjau ikut ditandai wajar. "
               "Ini uji risiko pada label sintetis, bukan ukuran kesalahan petugas nyata.")
    cols = st.columns(3)
    cols[0].metric("Presisi antrean awal", f"{report['baseline_precision']:.1%}")
    for col, scenario in zip(cols[1:], report["scenarios"]):
        col.metric(f"Salah tandai wajar {scenario['error_rate']:.0%}",
                   f"{scenario['precision_mean']:.1%}",
                   f"rentang P10–P90: {scenario['precision_p10']:.1%}–{scenario['precision_p90']:.1%}")
    st.caption("Rata-rata klaster fraud yang skornya ikut turun: " + " · ".join(
        f"{s['error_rate']:.0%}: {s['fraud_clusters_demoted_mean']:.1f}"
        for s in report["scenarios"]))


def _temporal_impact():
    report = bench.get_temporal_impact()
    st.markdown("### Kapan cincin pertama kali tertangkap?")
    if not report:
        st.info("Replay mingguan belum dihitung. Jalankan `python -m core.temporal_impact` untuk membuat hasil sintetis.")
        return
    rings = report.get("rings", [])
    comparable = [r for r in rings if r.get("weeks_earlier") is not None]
    earlier = [r["weeks_earlier"] for r in comparable if r["weeks_earlier"] > 0]
    later = [r["weeks_earlier"] for r in comparable if r["weeks_earlier"] < 0]
    tied = [r["weeks_earlier"] for r in comparable if r["weeks_earlier"] == 0]
    st.caption(report["meta"]["caveat"] + " Kapasitas "
               f"{report['meta']['capacity_claims_per_week']} klaim per minggu.")
    result_cols = st.columns(3)
    result_cols[0].metric("JALA lebih awal", f"{len(earlier)} cincin")
    result_cols[1].metric("Minggu yang sama", f"{len(tied)} cincin")
    result_cols[2].metric("Aturan lebih awal", f"{len(later)} cincin")
    if earlier:
        st.caption(f"Saat JALA lebih awal, median selisihnya {median(earlier):.1f} minggu.")
    if rings:
        st.dataframe(rings, hide_index=True, use_container_width=True)


def _chart_card(title: str, sub: str, fig) -> None:
    """Keep the heading and chart adjacent in a scoped block, without negative margins."""
    panel_key = "chart_panel_" + "".join(
        char.lower() if char.isalnum() else "_" for char in title
    ).strip("_")
    with st.container(key=panel_key):
        st.markdown(
            f'<div class="j-card j-eqhead"><div class="j-h2" style="color:#0F766E;">{title}</div>'
            f'<div class="j-sub">{sub}</div></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _pct(v: float) -> str:
    return f"{v * 100:.0f}%" if v >= .095 else f"{v * 100:.1f}%"


def _evidence():
    m = bench.get_metrics()
    g, r, rnd = m["scorers"]["graph_gbm"], m["scorers"]["rules"], m["random"]
    go = m["graph_only_at_500"]
    st.markdown(
        f"""
        <div style="text-align:center;margin:34px 0 18px;">
          <span class="j-pill teal">BUKTI EVALUASI · DATA SINTETIS BERLABEL</span>
          <div class="j-h1" style="font-size:28px;margin:12px 0 8px;">Hasil terukur, bukan angka ketikan</div>
          <div class="j-body" style="max-width:820px;margin:0 auto;">Skor dihitung kode pada
            <b>{m['n_claims']:,}</b> klaim sintetis ({m['n_fraud']} fraud, {m['prevalence']:.1%}) dari
            {m['n_faskes']} faskes. Label hanya dipakai untuk menilai dan tidak pernah dibaca detektor.
            Validasi silang dilakukan per kelompok faskes, sehingga cincin yang sama tidak dipakai melatih
            sekaligus menguji.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    cards_data = [
        ("AUC-ROC", f"{g['auc']:.3f}", f"Aturan lama: {r['auc']:.3f} · Acak: 0.500", "teal"),
        ("FRAUD TERTANGKAP, 500 KLAIM DIPERIKSA", _pct(g["recall_at_k"][500]),
         f"Aturan: {_pct(r['recall_at_k'][500])} · Acak: {_pct(rnd['recall_at_k'][500])}", "teal"),
        ("PRESISI 250 TERATAS", _pct(g["precision_at_k"][250]),
         f"Aturan: {_pct(r['precision_at_k'][250])} · Acak: {_pct(rnd['precision_at_k'][250])}", "dark"),
        ("LOLOS ATURAN, TERTANGKAP JARINGAN", f"{go['of_which_missed_by_rules']}",
         f"klaim fraud di 500 teratas yang tidak disentuh aturan lama (dari {go['fraud_total_missed_by_rules']} yang lolos)", "dark"),
    ]
    for col, (label, value, note, tone) in zip(cols, cards_data):
        with col:
            st.markdown(cards.metric_card(label, value, note=note, value_tone=tone, label_lines=2), unsafe_allow_html=True)

    status_l, status_r = st.columns(2)
    with status_l:
        st.markdown(
            '<div class="j-card tealwash"><div class="j-label">Evaluasi prototipe</div>'
            '<div class="j-h2" style="margin:5px 0;">Data sintetis · validasi silang per kelompok faskes</div>'
            '<div class="j-sub">Setiap skor uji berasal dari model yang tidak dilatih pada kelompok faskes tersebut. '
            'Baseline aturan adalah pembanding sederhana yang kami definisikan, bukan sistem BPJS.</div></div>',
            unsafe_allow_html=True,
        )
    with status_r:
        st.markdown(
            '<div class="j-card"><div class="j-label">Evaluasi dunia nyata</div>'
            '<div class="j-h2" style="margin:5px 0;">Belum tersedia</div>'
            '<div class="j-sub">Belum ada hasil pada data klaim nyata atau label verifikasi nyata. '
            'Karena itu angka di halaman ini tidak menyatakan akurasi operasional BPJS.</div></div>',
            unsafe_allow_html=True,
        )
    st.caption(
        "Cara membaca metrik: AUC-ROC mengukur kemampuan mengurutkan pasangan positif dan negatif; "
        "Average Precision merangkum presisi sepanjang urutan; Recall@500 adalah bagian dari seluruh klaim fraud "
        "sintetis yang masuk 500 prioritas teratas. Precision@k bergantung pada prevalensi fraud yang ditentukan pembangkit."
    )

    impact = bench.get_temporal_impact()
    if impact:
        weekly_capacity = st.slider(
            "Kapasitas verifikator (klaim per minggu)", min_value=10,
            max_value=85, value=35, step=5,
            help="Antrean setiap minggu berisi klaim baru pada replay sintetis; angka bukan hasil operasional.",
            key="capacity_claims_per_week",
        )
        grid = impact["capacity_grid"]

        def total_hits(key: str) -> int:
            total = 0.0
            for week in impact["weekly"]:
                curve = week["capacity_curve"][key]
                total += float(np.interp(weekly_capacity, grid, curve))
            return round(total)

        hits_jala = total_hits("fraud_caught_jala")
        hits_rules = total_hits("fraud_caught_rules")
        total_fraud = sum(w["n_fraud"] for w in impact["weekly"])
        cap_cols = st.columns(2)
        with cap_cols[0]:
            st.metric("Fraud sintetis tertangkap · JALA", f"{hits_jala} klaim",
                      f"{hits_jala / total_fraud:.1%} dari fraud")
        with cap_cols[1]:
            st.metric("Fraud sintetis tertangkap · aturan", f"{hits_rules} klaim",
                      f"{hits_rules / total_fraud:.1%} dari fraud")
        _chart_card("Simulasi kapasitas audit mingguan",
                    "Setiap minggu memeringkat klaim baru; jumlah tangkapan dijumlahkan sepanjang 14 minggu.",
                    charts.weekly_replay_capacity_chart(impact, weekly_capacity))
    else:
        st.info("Jalankan `python -m core.temporal_impact` untuk membuat replay mingguan dan simulator kapasitasnya.")

    fairness = m.get("fairness_synthetic")
    if fairness:
        st.markdown("### Audit kesalahan tandai per kelompok · data sintetis")
        st.caption(f"Tingkat klaim sah yang melewati ambang skor {fairness['threshold']:.1f}. "
                   f"{fairness['caveat']} Kelompok kecil dapat menghasilkan angka yang tidak stabil.")
        fair_cols = st.columns(2)
        fair_cols[0].caption("Menurut tipe faskes")
        fair_cols[0].dataframe(fairness["by_type"], hide_index=True, use_container_width=True)
        fair_cols[1].caption("Menurut wilayah sintetis")
        fair_cols[1].dataframe(fairness["by_region"], hide_index=True, use_container_width=True)

    rows = ""
    names = {"phantom": "Phantom Billing (Klaim Palsu)", "repeat": "Repeat Billing",
             "selfref": "Rujukan tidak sesuai (Self-referral)"}
    for t, v in m["per_typology"].items():
        rows += (
            f'<tr><td>{names[t]}</td><td style="text-align:right;">{v["n"]}</td>'
            f'<td style="text-align:right;">{v["rules"]["auc"]:.3f}</td>'
            f'<td style="text-align:right;">{v["iforest"]["auc"]:.3f}</td>'
            f'<td style="text-align:right;color:#0F766E;font-weight:600;">{v["graph_gbm"]["auc"]:.3f}</td>'
            f'<td style="text-align:right;">{v["graph_gbm"]["ap"]:.2f}</td></tr>'
        )
    caveats = "".join(f'<li style="margin-bottom:6px;">{c}</li>' for c in m["caveats"])
    left, right = st.columns([3, 2])
    with left:
        st.markdown(
            f"""
            <div class="j-card">
              <div class="j-h2">Per tipologi (tipologi itu vs klaim sah)</div>
              <div class="j-inline-table-wrap"><table class="j-inline-table">
                <thead><tr style="text-align:right;color:#64748B;">
                  <th style="text-align:left;">Tipologi</th><th>Klaim fraud</th><th>AUC aturan</th>
                  <th>AUC Isolation Forest (tanpa label)</th><th>AUC JALA</th><th>AP JALA</th></tr></thead>
                <tbody>{rows}</tbody>
              </table></div>
              <div class="j-sub" style="margin-top:10px;">Tingkat faskes: AUC {m['faskes_level']['auc']:.2f};
                {int(m['faskes_level']['precision_at_10'] * 10)} dari 10 faskes berisiko tertinggi memang faskes
                fraud ({m['faskes_level']['n_fraud_faskes']} dari {m['n_faskes']} faskes).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="j-card tealwash">
              <div class="j-h2">Batasan yang perlu dibaca</div>
              <ul class="j-body" style="font-size:12.5px;padding-left:18px;margin-top:8px;">{caveats}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _robustness():
    rob = bench.get_robustness()
    if not rob:
        st.info("Hasil uji ketahanan belum ada. Jalankan `python -m core.robustness --json docs/robustness.json`.")
        return
    meta, ab, tr = rob["meta"], rob["ablation"]["bertahap"], rob["transfer"]
    ev0, ev1 = rob["evasion"][0], rob["evasion"][-1]
    fp, rep = rob["false_positives"], rob["repeat_before_after"]
    names = list(ab)
    selfref_wo, selfref_with = ab[names[1]]["per_typology"]["selfref"]["ap"], ab[names[2]]["per_typology"]["selfref"]["ap"]

    st.markdown(
        f"""
        <div style="text-align:center;margin:40px 0 18px;">
          <span class="j-pill teal">UJI KETAHANAN · MENJAWAB "FRAUD-NYA DISISIPKAN SENDIRI"</span>
          <div class="j-h1" style="font-size:28px;margin:12px 0 8px;">Apakah jaringan benar-benar menambah nilai?</div>
          <div class="j-body" style="max-width:860px;margin:0 auto;">Lima pemeriksaan tambahan, semuanya dihitung kode:
            ablasi fitur, transfer ke dunia yang distribusinya bergeser, fraud yang sengaja menghindar, analisis klaim sah
            yang salah ditandai, dan perbaikan Repeat Billing. Dunia B dan fraud menghindar tetap dibuat oleh keluarga
            pembangkit yang sama, jadi ini menguji ketahanan terhadap pergeseran parameter, bukan akurasi di data nyata.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    cards_data = [
        ("TRANSFER KE DUNIA B, TANPA DILATIH ULANG", f"{tr['A_ke_B']['jala_transfer']['auc']:.3f}",
         f"AUC. Aturan lama: {tr['A_ke_B']['rules']['auc']:.3f} · seed, ukuran cincin, jam kirim, domisili, selisih tarif berbeda", "teal"),
        ("FRAUD PALING MENGHINDAR (TINGKAT 1,0)", _pct(ev1["model_beku"]["r_precision"]),
         f"tertangkap tanpa pembaruan model (dunia utama: {_pct(ev0['model_beku']['r_precision'])}) · dilatih ulang: "
         f"{_pct(ev1['model_dilatih_ulang']['r_precision'])} · aturan lama: {_pct(ev1['rules']['r_precision'])}", "dark"),
        ("SELF-REFERRAL TANPA RELASI MULTI-ENTITAS", f"AP {selfref_wo:.2f}",
         f"naik menjadi {selfref_with:.2f} dengan relasi multi-entitas (dokter-faskes-rujukan)", "teal"),
        (f"SALAH TANDAI DI {fp['k']} TERATAS", f"{fp['sah_di_top_k']}",
         f"klaim sah dari {fp['k']} ({fp['sah_di_top_k'] / fp['k']:.1%}); {fp['fraud_di_top_k']} adalah fraud", "dark"),
    ]
    for col, (label, value, note, tone) in zip(cols, cards_data):
        with col:
            st.markdown(cards.metric_card(label, value, note=note, value_tone=tone, label_lines=2), unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        _chart_card("Ablasi: dari mana nilai tambahnya?",
                    "Average precision per tipologi. Agregat entitas (jumlah klaim dan faskes per peserta/dokter) "
                    "setara derajat node, fitur graf paling murah. Relasi multi-entitas butuh catatan entitas lain.",
                    charts.ablation_chart(rob))
    with right:
        _chart_card("Fraud yang sengaja menghindar",
                    "Tingkat naik = kiriman dipecah, kunjungan disebar, peserta fiktif setempat dan lebih banyak, "
                    "dokter tak lagi lintas faskes, klaim ulang lebih renggang, tarif di bawah plafon.",
                    charts.evasion_chart(rob))

    rows = "".join(
        f'<tr><td>{k}</td><td style="text-align:right;">{v["n"]:,}</td>'
        f'<td style="text-align:right;">{v["salah_ditandai"]}</td><td style="text-align:right;">{v["fp_rate"]:.1%}</td></tr>'
        for k, v in [(k, v) for k, v in fp["per_jenis_sah"].items() if not k.startswith("(")][:5]
    )
    per = fp["per_jenis_sah"]
    plain = next((v["salah_ditandai"] for k, v in per.items() if k.startswith("(")), 0)
    clean = [lbl for key, lbl in (("batch_malam_rs", "batch malam RS"), ("dokter_dua_praktik", "dokter dua tempat praktik"),
                                  ("dokter_daerah", "dokter daerah")) if per.get(key, {}).get("salah_ditandai", 1) == 0]
    clean_txt = (", ".join(clean) + " tidak ditandai sama sekali; ") if clean else ""
    ms = rep["multi_seed"]["mean"]
    one = rep["v1_19_fitur"]["dunia_utama_cv"]["per_typology"]["repeat"]["ap"], rep["v2_22_fitur"]["dunia_utama_cv"]["per_typology"]["repeat"]["ap"]
    trf = rep["v1_19_fitur"]["transfer_A_ke_B"]["per_typology"]["repeat"]["ap"], rep["v2_22_fitur"]["transfer_A_ke_B"]["per_typology"]["repeat"]["ap"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="j-card">
              <div class="j-h2">Klaim sah yang paling sering salah ditandai</div>
              <div class="j-inline-table-wrap"><table class="j-inline-table">
                <thead><tr style="text-align:right;color:#64748B;"><th style="text-align:left;">Jenis klaim sah</th>
                  <th>Jumlah</th><th>Ditandai</th><th>Tingkat</th></tr></thead><tbody>{rows}</tbody>
              </table></div>
              <div class="j-sub" style="margin-top:10px;">Di {fp['k']} teratas: {clean_txt}{plain} klaim sah biasa
                ikut tertandai. Dialisis dan kunjungan ulang UGD paling rawan karena pola waktunya mirip klaim berulang.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="j-card">
              <div class="j-h2">Perbaikan Repeat Billing (titik terlemah)</div>
              <div class="j-body" style="font-size:13px;margin-top:8px;">Tiga fitur ditambahkan (selisih tarif, pasangan faskes
                yang saling menagih ulang, intensitas per faskes). Average precision Repeat Billing:</div>
              <div class="j-inline-table-wrap"><table class="j-inline-table">
                <thead><tr style="text-align:right;color:#64748B;"><th style="text-align:left;">Ukuran</th><th>19 fitur</th><th>22 fitur</th></tr></thead>
                <tbody>
                  <tr><td>Rata-rata 5 dunia (seed 1-5)</td><td style="text-align:right;">{ms['v1']['ap_repeat']:.2f}</td><td style="text-align:right;color:#0F766E;font-weight:600;">{ms['v2']['ap_repeat']:.2f}</td></tr>
                  <tr><td>Transfer dunia A ke B</td><td style="text-align:right;">{trf[0]:.2f}</td><td style="text-align:right;color:#0F766E;font-weight:600;">{trf[1]:.2f}</td></tr>
                  <tr><td>Dunia utama saja (seed 2026)</td><td style="text-align:right;">{one[0]:.2f}</td><td style="text-align:right;">{one[1]:.2f}</td></tr>
                </tbody>
              </table></div>
              <div class="j-sub" style="margin-top:10px;">Di seed 2026 sendiri tidak ada perbaikan; hasilnya baru terlihat
                lintas seed dan lintas dunia. Fitur dirancang setelah melihat pembangkit, jadi anggap peningkatan ini optimistis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    caveats = "".join(f'<li style="margin-bottom:6px;">{c}</li>' for c in rob["caveats"])
    st.markdown(
        f"""
        <div class="j-card tealwash" style="margin-top:16px;">
          <div class="j-h2">Batasan uji ketahanan</div>
          <ul class="j-body" style="font-size:12.5px;padding-left:18px;margin-top:8px;">{caveats}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
