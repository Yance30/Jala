import streamlit as st

from components import layout
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


def render():
    render_content()
    st.markdown(
        """
        <div class="j-footer">
          <div><span class="dot teal"></span>PoC Node 04 · Aktif - Model GNN v2.4 (Sync OK)</div>
          <div>JALA Engine © 2024 BPJS Kesehatan RI &nbsp;•&nbsp; Unit Audit Forensik &amp; Investigasi Khusus</div>
        </div>
        """,
        unsafe_allow_html=True,
    )