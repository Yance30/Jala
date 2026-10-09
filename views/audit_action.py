import html

import pandas as pd
import streamlit as st

from components import bench, cards, export_context, guide, layout, tables, verifier_tools
from data.mock_data import AUDIT_ACTIONS, AUDIT_TEMPLATES
from core.live import rp


def _esc(value) -> str:
    """Escape plain text before embedding it in the HTML snippets below."""
    return html.escape(str(value), quote=True)


def _apply_template(tpl: str):
    prefix = f"[{tpl}] "
    current = st.session_state.get("note_draft", "") or ""
    if not current.startswith(prefix):
        st.session_state.note_draft = prefix + current

@st.dialog("Konfirmasi Otorisasi — Penangguhan Pembayaran Klaim (Simulasi)")
def _confirm_freeze(a: dict):
    st.markdown(
        f"""
        <div class="j-body">Anda akan menerbitkan instruksi penangguhan pencairan dana terhadap
        <b>{_esc(a['n_claims'])} klaim</b> senilai <b>{_esc(rp(a['value']))}</b> pada <b>{_esc(a['n_faskes'])} Faskes</b> terkait.</div>
        <div class="j-note" style="margin:10px 0;"><span>ⓘ</span><div><b>Simulasi prototipe:</b> tidak ada pembayaran
          yang ditangguhkan dan tidak ada sistem BPJS yang dihubungi. Riwayat tersedia selama sesi aktif; penyimpanan lokal lintas sesi bersifat opsional. Perubahan skor hanya berlaku pada sesi ini.</div></div>
        <div class="j-label" style="margin:14px 0 6px;">Pada alur sungguhan (rancangan, belum terhubung), langkah ini akan:</div>
        """,
        unsafe_allow_html=True,
    )
    for item in [
        "Menangguhkan pencairan klaim terkait di sistem pembayaran",
        "Memberi notifikasi ke unit pengampu faskes",
        "Menyiapkan rancangan berita acara untuk ditinjau petugas",
    ]:
        st.markdown(f'<div style="font-size:13px;margin-bottom:6px;">• {item}</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Batal", width="stretch"):
        st.rerun()
    if c2.button("✔ Konfirmasi (Simulasi)", width="stretch", type="primary"):
        st.session_state.audit_log.append(f"[{a['id']}] FREEZE dicatat (simulasi: tidak ada sistem eksternal yang dihubungi).")
        st.session_state.setdefault("audited", {})[a["id"]] = "freeze"
        note = st.session_state.get("note_draft", "") or ""
        score_before = a["score"]
        bench.apply_verdict(a["id"], "confirm", note)
        score_after = bench.get_live().by_id[a["id"]]["score"]
        bench.record_review_event(a["id"], "Konfirmasi penangguhan (simulasi)", note,
                                  score_before, score_after)
        st.rerun()


def render():
    live = bench.get_live()
    if not live.clusters:
        layout.page_header("", "teal", "Tindak Lanjut Audit", "Belum ada klaster yang dapat ditinjau.")
        st.info("Antrean tindak lanjut kosong. Buka Prioritas Klaster untuk memeriksa kasus yang tersedia.")
        if st.button("Buka Prioritas Klaster", type="primary"):
            layout.goto("risk")
        layout.render_footer()
        return
    cid = st.session_state.get("selected_cluster")
    if cid not in live.by_id:
        cid = live.clusters[0]["id"]
        st.session_state.selected_cluster = cid
    a = live.audit(cid)
    AUDIT_FASKES = a["faskes_rows"]
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:6px 10px;flex-wrap:wrap;">
          <span class="j-pill teal">ALUR VERIFIKATOR · TINDAK LANJUT</span>
          <span class="j-sub">REF: AUD-ACT-2026-{_esc(cid)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    layout.page_header(
        "", "teal", "Tindak Lanjut Audit",
        "Tinjau dugaan, periksa bukti, lalu catat tindak lanjut. JALA hanya menyusun prioritas; "
        "skor bukan bukti dan keputusan akhir ada pada verifikator.",
        right_html=(
            '<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;">'
            '<span class="j-chip">Data sintetis · mode simulasi</span>'
            '<span class="j-chip">Keputusan akhir: <b>verifikator</b></span></div>'
        ),
    )
    guide.render_page_guide("audit")
    if st.button("Kembali ke Prioritas Klaster", icon=":material/arrow_back:", key="audit_back_to_queue"):
        layout.goto("risk", cluster=cid)

    st.markdown(
        f"""
        <div class="j-card" style="border-left:4px solid #DC2626;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
            <div>
              <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <span class="j-iconbox red">✳</span>
                <b style="font-size:18px;">{_esc(a['name'])}</b>
                {cards.badge(a['flag'], 'red')}
                {cards.badge(*a['typology'])}
              </div>
              <div class="j-sub" style="margin-top:6px;">🧠 {a['algo']}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <div style="width:56px;height:56px;border-radius:9999px;border:3px solid #DC2626;color:#DC2626;
                          display:flex;align-items:center;justify-content:center;font-weight:700;">{_esc(a['score'])}%</div>
              <div>
                <div class="j-label">Network Risk Score</div>
                <div style="color:#DC2626;font-weight:600;font-size:13px;">{_esc(a['score_note'])}</div>
              </div>
            </div>
          </div>
          <div class="j-grid4" style="margin-top:16px;">
            {''.join(
                f'<div class="j-card tint" style="padding:12px;"><div class="j-label">{_esc(label)}</div>'
                f'<div style="font-weight:600;margin:4px 0 2px;color:{ {"dark": "#132A1C", "red": "#DC2626", "teal": "#0F766E"}[tone] };">'
                f'{_esc(value)}</div><div class="j-sub">{_esc(note)}</div></div>'
                for label, value, note, tone in a['cards'])}
          </div>
          <div class="j-note" style="margin-top:14px;align-items:flex-start;">
            <span>ⓘ</span>
            <div>
              <b>Ringkasan pola terukur:</b>
              <div style="margin-top:4px;">{_esc(a['evidence'])}</div>
            </div>
          </div>
          <div style="display:flex;justify-content:flex-end;margin-top:10px;">
            <span class="j-chip"><span class="ms">hub</span> {_esc(a['density'])}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Buka Peta Jaringan", icon=":material/open_in_new:", key="open_graph"):
            layout.goto("network", cluster=cid)
    with b2:
        verifier_tools.evidence_button(cid, key="evidence_audit")
    verifier_tools.modus_note(live.by_id[cid]["typology"])
    verifier_tools.benign_note(live, cid)
    verifier_tools.feedback_card(live, cid)

    audited_status = st.session_state.get("audited", {}).get(cid)
    action_notice = st.session_state.pop("audit_action_notice", None)
    if action_notice:
        st.success(action_notice)
    if audited_status:
        labels = {
            "freeze": "Penangguhan dicatat sebagai simulasi",
            "field_audit": "Rencana pemeriksaan lapangan dicatat",
            "dismiss": "Pola ditandai wajar dalam simulasi",
        }
        st.info(f"Status klaster: {labels.get(audited_status, 'Tindak lanjut dicatat')} · hanya berlaku pada demo ini.")
        if audited_status == "field_audit" and st.button("Batalkan rencana pada demo ini", key=f"undo_field_{cid}"):
            st.session_state["audited"].pop(cid, None)
            bench.record_review_event(cid, "Rencana pemeriksaan dibatalkan")
            st.rerun()

    st.markdown(
        """
        <div class="j-alert-teal" style="margin:14px 0;">
          <b>🛡 KETENTUAN &amp; TATA KELOLA KEPUTUSAN</b>
          <span class="j-pill grey" style="margin-left:8px;">Prinsip rancangan</span>
          <div style="margin-top:8px;font-weight:600;color:#132A1C;">"JALA provides a priority recommendation
            only. Final decision remains with the Verifikator team."</div>
          <div style="margin-top:6px;color:#475569;">Sistem JALA hanya menyediakan rekomendasi prioritas
            berbasis model graf. Keputusan final dan kewenangan eksekusi sepenuhnya berada pada Tim
            Verifikator BPJS Kesehatan.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:8px;flex-wrap:wrap;margin:18px 0 10px;">
          <div>
            <div class="j-h2">Pilih tindak lanjut</div>
            <div class="j-sub">Opsi di bawah hanya simulasi. Riwayat tersedia selama sesi aktif; penyimpanan lokal lintas sesi bersifat opsional. Tidak terhubung ke sistem BPJS.</div>
          </div>
          <span class="j-pill grey">3 opsi demo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="audit_actions"):
        cols = st.columns(3)
        for i, (col, act) in enumerate(zip(cols, AUDIT_ACTIONS)):
            action_title = act["title"]
            with col:
                st.markdown(
                    f"""
                    <div class="j-card j-actcard">
                      <div class="j-actcard-top">
                        <span class="j-iconbox {act['icon_tone']}" style="width:42px;height:42px;">{act['icon']}</span>
                        {cards.badge(*act["tag"])}
                      </div>
                      <div class="j-actcard-title">{_esc(action_title)}</div>
                      <div class="j-actcard-body">{_esc(act['body'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    act["button"],
                    width="stretch",
                    type="primary" if act["button_kind"] == "primary" else "secondary",
                    key=f"act_{i}_{act['id']}",
                ):
                    if act["button_kind"] == "primary":
                        _confirm_freeze(a)
                    else:
                        note = st.session_state.get("note_draft", "") or ""
                        score_before = live.by_id[cid]["score"]
                        st.session_state.audit_log.append(f"[{cid}] {action_title} dicatat (simulasi).")
                        if act["id"] == "dismiss":
                            st.session_state.setdefault("audited", {})[cid] = "dismiss"
                            bench.apply_verdict(cid, "dismiss", note)
                            score_after = bench.get_live().by_id[cid]["score"]
                        elif act["id"] == "field_audit":
                            st.session_state.setdefault("audited", {})[cid] = "field_audit"
                            score_after = score_before
                        else:
                            score_after = score_before
                        bench.record_review_event(cid, action_title, note, score_before, score_after)
                        if act["id"] == "dismiss":
                            st.rerun()
                        st.session_state["audit_action_notice"] = f"{action_title} tercatat di riwayat lokal. Tidak ada tindakan eksternal yang dijalankan."
                        st.rerun()

                st.markdown(
                    f'<div class="j-actcard-note">{_esc(act["note"])}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    l, r = st.columns([3, 2])
    with l:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
              <div class="j-h2"><span class="ms">hub</span> {len(AUDIT_FASKES)} Faskes dalam Klaster {cid}</div>
              <span class="j-sub">Terfilter: {len(AUDIT_FASKES)} titik simpul</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(tables.audit_faskes_html(AUDIT_FASKES), unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        df = pd.DataFrame(AUDIT_FASKES, columns=["kode", "wilayah", "tipe", "peran", "vol", "nilai"])
        c1, c2 = st.columns([1, 1])
        c1.markdown(f'<div class="j-sub">Menampilkan {len(AUDIT_FASKES)} dari {len(AUDIT_FASKES)} faskes terkait</div>', unsafe_allow_html=True)
        c2.download_button("Ekspor daftar faskes (.CSV)", export_context.csv_bytes(df),
                           file_name=f"jala_{cid}_faskes.csv", width="stretch")
        verifier_tools.whatif_panel(live, cid)
    with r:
        st.markdown(
            """
            <div class="j-h2">✎ Catatan Verifikator</div>
            <div class="j-sub" style="margin:4px 0 10px;">Tambahkan justifikasi forensik sebelum menekan
              tombol tindakan, agar tercatat dalam paket pemeriksaan simulasi. Catatan ini bukan berita acara resmi.</div>
            """,
            unsafe_allow_html=True,
        )
        note = st.text_area("Catatan verifikator", placeholder="Tuliskan pertimbangan atau konteks lapangan "
                                                    "yang perlu dicatat…",
                            height=120, key="note_draft")
        chips = st.columns(len(AUDIT_TEMPLATES) + 1)
        chips[0].markdown('<div class="j-sub" style="padding-top:6px;">Template Cepat:</div>',
                          unsafe_allow_html=True)
        for col, tpl in zip(chips[1:], AUDIT_TEMPLATES):
            with col:
                st.button(
                    tpl,
                    key=f"tpl_{tpl}",
                    width="stretch",
                    on_click=_apply_template,
                    args=(tpl,),
                )
        st.markdown(
            """
            <div class="j-card tint" style="margin-top:14px;">
              <div style="font-weight:600;color:#0F766E;font-size:13px;">Contoh verifikasi tanda tangan digital</div>
              <div class="j-sub" style="margin-top:6px;">Data petugas dan sertifikat berikut hanya contoh sintetis; tidak mewakili identitas atau sertifikat BPJS nyata.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="j-footer" style="margin-top:18px;">
          <div>🕐 Setiap tindak lanjut dicatat di riwayat lokal dan dapat disertakan dalam paket pemeriksaan.
            Prototipe: belum terintegrasi dengan sistem BPJS.</div>
          <div>KLASTER: {cid}</div>
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

    verifier_tools.review_timeline(cid, key=f"audit_history_{cid}")
    layout.render_footer()
