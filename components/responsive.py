"""Shared responsive rules, loaded after the base theme and topbar rules."""

CSS = """
<style>
/* Let long identifiers wrap without changing table data or hiding overflow. */
.j-topbar, .j-pagehead, .j-demo-notice {min-width:0;box-sizing:border-box}
.j-pagehead > div, .j-topbar > div {min-width:0}
[data-testid="stHeading"], [data-testid="stCaptionContainer"],
.j-body, .j-crumb, .j-demo-notice {overflow-wrap:anywhere}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {max-width:100%;min-width:0}

@media(max-width:900px){
  /* Stack work panels before they become too narrow to read. */
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:1rem}
  [data-testid="stMain"] [data-testid="stColumn"] {
    width:100% !important;flex:1 1 100% !important;min-width:0 !important;
  }
  .j-pagehead {flex-direction:column;gap:12px !important}
  .j-pagehead-right {text-align:left !important;max-width:100%}
}

@media(max-width:640px){
  .stApp [data-testid="stMainBlockContainer"],
  .stApp:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stMainBlockContainer"] {
    padding-left:16px !important;padding-right:16px !important;
    width:100% !important;max-width:100% !important;box-sizing:border-box;
  }
  .j-topbar {flex-wrap:wrap;gap:10px}
  .j-topbar > div {max-width:100%;flex-wrap:wrap}
  .j-workflow ol {grid-auto-flow:row;grid-template-columns:repeat(2,minmax(0,1fr))}
  .j-workflow li {min-height:44px;box-sizing:border-box}
  [data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stButton"]),
  [data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stDownloadButton"]),
  [data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]),
  [data-testid="stMain"] [data-testid="stButton"],
  [data-testid="stMain"] [data-testid="stDownloadButton"],
  [data-testid="stMain"] [data-testid="stFormSubmitButton"] {width:100% !important}
  [data-testid="stMain"] [data-testid="stButton"] button,
  [data-testid="stMain"] [data-testid="stDownloadButton"] button,
  [data-testid="stMain"] [data-testid="stFormSubmitButton"] button {
    width:100%;min-height:44px;height:auto;white-space:normal;padding:10px 12px;
  }
  [data-testid="stMain"] button p {white-space:normal;overflow-wrap:anywhere}
  [data-testid="stMain"] input, [data-testid="stMain"] textarea {font-size:16px !important}
  [role="tablist"] {max-width:100%;overflow-x:auto}
  [role="tab"] {flex-shrink:0;min-height:44px}
  [role="dialog"] {max-width:calc(100vw - 24px) !important;box-sizing:border-box}
}
</style>
"""
