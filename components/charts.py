"""Grafik untuk dashboard JALA (plotly + grafik jaringan animasi SVG)."""
import json

import plotly.graph_objects as go

import data.mock_data as md
from components.typology import label as typology_label

TEAL = "#0F766E"
ORANGE = "#F97316"
RED = "#DC2626"
GRID = "#E2E8F0"
INK = "#132A1C"
MUTED = "#64748B"


def _base_layout(fig, height=320):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ---------------------------------------------------------------------------
# Trend mingguan (dashboard): 3 tipologi fraud
# ---------------------------------------------------------------------------
def trend_chart(weeks, series):
    fig = go.Figure()
    for i, (name, ys) in enumerate(series.items()):
        color = md.TREND_COLORS.get(name, TEAL)
        fill = i == 0  # seri pertama (Phantom Billing) diberi area fill
        fig.add_trace(go.Scatter(
            x=weeks, y=ys, name=typology_label(name), mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            fill="tozeroy" if fill else None,
            fillcolor=_hex_to_rgba(color, .08) if fill else None,
        ))
    fig = _base_layout(fig, height=420)
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# Lonjakan frekuensi klaim vs ambang normal (Claim Details)
# ---------------------------------------------------------------------------
def freq_chart(labels, baseline, spike, peak=""):
    """Bar klaim terdeteksi + garis ambang normal, dengan anotasi puncak."""
    base_max = max(baseline) if baseline else 0
    colors = [
        RED if v >= base_max * 2 else ORANGE if v > base_max else TEAL
        for v in spike
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=spike, name="Klaim Ditandai",
        marker_color=colors,
        hovertemplate="%{x}<br>%{y} klaim ditandai<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=baseline, name="Klaim Lain di Faskes Sama",
        mode="lines+markers",
        line=dict(color=MUTED, width=2, dash="dash"),
        marker=dict(size=6, color=MUTED),
        hovertemplate="%{x}<br>klaim lain %{y}<extra></extra>",
    ))
    fig = _base_layout(fig, height=260)
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0.35,
    )
    if peak and spike:
        fig.add_annotation(
            x=labels[spike.index(max(spike))], y=max(spike),
            text=f"Puncak {peak}", showarrow=True, arrowhead=2, ay=-30,
            font=dict(size=11, color=RED, family="Inter, sans-serif"),
        )
    return fig


# ---------------------------------------------------------------------------
# Animated HIN graph (SVG + requestAnimationFrame, rendered in an iframe)
# ---------------------------------------------------------------------------
_NETWORK_HTML = """
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;height:100%;background:transparent;overflow:hidden;
    font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
  #wrap{position:relative;width:100%;height:100%;}
  svg{position:absolute;inset:0;width:100%;height:100%;display:block;}
  .lbl{font-size:12px;font-weight:700;text-anchor:middle;pointer-events:none;}
  .sub{font-size:10.5px;font-weight:500;text-anchor:middle;pointer-events:none;}
  .elabel{font-size:10px;font-weight:500;text-anchor:middle;dominant-baseline:central;pointer-events:none;}
  .node{cursor:pointer;}
  #tip{position:absolute;display:none;pointer-events:none;background:#fff;border:1px solid #E2E8F0;
    border-radius:8px;padding:8px 10px;font-size:12px;color:#132A1C;
    box-shadow:0 4px 14px rgba(19,42,28,.12);max-width:220px;z-index:5;}
  #tip b{display:block;font-size:12.5px;}
  #tip span{color:#64748B;}
  #ctl{position:absolute;right:8px;top:6px;z-index:6;display:flex;gap:6px;}
  #ctl button{font:500 11px 'Inter',sans-serif;color:#334155;background:rgba(255,255,255,.9);
    border:1px solid #E2E8F0;border-radius:6px;padding:4px 9px;cursor:pointer;}
  #ctl button:hover{background:#F1F5F9;}
</style></head>
<body>
<div id="wrap">
  <div id="ctl"><button id="tgl">&#10074;&#10074; Jeda animasi</button></div>
  <svg id="g" xmlns="http://www.w3.org/2000/svg"></svg>
  <div id="tip"></div>
</div>
<script>
(function(){
  var NODES = __NODES__, EDGES = __EDGES__, ZOOM = __ZOOM__, PULSE = __PULSE__;
  var XR = 13.5, YR = 9.0, NS = "http://www.w3.org/2000/svg";
  var TEAL = "#0F766E", ORANGE = "#EA580C";
  var svg = document.getElementById("g"), tip = document.getElementById("tip");
  var W = 0, H = 0, paused = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hover = null, T = 0, last = null;

  function el(name, attrs, parent){
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    (parent || svg).appendChild(e); return e;
  }
  var gCluster = el("g", {}), gEdges = el("g", {}), gPk = el("g", {}), gNodes = el("g", {}),
      gLabels = el("g", {}), gEL = el("g", {});

  var byId = {}, rand = (function(s){ return function(){ s = (s*9301+49297)%233280; return s/233280; }; })(7);
  NODES.forEach(function(n, i){
    n.px = rand()*6.28; n.py = rand()*6.28;
    n.fx = 0.35 + rand()*0.35; n.fy = 0.30 + rand()*0.35;
    n.amp = (n.type === "faskes" ? 4 : 8) * (n.risk ? 1.25 : 1);
    n.r = (n.type === "faskes" ? 13 : 9) * ZOOM;
    byId[n.id] = n;
  });

  var cluster = el("ellipse", {fill:"rgba(249,115,22,0.06)", stroke:"rgba(249,115,22,0.30)",
                               "stroke-width":1, "stroke-dasharray":"4 5"}, gCluster);
  var hasRisk = NODES.some(function(n){ return n.risk; });
  if (!hasRisk) cluster.style.display = "none";
  var rings = [0, 1].map(function(){ return el("circle", {fill:"none", stroke:"rgba(220,38,38,.55)", "stroke-width":1.6}, gCluster); });

  EDGES.forEach(function(e){
    e.color = e.risk ? "rgba(220,38,38,0.75)" : (e.faint ? "rgba(148,163,184,0.55)" : TEAL);
    var dash = e.style === "dash" ? "9 6" : (e.style === "dot" ? "2 5" : "");
    e.line = el("line", {stroke:e.color, "stroke-width":1.7, "stroke-linecap":"round"}, gEdges);
    if (dash) e.line.setAttribute("stroke-dasharray", dash);
    e.dashLen = e.style === "dash" ? 15 : (e.style === "dot" ? 7 : 0);
    var cnt = e.faint ? 0 : (e.risk ? 2 : 1);
    e.pk = []; for (var i = 0; i < cnt; i++)
      e.pk.push({ph: i/cnt + rand()*0.3, c: el("circle", {r: e.risk ? 3.4 : 2.8, fill:e.color}, gPk)});
    e.spd = e.risk ? 0.32 : 0.12;
    if (e.label){
      e.bg = el("rect", {fill:"rgba(255,255,255,.9)", rx:3}, gEL);
      e.txt = el("text", {"class":"elabel", fill: e.risk ? "#C2410C" : "#64748B"}, gEL);
      e.txt.textContent = e.label;
    }
  });

  function shape(n, g){
    var c = n.risk ? ORANGE : (n.type === "dokter" ? "#115E59" : TEAL);
    var a = {fill:c, stroke:"#fff", "stroke-width":2};
    var r = n.r, s;
    if (n.type === "pasien") s = el("circle", Object.assign({r:r}, a), g);
    else if (n.type === "dokter") s = el("rect", Object.assign({x:-r*0.9, y:-r*0.9, width:r*1.8, height:r*1.8}, a), g);
    else if (n.type === "icd") s = el("rect", Object.assign({x:-r*0.75, y:-r*0.75, width:r*1.5, height:r*1.5, transform:"rotate(45)"}, a), g);
    else {
      var pts = []; for (var k = 0; k < 6; k++){ var t = Math.PI/3*k + Math.PI/6;
        pts.push((Math.cos(t)*r*1.05).toFixed(1)+","+(Math.sin(t)*r*1.05).toFixed(1)); }
      s = el("polygon", Object.assign({points:pts.join(" ")}, a), g);
    }
    return s;
  }
  NODES.forEach(function(n){
    n.g = el("g", {"class":"node"}, gNodes); n.shape = shape(n, n.g);
    n.g.addEventListener("mouseenter", function(){ hover = n.id; });
    n.g.addEventListener("mousemove", function(ev){
      var b = svg.getBoundingClientRect();
      tip.style.display = "block";
      tip.innerHTML = "<b>"+n.label+"</b><span>"+(n.sub||n.type)+"</span>";
      tip.style.left = Math.min(ev.clientX - b.left + 14, W - 230) + "px";
      tip.style.top = (ev.clientY - b.top + 14) + "px";
    });
    n.g.addEventListener("mouseleave", function(){ hover = null; tip.style.display = "none"; });
    n.lbl = el("text", {"class":"lbl", fill: n.risk ? "#C2410C" : "#334155"}, gLabels);
    n.lbl.textContent = n.label;
    n.sb = el("text", {"class":"sub", fill: n.risk ? "#C2410C" : "#475569"}, gLabels);
    n.sb.textContent = n.sub || "";
  });

  function resize(){
    var b = svg.getBoundingClientRect(); W = b.width; H = b.height;
    var sx = W/XR, sy = H/YR, k = Math.min(sx, sy)/60;
    NODES.forEach(function(n){ n.bx = n.x*sx; n.by = (YR-n.y)*sy; });
    cluster.setAttribute("cx", 9.4*sx); cluster.setAttribute("cy", (YR-4.5)*sy);
    cluster.setAttribute("rx", 3.0*sx); cluster.setAttribute("ry", 3.6*sy);
    draw(0);
  }

  function draw(t){
    var kp = byId[PULSE];
    NODES.forEach(function(n){
      var dx = paused ? 0 : Math.sin(t*n.fx + n.px)*n.amp;
      var dy = paused ? 0 : Math.cos(t*n.fy + n.py)*n.amp;
      n.cx = n.bx + dx; n.cy = n.by + dy;
    });
    NODES.forEach(function(n){
      var hot = hover === n.id;
      var linked = hover && EDGES.some(function(e){ return (e.src === hover && e.dst === n.id) || (e.dst === hover && e.src === n.id); });
      var dim = hover && !hot && !linked;
      var pulse = (n.risk && !paused) ? 1 + 0.06*Math.sin(t*3 + n.px) : 1;
      var sc = (hot ? 1.3 : 1) * pulse;
      n.g.setAttribute("transform", "translate("+n.cx+","+n.cy+") scale("+sc+")");
      n.g.style.opacity = dim ? 0.3 : 1;
      var off = n.r + (n.type === "faskes" ? 20 : 17)*ZOOM;
      n.lbl.setAttribute("x", n.cx); n.lbl.setAttribute("y", n.cy + off);
      n.sb.setAttribute("x", n.cx); n.sb.setAttribute("y", n.cy + off + 14);
      n.lbl.style.opacity = n.sb.style.opacity = dim ? 0.3 : 1;
    });
    EDGES.forEach(function(e){
      var a = byId[e.src], b = byId[e.dst];
      if (!a || !b) return;
      var on = !hover || e.src === hover || e.dst === hover;
      e.line.setAttribute("x1", a.cx); e.line.setAttribute("y1", a.cy);
      e.line.setAttribute("x2", b.cx); e.line.setAttribute("y2", b.cy);
      e.line.style.opacity = on ? 1 : 0.15;
      e.line.setAttribute("stroke-width", on && hover ? 2.6 : 1.7);
      if (e.dashLen) e.line.setAttribute("stroke-dashoffset", -(t*(e.risk ? 30 : 14)) % e.dashLen);
      e.pk.forEach(function(p){
        var u = paused ? p.ph : ((t*e.spd + p.ph) % 1);
        p.c.setAttribute("cx", a.cx + (b.cx-a.cx)*u); p.c.setAttribute("cy", a.cy + (b.cy-a.cy)*u);
        p.c.style.opacity = on ? Math.sin(u*Math.PI) : 0;
      });
      if (e.txt){
        var mx = (a.cx+b.cx)/2, my = (a.cy+b.cy)/2;
        e.txt.setAttribute("x", mx); e.txt.setAttribute("y", my);
        var w = e.label.length*5.4 + 8;
        e.bg.setAttribute("x", mx - w/2); e.bg.setAttribute("y", my - 8);
        e.bg.setAttribute("width", w); e.bg.setAttribute("height", 16);
        e.txt.style.opacity = e.bg.style.opacity = on ? 1 : 0.15;
      }
    });
    if (kp && hasRisk){
      var sx = W/XR, sy = H/YR;
      cluster.setAttribute("stroke-opacity", paused ? 1 : 0.7 + 0.3*Math.sin(t*1.6));
      rings.forEach(function(r, i){
        var u = paused ? 0 : ((t/3 + i*0.5) % 1);
        r.setAttribute("cx", kp.cx); r.setAttribute("cy", kp.cy);
        r.setAttribute("r", kp.r + u*70*ZOOM); r.setAttribute("opacity", paused ? 0 : (1-u)*0.7);
      });
    }
  }

  function loop(ts){
    if (last === null) last = ts;
    if (!paused) T += (ts - last)/1000;
    last = ts; draw(T); requestAnimationFrame(loop);
  }
  var tgl = document.getElementById("tgl");
  function label(){ tgl.innerHTML = paused ? "&#9654; Putar animasi" : "&#10074;&#10074; Jeda animasi"; }
  tgl.addEventListener("click", function(){ paused = !paused; label(); });
  label();
  window.addEventListener("resize", resize);
  resize(); requestAnimationFrame(loop);
})();
</script></body></html>
"""


def network_animated_html(graph, zoom: float = 1.0, isolate: bool = False) -> str:
    """Self-contained animated HIN graph (SVG + requestAnimationFrame). graph = (nodes, edges) dari core.live."""
    all_nodes, all_edges = graph
    pulse = next((n["id"] for n in all_nodes if n["risk"] and n["type"] == "faskes"), "")
    nodes = [n for n in all_nodes if (n["risk"] or not isolate)]
    ids = {n["id"] for n in nodes}
    edges = [e for e in all_edges if e["src"] in ids and e["dst"] in ids and not (isolate and e.get("faint"))]
    return (
        _NETWORK_HTML
        .replace("__NODES__", json.dumps(nodes))
        .replace("__EDGES__", json.dumps(edges))
        .replace("__ZOOM__", str(float(zoom)))
        .replace("__PULSE__", json.dumps(pulse))
    )


# ---------------------------------------------------------------------------
# Simulasi kapasitas audit (hasil core.evaluate, bukan angka ketikan)
# ---------------------------------------------------------------------------
def capacity_chart(metrics: dict, capacity: int | None = None):
    xs = metrics["curve_ks"]
    sc = metrics["scorers"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[v * 100 for v in metrics["random"]["curve"]], name="Pemilihan acak",
                             mode="lines", line=dict(color=ORANGE, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=xs, y=[v * 100 for v in sc["rules"]["curve"]], name="Aturan per klaim (cara lama)",
                             mode="lines", line=dict(color="#94A3B8", width=2.5)))
    fig.add_trace(go.Scatter(x=xs, y=[v * 100 for v in sc["graph_gbm"]["curve"]], name="JALA: fitur graf + GBM",
                             mode="lines", line=dict(color=TEAL, width=3),
                             fill="tonexty", fillcolor="rgba(15,118,110,.07)"))
    if capacity is not None:
        capacity = max(0, min(int(capacity), int(xs[-1])))
        def at_k(curve):
            i = min(range(len(xs)), key=lambda j: abs(xs[j] - capacity))
            return float(curve[i]) * 100
        fig.add_vline(x=capacity, line_dash="dot", line_color="#0F766E")
        fig.add_trace(go.Scatter(
            x=[capacity, capacity],
            y=[at_k(sc["rules"]["curve"]), at_k(sc["graph_gbm"]["curve"])],
            mode="markers", marker=dict(size=10, color=["#94A3B8", TEAL]),
            name=f"Pada kapasitas {capacity:,}", showlegend=False,
            hovertemplate="%{y:.1f}% tertangkap<extra></extra>"))
    fig = _base_layout(fig, height=360)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), hovermode="x unified")
    fig.update_xaxes(title_text="Klaim yang diperiksa verifikator (urut skor tertinggi)")
    fig.update_yaxes(title_text="Fraud tertangkap (%)", range=[0, 100], ticksuffix="%")
    return fig


def weekly_replay_capacity_chart(report: dict, selected_capacity: int):
    """Caught fraud counts summed from each week's incoming-claim queue."""
    grid = report["capacity_grid"]
    weekly = report["weekly"]
    limit = min(max(selected_capacity, 0), max(grid))

    def total(key, k):
        hits = 0.0
        for week in weekly:
            curve = week["capacity_curve"][key]
            idx = next((i for i, x in enumerate(grid) if x >= k), len(grid) - 1)
            if idx == 0:
                value = curve[0]
            else:
                lo, hi = grid[idx - 1], grid[idx]
                frac = (k - lo) / (hi - lo)
                value = curve[idx - 1] + frac * (curve[idx] - curve[idx - 1])
            hits += value
        return hits

    xs = [x for x in grid if x <= max(85, limit)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[total("fraud_caught_rules", x) for x in xs],
                             name="Aturan per klaim", mode="lines", line=dict(color="#94A3B8", width=2.5)))
    fig.add_trace(go.Scatter(x=xs, y=[total("fraud_caught_jala", x) for x in xs],
                             name="JALA", mode="lines", line=dict(color=TEAL, width=3)))
    fig.add_vline(x=limit, line_dash="dot", line_color="#0F766E")
    fig = _base_layout(fig, height=320)
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), hovermode="x unified")
    fig.update_xaxes(title_text="Klaim yang diperiksa per minggu")
    fig.update_yaxes(title_text="Total klaim fraud sintetis tertangkap (14 minggu)", rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# Uji ketahanan (hasil core.robustness, dibaca dari docs/robustness.json)
# ---------------------------------------------------------------------------
_TYP_NAMES = {"phantom": "Phantom Billing (Klaim Palsu)", "repeat": "Repeat Billing", "selfref": "Rujukan tidak sesuai (Self-referral)"}


def ablation_chart(rob: dict):
    """Average precision per tipologi untuk tiga tahap fitur (validasi silang per kelompok faskes)."""
    stages = rob["ablation"]["bertahap"]
    labels = {0: "Per-klaim saja", 1: "+ agregat entitas (derajat)", 2: "+ relasi multi-entitas (JALA)"}
    colors = ["#CBD5E1", "#94A3B8", TEAL]
    fig = go.Figure()
    for i, (_name, blk) in enumerate(stages.items()):
        fig.add_trace(go.Bar(
            x=[_TYP_NAMES[t] for t in _TYP_NAMES], y=[blk["per_typology"][t]["ap"] for t in _TYP_NAMES],
            name=labels[i], marker_color=colors[i],
            text=[f"{blk['per_typology'][t]['ap']:.2f}" for t in _TYP_NAMES], textposition="outside"))
    fig = _base_layout(fig, height=320)
    fig.update_layout(barmode="group", margin=dict(l=10, r=10, t=40, b=10))
    fig.update_yaxes(title_text="Average precision", range=[0, 1.12])
    return fig


def evasion_chart(rob: dict):
    """R-precision (k = jumlah fraud) menurut tingkat penghindaran. Dipakai R-precision, bukan recall@500,
    karena jumlah fraud ikut berubah antar tingkat."""
    rows = rob["evasion"]
    xs = [r["level"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[r["rules"]["r_precision"] * 100 for r in rows], name="Aturan per klaim (cara lama)",
                             mode="lines+markers", line=dict(color="#94A3B8", width=2.5)))
    fig.add_trace(go.Scatter(x=xs, y=[r["model_dilatih_ulang"]["r_precision"] * 100 for r in rows],
                             name="JALA dilatih ulang pada dunia itu (CV)", mode="lines+markers",
                             line=dict(color=ORANGE, width=2.5, dash="dash")))
    fig.add_trace(go.Scatter(x=xs, y=[r["model_beku"]["r_precision"] * 100 for r in rows],
                             name="JALA tanpa pembaruan (dilatih di dunia seed lain)", mode="lines+markers",
                             line=dict(color=TEAL, width=3)))
    fig = _base_layout(fig, height=320)
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=30), hovermode="x unified")
    fig.update_xaxes(title_text="Tingkat menghindar (0 = biasa, 1 = paling menghindar)", tickvals=xs, title_standoff=8)
    fig.update_yaxes(title_text="Fraud tertangkap (%)", range=[0, 100], ticksuffix="%")
    return fig
