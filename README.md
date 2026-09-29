# JALA Fraud Analytics (Streamlit)

Working Streamlit implementation of the 8 Stitch screens for the JALA BPJS healthcare-claims
fraud-detection dashboard. Synthetic data only — no real participant data (UU PDP compliant).

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
# → http://localhost:8501
```

Verified on Python 3.14 with streamlit 1.57, plotly, pandas.

## Screens & navigation

Sidebar nav rail (styled per `DESIGN.md`) exposes 7 modules; deep links work via `?page=<key>`:

| Key | Screen |
|---|---|
| `dashboard` | Fraud Intelligence Dashboard (KPIs, weekly HAN trend chart) |
| `pipeline` | Detection Pipeline (4-stage GNN: ETL → Topology → HAN → HITL) |
| `network` | Network Graph (interactive HIN topology, zoom / isolate / filters) |
| `risk` | Risk Ranking (filter chips, search, score bars, CSV export) |
| `claim` | Claim Details — triage queue + forensic side panel (open from Risk Ranking) |
| `comparison` | Rule-Based (legacy) vs HAN paradigm comparison |
| `audit` | Audit Action (3 operational actions, freeze confirmation dialog, audit log) |
| `about` | Data source & privacy notes |

Cross-links reproduced from the mockups: Pipeline → Network Graph; Network Graph → Risk
Ranking / Audit Action / isolate subgraph; Risk Ranking → Claim Details / Sub-Graph;
Audit Action → Network Graph.

## Structure

```text
app.py            router, session-state nav, design-token injection
views/            one module per screen (named views/, not pages/, because Streamlit
                  treats a top-level pages/ dir as implicit multi-page and would add
                  a second unstyled nav)
components/       theme.py (DESIGN.md tokens as CSS), sidebar, layout, cards, tables, charts
data/mock_data.py all sample data transcribed from the Stitch export
assets/logo.png     official JALA logo mark (also used as browser favicon)
assets/stitch_reference/  original Stitch screen renders (design reference)
DESIGN.md         design system source of truth (colors, type, radius, shadows)
```

## Design fidelity

`components/theme.py` encodes DESIGN.md: Inter with tabular numerals, deep-teal primary
`#0F766E`, forest-pine ink `#132A1C`, forensic amber `#F97316`, red reserved for confirmed
fraud, 4/8px radii, pill badges, 1px `#E2E8F0` outlines, low-opacity tinted shadows.
Icons use emoji approximations of the Material Symbols (font unavailable offline).

## Interactivity

Period selector · entity search · risk/typology filters & chips · graph zoom/reset/isolate ·
cluster selection driving the Claim Details panel · CSV downloads · verifikator notes with
quick templates · `st.dialog` freeze authorization with session audit trail · plotly charts
(trends, claim-frequency spike, HIN network).
