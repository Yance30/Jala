from html import escape

from .cards import badge, score_bar
from .typology import label as typology_label


def risk_table_html(rows) -> str:
    body = []
    for r in rows:
        body.append(
            f"""
            <tr>
              <td style="width:38%;">
                <div style="display:flex;gap:10px;align-items:flex-start;">
                  <span class="j-iconbox {escape(str(r['icon_tone']))}">{escape(str(r['icon']))}</span>
                  <div>
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                      <b style="font-size:14px;color:#132A1C;">{escape(str(r['name']))}</b>{badge(*r['status'])}
                    </div>
                    <div class="j-sub" style="margin-top:3px;">{escape(str(r['subtitle']))}</div>
                  </div>
                </div>
              </td>
              <td style="width:16%;">{score_bar(r['score'], r['conf'], r['metric'])}</td>
              <td style="width:12%;">{badge(*r['typology'])}</td>
              <td style="width:34%;"><div class="j-why">{escape(str(r['why']))}</div></td>
            </tr>
            """
        )
    return f"""
    <div class="j-scrollhint">← geser tabel ke samping →</div>
    <div class="j-table-wrap"><table class="j-table j-table-risk">
      <thead><tr>
        <th>Klaster / Nama Jaringan</th><th>Skor Prioritas (0–100)</th><th>Dugaan Pola</th><th>Alasan Penandaan</th>
      </tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table></div>
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
              <td class="num"><b style="color:{'#DC2626' if r['score'] >= 90 else '#132A1C'};">{r['score']}%</b></td>
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
        <th style="text-align:right;">Skor Risiko Jaringan</th><th>Status</th>
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
