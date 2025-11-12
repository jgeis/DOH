# multi_dashboard.py
from dash import Dash, html, dcc, callback, Input, Output, no_update, ctx
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server
app.title = "Substance Use Dashboards"

# Import tab modules AFTER app is created
import app_alt as alt
try:
    import polysubstance_dashboard as poly
except ModuleNotFoundError:
    import polysubstance_dashboard as poly

try:
    import cooccurring_dashboard as co
    HAS_CO = True
except Exception:
    HAS_CO = False

# --- UI: top navigation that IS tabbable ---
top_nav = html.Nav(
    [
        html.Button("Go to Discharges", id="nav-to-alt",
                    className="btn btn-outline-primary btn-sm me-2",
                    title="Alt+Shift+D", accessKey="d"),
        html.Button("Go to Polysubstance", id="nav-to-poly",
                    className="btn btn-outline-primary btn-sm me-2",
                    title="Alt+Shift+P", accessKey="p"),
        *( [html.Button("Go to Co-occurring", id="nav-to-co",
                        className="btn btn-outline-secondary btn-sm",
                        title="Alt+Shift+C", accessKey="c")] if HAS_CO else [] )
    ],
    className="mb-2"
)

# --- Tabs remain for mouse users; buttons control them ---
tabs = [
    dcc.Tab(label="Discharges related to substance use", value="alt",
            className="tab", selected_className="tab--selected"),
    dcc.Tab(label="Related to polysubstance use", value="poly",
            className="tab", selected_className="tab--selected"),
]
if HAS_CO:
    tabs.append(
        dcc.Tab(label="Co-occurring: SUD × MH (secondary)", value="co",
                className="tab", selected_className="tab--selected")
    )

app.layout = dbc.Container(
    [
        # First focus stop: skip to nav
        html.A("Skip to navigation", href="#top-nav",
               className="visually-hidden-focusable", tabIndex=0),

        # Tabbable nav buttons FIRST
        html.Div(top_nav, id="top-nav"),

        # Keep the Tabs for normal UI
        dcc.Tabs(id="view-tabs", value="alt", children=tabs, className="tabs"),

        # Title gets updated per tab
        html.H2(id="page-title", className="text-center mb-2"),

        # Where tab content renders
        html.Div(id="view-container", style={"marginTop": "12px"}),
    ],
    fluid=True,
)

# --- Wire buttons -> switch active tab ---
@callback(
    Output("view-tabs", "value"),
    Input("nav-to-alt", "n_clicks"),
    Input("nav-to-poly", "n_clicks"),
    Input("nav-to-co", "n_clicks") if HAS_CO else Input("view-tabs", "value"),
    prevent_initial_call=True,
)
def switch_tabs(n_alt, n_poly, n_co_or_value):
    trig = ctx.triggered_id
    if trig == "nav-to-alt":
        return "alt"
    if trig == "nav-to-poly":
        return "poly"
    if HAS_CO and trig == "nav-to-co":
        return "co"
    return no_update

# --- Render selected tab + title ---
@callback(
    Output("view-container", "children"),
    Output("page-title", "children"),
    Input("view-tabs", "value"),
)
def render_view(value):
    if value == "poly":
        return poly.layout, "Related to polysubstance use"
    if value == "co" and HAS_CO:
        return co.layout, "Co-occurring: SUD × MH (secondary)"
    return alt.layout, ""

if __name__ == "__main__":
    app.run(debug=True)
