def badge(text: str, tone: str = "grey") -> str:
    return f'<span class="j-pill {tone}">{text}</span>'


def metric_card(label: str, value: str, badge_html: str = "", note: str = "", icon: str = "",
                value_tone: str = "", label_lines: int = 1, card_class: str = "") -> str:
    tone_cls = f" {value_tone}" if value_tone else ""
    card_cls = f" {card_class}" if card_class else ""
    note_html = f'<div class="j-note" style="margin-top:14px;">{icon}&nbsp;<span>{note}</span></div>' if note else ""
    return (
        f'<div class="j-card{card_cls}">'
        f'<div style="display:flex;justify-content:space-between;align-items:{"flex-start" if label_lines > 1 else "center"};gap:8px;'
        f'min-height:{label_lines * 18 if label_lines > 1 else 0}px;">'
        f'<span class="j-label">{label}</span>{badge_html}</div>'
        f'<div class="j-value{tone_cls}" style="margin-top:10px;">{value}</div>'
        f'{note_html}</div>'
    )


def stat_card(label: str, value: str, note: str = "", icon: str = "", icon_tone: str = "grey",
              value_tone: str = "dark", delta: str = "") -> str:
    delta_html = f' <span style="color:#0F766E;font-size:12px;font-weight:600;">{delta}</span>' if delta else ""
    note_html = f'<div class="j-sub" style="margin-top:2px;">{note}</div>' if note else ""
    return (
        '<div style="display:flex;gap:12px;align-items:flex-start;"><div>'
        f'<div class="j-label">{label}</div>'
        f'<div class="j-value {value_tone}" style="font-size:26px;margin-top:4px;">{value}{delta_html}</div>'
        f'{note_html}</div>'
        f'<div style="margin-left:auto;"><span class="j-iconbox {icon_tone}">{icon}</span></div></div>'
    )


def kv(label: str, value: str, tone: str = "") -> str:
    color = {"red": "#DC2626", "teal": "#0F766E"}.get(tone, "#132A1C")
    return f"""
    <div class="j-kv">
      <span class="k">{label}</span>
      <span class="v" style="color:{color};">{value}</span>
    </div>
    """


def score_bar(score: int, conf: str, metric: str, tone: str = "#B91C1C") -> str:
    color = tone if score > 85 else "#0F766E"
    return f"""
    <div>
      <div style="display:flex;align-items:baseline;gap:6px;">
        <span style="font-size:18px;font-weight:700;color:{color};">{score}%</span>
        <span style="font-size:11px;color:#64748B;">{conf}</span>
      </div>
      <div class="j-bar" style="margin:6px 0;"><span style="width:{score}%;background:{color};"></span></div>
      <div class="j-sub">{metric}</div>
    </div>
    """
