import plotly.graph_objects as go

from data.mock_data import (
    GRAPH_EDGES,
    GRAPH_NODES,
    TREND_COLORS,
    TREND_SERIES,
    TREND_WEEKS,
)

FONT = dict(family="Inter, sans-serif", size=12, color="#475569")


def _base_layout(fig, height):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        hoverlabel=dict(font_family="Inter, sans-serif", font_size=12),
    )
    return fig


def trend_chart():
    fig = go.Figure()
    for name, values in TREND_SERIES.items():
        fig.add_trace(
            go.Scatter(
                x=TREND_WEEKS,
                y=values,
                mode="lines+markers",
                name=name,
                line=dict(color=TREND_COLORS[name], width=2.5),
                marker=dict(size=6, color=TREND_COLORS[name]),
                fill="tozeroy" if name == "Phantom Billing" else None,
                fillcolor="rgba(15,118,110,0.08)" if name == "Phantom Billing" else None,
                hovertemplate="%{x}: %{y} flagged<br>",
            )
        )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#EDF1F4", zeroline=False, range=[0, 170])
    fig.update_layout(legend=dict(orientation="h", y=1.08, x=1.0, xanchor="right", font=dict(size=12)))
    return _base_layout(fig, 380)


def freq_chart(labels, baseline, spike, peak):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels, y=baseline, mode="lines", name="Baseline Normal",
            line=dict(color="#0F766E", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=labels, y=spike, mode="lines+markers", name="Spike Anomali",
            line=dict(color="#C2410C", width=2.5),
            marker=dict(size=7, color="#DC2626"),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.10)",
        )
    )
    peak_idx = spike.index(max(spike))
    fig.add_annotation(
        x=labels[peak_idx], y=spike[peak_idx], text=peak, showarrow=False,
        yshift=16, font=dict(color="#FFFFFF", size=10),
        bgcolor="#DC2626", bordercolor="#DC2626", borderpad=4,
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#EDF1F4", zeroline=False)
    fig.update_layout(legend=dict(orientation="h", y=1.15, x=1.0, xanchor="right", font=dict(size=11)))
    return _base_layout(fig, 260)


_NODE_SYMBOL = {"pasien": "circle", "faskes": "hexagon", "dokter": "square", "icd": "diamond"}


def network_figure(zoom: float = 1.0, isolate: bool = False):
    nodes = [n for n in GRAPH_NODES if (n["risk"] or not isolate)]
    ids = {n["id"] for n in nodes}
    edges = [e for e in GRAPH_EDGES if e["src"] in ids and e["dst"] in ids and not (isolate and e.get("faint"))]
    pos = {n["id"]: (n["x"], n["y"]) for n in GRAPH_NODES}

    fig = go.Figure()
    for e in edges:
        x0, y0 = pos[e["src"]]
        x1, y1 = pos[e["dst"]]
        dash = {"solid": None, "dash": "dash", "dot": "dot"}[e["style"]]
        color = "rgba(220,38,38,0.75)" if e["risk"] else ("rgba(148,163,184,0.5)" if e.get("faint") else "#0F766E")
        fig.add_trace(
            go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines", hoverinfo="skip",
                line=dict(color=color, width=1.6, dash=dash), showlegend=False,
            )
        )
        if e["label"]:
            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=e["label"], showarrow=False,
                font=dict(size=9, color="#C2410C" if e["risk"] else "#64748B"),
                bgcolor="rgba(255,255,255,0.85)", borderpad=2,
            )

    for group, color, size in ((False, "#0F766E", 26), (True, "#EA580C", 26)):
        grp = [n for n in nodes if n["risk"] == group]
        if not grp:
            continue
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in grp], y=[n["y"] for n in grp], mode="markers",
                marker=dict(
                    size=[size * zoom if n["type"] == "faskes" else 18 * zoom for n in grp],
                    color=color, symbol=[_NODE_SYMBOL[n["type"]] for n in grp],
                    line=dict(color="#FFFFFF", width=2),
                ),
                text=[f"<b>{n['label']}</b><br>{n['sub']}" for n in grp],
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            )
        )
        for n in grp:
            label_color = "#C2410C" if n["risk"] else "#334155"
            fig.add_annotation(
                x=n["x"], y=n["y"], text=f"<b>{n['label']}</b><br><span style='font-size:9px'>{n['sub']}</span>",
                showarrow=False, yshift=-34 * zoom, font=dict(size=10, color=label_color),
            )

    fig.add_shape(
        type="circle", x0=6.4, y0=0.9, x1=12.4, y1=8.1,
        fillcolor="rgba(249,115,22,0.06)", line=dict(color="rgba(249,115,22,0.25)", width=1, dash="dot"),
    )
    fig.update_xaxes(visible=False, range=[0, 13.5])
    fig.update_yaxes(visible=False, range=[0, 9])
    fig.update_layout(height=int(620 * min(max(zoom, 0.8), 1.6)))
    return _base_layout(fig, int(620 * min(max(zoom, 0.8), 1.6)))
