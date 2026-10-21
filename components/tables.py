from html import escape

from .cards import badge
from .typology import label as typology_label


def risk_table_html(rows) -> str:
    body = []
    cards = []
    for r in rows:
        score = max(0, min(100, int(r["score"])))
        name = escape(str(r["name"]))
        subtitle = escape(str(r["subtitle"]))
        why = escape(str(r["why"]))
        status = badge(escape(str(r["status"][0])), escape(str(r["status"][1])))
        typology = badge(escape(str(r["typology"][0])), escape(str(r["typology"][1])))
        score_tone = "#B91C1C" if score > 85 else "#0F766E"
        score_html = (
            '<div class="j-risk-score">'
            f'<div class="j-risk-score-value" style="color:{score_tone};">{score}/100</div>'
            f'<div class="j-bar" style="margin:6px 0;"><span style="width:{score}%;background:{score_tone};"></span></div>'
            f'<div class="j-sub">{escape(str(r["conf"]))} · {escape(str(r["metric"]))}</div>'
            '<div class="j-risk-score-note">Urutan pemeriksaan, bukan probabilitas atau bukti.</div>'
            '</div>'
        )
        body.append(
            f"""
            <tr>
              <td style="width:38%;">
                <div style="display:flex;gap:10px;align-items:flex-start;">
                  <span class="j-iconbox {escape(str(r['icon_tone']))}">{escape(str(r['icon']))}</span>
                  <div>
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                      <b style="font-size:14px;color:#132A1C;">{name}</b>{status}
                    </div>
                    <div class="j-sub" style="margin-top:3px;">{subtitle}</div>
                  </div>
                </div>
              </td>
              <td style="width:16%;">{score_html}</td>
              <td style="width:12%;">{typology}</td>
              <td style="width:34%;"><div class="j-why">{why}</div></td>
            </tr>
            """
        )
        cards.append(
            f"""
            <article class="j-card j-risk-mobile-card">
              <div class="j-risk-mobile-heading">
                <div class="j-risk-mobile-name">{name}</div>
                {status}
              </div>
              <div class="j-risk-mobile-subtitle">{subtitle}</div>
              <div class="j-risk-mobile-score">
                <span>Prioritas pemeriksaan</span>
                <strong style="color:{score_tone};">{score}/100</strong>
              </div>
              <div class="j-risk-score-note">Skor mengurutkan pemeriksaan; bukan probabilitas atau bukti.</div>
              <div class="j-risk-mobile-field">
                <span>Dugaan pola</span>
                {typology}
              </div>
              <div class="j-risk-mobile-why">
                <b>Alasan penandaan</b>
                <span>{why}</span>
              </div>
            </article>
            """
        )
    return f"""
    <div class="j-risk-mobile-cards">{''.join(cards)}</div>
    <div class="j-risk-desktop-table">
    <div class="j-table-wrap"><table class="j-table j-table-risk">
      <thead><tr>
        <th>Klaster / Nama Jaringan</th><th>Prioritas (/100)</th><th>Dugaan Pola</th><th>Alasan Penandaan</th>
      </tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table></div>
    </div>
    """


def triage_table_html(rows, selected_id=None) -> str:
    body = []
    for r in rows:
        hl = ' style="background:#E6F4F2;"' if r["id"] == selected_id else ""
        dot = "red" if r["score"] >= 90 else ("amber" if r["score"] >= 85 else "green")
        body.append(
            f"""
            <tr{hl}>
              <td>
                <div style="display:flex;gap:8px;align-items:flex-start;">
                  <span class="dot {dot}" style="margin-top:6px;"></span>
                  <div>
                    <b style="color:#132A1C;">{escape(str(r['name']))}</b>
                    <div class="j-sub">{escape(str(r['nodes']))}</div>
                  </div>
                </div>
              </td>
              <td>{badge(typology_label(r['typology']), 'amber' if r['typology'] in ('Phantom Billing', 'Repeat Billing', 'Upcoding Prosedur', 'Ghost Prescription') else 'grey')}</td>
              <td>{escape(str(r['faskes']))}</td>
              <td class="num">{r['volume']}</td>
              <td class="num" style="color:#B91C1C;font-weight:600;">{escape(str(r['value']))}</td>
              <td class="num"><b style="color:{'#DC2626' if r['score'] >= 90 else '#132A1C'};">{r['score']}/100</b></td>
              <td>{badge(*r['status'])}</td>
            </tr>
            """
        )
    return f"""
    <div class="j-scrollhint">← geser tabel ke samping →</div>
    <div class="j-table-wrap"><table class="j-table j-table-triage">
      <thead><tr>
        <th>Klaster / Entitas Jaringan</th><th>Kategori Tipologi</th><th>Faskes / Dokter Terkait</th>
        <th style="text-align:right;">Volume Klaim</th><th style="text-align:right;">Nilai Anomali</th>
        <th style="text-align:right;">Prioritas pemeriksaan (/100)</th><th>Status</th>
      </tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table></div>
    """


def audit_faskes_html(rows) -> str:
    body = []
    for code, region, tipe, role, vol, nilai in rows:
        body.append(
            f"""
            <tr>
              <td><b style="color:#132A1C;">{escape(str(code))}</b><div class="j-sub">{escape(str(region))}</div></td>
              <td>{escape(str(tipe))}</td>
              <td>{badge(*role)}</td>
              <td class="num">{vol}</td>
              <td class="num" style="color:#B91C1C;font-weight:600;">{escape(str(nilai))}</td>
            </tr>
            """
        )
    return f"""
    <div class="j-scrollhint">← geser tabel ke samping →</div>
    <div class="j-table-wrap"><table class="j-table j-table-faskes">
      <thead><tr>
        <th>Kode Faskes / Nama</th><th>Tipe</th><th>Peran Klaster</th>
        <th style="text-align:right;">Vol Klaim</th><th style="text-align:right;">Total Nilai</th>
      </tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table></div>
    """
