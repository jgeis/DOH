from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# Import the exported layouts
from app_alt import layout as alt_layout
from polysubstance_dashboard import layout as poly_layout
# If you used the fallback-friendly file I gave you:
# from cooccurring_dashboard_db import layout as co_layout

# If your co-occurring file is named differently, adjust the import above.
try:
    from cooccurring_dashboard_db import layout as co_layout
    HAS_CO = True
except Exception:
    HAS_CO = False
    co_layout = html.Div(
        "Co-occurring dashboard not available (cooccurring_dashboard_db.py not found)."
    )

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Substance Use Dashboards"

# IMPORTANT for deployment (Render/Gunicorn, etc.)
server = app.server

tabs = [
    dcc.Tab(
        label="Discharges related to substance use",
        value="alt",
        className="tab",
        selected_className="tab--selected",
    ),
    dcc.Tab(
        label="Related to polysubstance use",
        value="poly",
        className="tab",
        selected_className="tab--selected",
    ),
]
# Add co-occurring tab if available
if HAS_CO:
    tabs.append(
        dcc.Tab(
            label="Co-occurring: SUD × MH (secondary)",
            value="co",
            className="tab",
            selected_className="tab--selected",
        )
    )

app.layout = html.Div(
    [
        dcc.Tabs(id="view-tabs", value="alt", children=tabs, className="tabs"),
        html.Div(id="view-container", style={"marginTop": "12px"}),
    ]
)

@callback(Output("view-container", "children"), Input("view-tabs", "value"))
def render_view(value):
    if value == "poly":
        return poly_layout
    if value == "co" and HAS_CO:
        return co_layout
    return alt_layout

if __name__ == "__main__":
    app.run(debug=True)
