import pandas as pd
import streamlit as st

from components import cards, layout, tables
from data.mock_data import AUDIT_ACTIONS, AUDIT_CLUSTER, AUDIT_FASKES, AUDIT_TEMPLATES


@st.dialog("Konfirmasi Otorisasi — Penangguhan Pembayaran Klaim")
def _confirm_freeze():
    st.markdown(
        """
        <div class="j-body">Anda akan menerbitkan instruksi penangguhan pencairan dana terhadap
        <b>412 klaim</b> senilai <b>Rp 1.48 Miliar</b> pada <b>5 Faskes</b> terkait.</div>
        <div class="j-label" style="margin:14px 0 6px;">Tindakan Ini Akan Menghasilkan:</div>
        """,
        unsafe_allow_html=True,
    )
    for item in [
        "Pemblokiran otomatis nomor SEP terkait di sistem e-Klaim INA-CBG",
        "Notifikasi resmi otomatis ke Kantor Cabang pengampu faskes",
        "Pembuatan draft Berita Acara Pemeriksaan Khusus (BAPK-01)",
    ]:
        st.markdown(f'<div style="font-size:13px;margin-bottom:6px;">• {item}</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Batal", width="stretch"):
        st.rerun()
    if c2.button("✔ Konfirmasi & Tandatangani", width="stretch", type="primary"):
        st.session_state.audit_log.append("FREEZE dieksekusi & ditandatangani (BAPK-01 draft dibuat).")
        st.rerun()


def render():
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="j-pill teal">HUMAN-IN-THE-LOOP TRIAGE · PROTOKOL AKSI VERIFIKATOR</span>
          <span class="j-sub">REF: AUD-ACT-2024-0921</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    layout.page_header(
        "", "teal", "Audit Action & Verifikasi Klaster",
        "Penetapan tindakan operasional investigasi lanjutan terhadap klaster sindikat anomali yang "
        "terdeteksi oleh Heterogeneous Graph Attention Network (HAN).",
        right_html=(
            '<div style="display:flex;gap:8px;">'
            '<span class="j-chip">✅ Tingkat Otomatisasi: <b>Triage L3</b></span>'
            '<span class="j-chip">⏳ SLA Respon: <b style="color:#C2410C;">03:42:15</b></span></div>'
        ),
    )

    a = AUDIT_CLUSTER
    st.markdown(
        f"""
        <div class="j-card" style="border-left:4px solid #DC2626;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
            <div>
              <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <span class="j-iconbox red">✳</span>
                <b style="font-size:18px;">{a['name']}</b>
                {cards.badge(a['flag'], 'red')}
                {cards.badge(*a['typology'])}
              </div>
              <div class="j-sub" style="margin-top:6px;">🧠 {a['algo']}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <div style="width:56px;height:56px;border-radius:9999px;border:3px solid #DC2626;color:#DC2626;
                          display:flex;align-items:center;justify-content:center;font-weight:700;">{a['score']}%</div>
              <div>
                <div class="j-label">Network Risk Score</div>
                <div style="color:#DC2626;font-weight:600;font-size:13px;">{a['score_note']}</div>
              </div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px;">
            {''.join(
                f'<div class="j-card tint" style="padding:12px;"><div class="j-label">{label}</div>'
                f'<div style="font-weight:600;margin:4px 0 2px;color:{ {"dark": "#132A1C", "red": "#DC2626", "teal": "#0F766E"}[tone] };">'
                f'{value}</div><div class="j-sub">{note}</div></div>'
                for label, value, note, tone in a['cards'])}
          </div>
          <div class="j-note" style="margin-top:14px;align-items:flex-start;">
            <span>ⓘ</span>
            <div>
              <b>Ringkasan Bukti Forensik Algoritma:</b>
              <div style="margin-top:4px;">{a['evidence']}</div>
            </div>
          </div>
          <div style="display:flex;justify-content:flex-end;margin-top:10px;">
            <span class="j-chip">🕸 {a['density']} &nbsp;·&nbsp; Buka Network Graph ⧉</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka Network Graph ⧉", key="open_graph"):
        layout.goto("network")

    st.markdown(
        """
        <div class="j-alert-teal" style="margin:14px 0;">
          <b>🛡 KETENTUAN &amp; TATA KELOLA KEPUTUSAN</b>
          <span class="j-pill grey" style="margin-left:8px;">Standard BPJS 2024</span>
          <div style="margin-top:8px;font-weight:600;color:#132A1C;">"JALA provides a priority recommendation
            only. Final decision remains with the Verifikator team."</div>
          <div style="margin-top:6px;color:#475569;">Sistem JALA hanya menyediakan rekomendasi prioritas
            berbasis model graf. Keputusan final dan kewenangan eksekusi sepenuhnya berada pada Tim
            Verifikator BPJS Kesehatan sesuai regulasi BAPK (Berita Acara Pemeriksaan Khusus).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:18px 0 10px;">
          <div>
            <div class="j-h2">Pilih Tindakan Operasional (Operational Action)</div>
            <div class="j-sub">Tentukan satu langkah hukum dan verifikasi yang sah untuk diaplikasikan
              langsung pada klaster ini.</div>
          </div>
          <span class="j-pill grey">3 Opsi Tersedia</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for col, act in zip(cols, AUDIT_ACTIONS):
        with col:
            st.markdown(
                f"""
                <div class="j-card" style="height:calc(100% - 60px);">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="j-iconbox {act['icon_tone']}" style="width:42px;height:42px;">{act['icon']}</span>
                    {cards.badge(*act['tag'])}
                  </div>
                  <div style="font-size:16px;font-weight:600;margin:12px 0 6px;">{act['title']}</div>
                  <div class="j-body" style="font-size:12.5px;">{act['body']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(act["button"], width="stretch",
                         type="primary" if act["button_kind"] == "primary" else "secondary",
                         key=f"act_{act['title']}"):
                if act["button_kind"] == "primary":
                    _confirm_freeze()
                else:
                    st.session_state.audit_log.append(f"{act['title']} dijadwalkan.")
                    st.toast(f"{act['title']} — tercatat di audit trail.", icon="✅")
            st.markdown(f'<div class="j-sub" style="text-align:center;margin-top:6px;">{act["note"]}</div>',
                        unsafe_allow_html=True)

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    l, r = st.columns([3, 2])
    with l:
        st.markdown(
            """
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div class="j-h2">🕸 5 Faskes dalam Klaster HAN-089</div>
              <span class="j-sub">Terfilter: 5 Titik Simpul</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(tables.audit_faskes_html(AUDIT_FASKES), unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        df = pd.DataFrame(AUDIT_FASKES, columns=["kode", "wilayah", "tipe", "peran", "vol", "nilai"])
        c1, c2 = st.columns([1, 1])
        c1.markdown('<div class="j-sub">Showing 5 of 5 linked health facilities</div>', unsafe_allow_html=True)
        c2.download_button("⬇ Ekspor Daftar Entitas (.CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name="jala_han089_faskes.csv", width="stretch")
    with r:
        st.markdown(
            """
            <div class="j-h2">✎ Catatan Verifikator</div>
            <div class="j-sub" style="margin:4px 0 10px;">Tambahkan justifikasi forensik sebelum menekan
              tombol tindakan untuk dilampirkan dalam draft BAPK elektronik.</div>
            """,
            unsafe_allow_html=True,
        )
        note = st.text_area("catatan", placeholder="Tuliskan catatan pertimbangan hukum atau indikasi "
                                                    "lapangan di sini…", label_visibility="collapsed",
                            height=120, key="note_draft")
        chips = st.columns(len(AUDIT_TEMPLATES) + 1)
        chips[0].markdown('<div class="j-sub" style="padding-top:6px;">Template Cepat:</div>',
                          unsafe_allow_html=True)
        for col, tpl in zip(chips[1:], AUDIT_TEMPLATES):
            with col:
                if st.button(tpl, key=f"tpl_{tpl}", width="stretch"):
                    st.session_state.note_draft = (
                        f"[{tpl}] " + st.session_state.get("note_draft", "")
                    )
                    st.rerun()
        st.markdown(
            """
            <div class="j-card tint" style="margin-top:14px;">
              <div style="font-weight:600;color:#0F766E;font-size:13px;">🔐 Digital Signature Verification</div>
              <div class="j-sub" style="margin-top:6px;">Petugas: Auditor Forensik (NPP: 948210)<br>
                Sertifikat Kunci Publik: BPJS-ID-RSA-4096-VALID</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="j-footer" style="margin-top:18px;">
          <div>🕐 Setiap tindakan akan dicatat ke dalam audit trail sistem dan terintegrasi otomatis dengan
            <b>Berita Acara Pemeriksaan Khusus (BAPK) BPJS Kesehatan</b>.</div>
          <div>HASH: 8f7e2a991c4d</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Lihat Riwayat Log →"):
        log = st.session_state.get("audit_log", [])
        if log:
            for entry in log:
                st.markdown(f"- {entry}")
        else:
            st.caption("Belum ada tindakan tercatat pada sesi ini.")

    layout.render_footer()
