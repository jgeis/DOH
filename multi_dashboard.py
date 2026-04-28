# multi_dashboard.py
from dash import Dash, html, dcc, page_container, callback, Input, Output
import dash_bootstrap_components as dbc

TAB_PATHS = {
    "/": "Substance Use Dashboards",
    "/discharges": "Any Discharge Related to Substance Use",
    "/sudors": "SUDORS Overdose Deaths",
    "/sudors-polysubstance": "SUDORS Polysubstance Co-occurrence",
    "/dose": "Drug Overdose Surveillance and Epidemiology (DOSE)",
    "/polysubstance": "Related to Polysubstance Use",
    "/wonder-overview": "CDC WONDER Overdose Deaths Overview",
    "/wonder-breakdown": "WONDER Overdose Deaths Breakdown",
    "/cares-call-volume": "Hawaiʻi CARES Crisis Center Volume",
    "/crisis-mobile-outreach": "Referral Destinations for Crisis Mobile Outreach Clients",
}

DEFAULT_PATH = "/discharges"

NAV_GROUPS = {
    "substance": [
        ("/discharges", "Any Discharge Related to Substance Use"),
        ("/polysubstance", "Related to Polysubstance Use"),
        ("/substance-use", "Related to co-occuring SUD (primary) and MH disorder (secondary)"),
       ("/mental-health", "Related to co-occuring MH disorder (primary) and SUD (secondary)"),
        # ("/polysubstance-alt", "Polysubstance Alternates"),
    ],
    # Example future group:
    # "new-visuals": [
    #     ("/new-overview", "New Visuals Overview"),
    #     ("/new-trends", "New Visuals Trends"),
    #     ("/new-details", "New Visuals Details"),
    # ],
}

ROUTE_TO_GROUP = {
    "/discharges": "substance",
    "/polysubstance": "substance",
    "/substance-use": "substance",
    "/mental-health": "substance",
    # "/polysubstance-alt": "substance",
    # Example future route mapping:
    # "/new-overview": "new-visuals",
    # "/new-trends": "new-visuals",
    # "/new-details": "new-visuals",
}

SUDORS_NAV_GROUPS = {
    "substance": [
        ("/sudors", "SUDORS Overdose Deaths"),
        ("/sudors-polysubstance", "SUDORS with Polysubstance Use"),
        ("/wonder-overview", "CDC WONDER Overdose Deaths Overview"),
        ("/wonder-breakdown", "WONDER Breakdown"),
    ],
}

SUDORS_ROUTE_TO_GROUP = {
    "/sudors": "substance",
    "/sudors-polysubstance": "substance",
    "/wonder-overview": "substance",
    "/wonder-breakdown": "substance",
}

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
)
server = app.server
app.title = "Substance Use Dashboards"

app.layout = dbc.Container(
    [
        html.A(
            "Skip to navigation",
            href="#top-nav",
            className="visually-hidden-focusable",
            tabIndex=0,
        ),

        dcc.Location(id="url", refresh=False),

        html.Div(
            html.Div(id="top-nav", className="tabs"),
            id="top-nav-wrapper",
            className="mb-2",
        ),

        html.H2(id="page-title", className="text-center mb-2"),

        html.Div(page_container, style={"marginTop": "12px"}),
    ],
    fluid=True,
)

@callback(
    Output("top-nav", "children"),
    Output("top-nav-wrapper", "style"),
    Output("page-title", "children"),
    Input("url", "pathname"),
)
def update_active_tab(pathname):
    """Render the active tab group for the current route and set title."""
    if not pathname:
        pathname = "/"

    group_name = ROUTE_TO_GROUP.get(pathname)
    sudors_group_name = SUDORS_ROUTE_TO_GROUP.get(pathname)
    tabs = []

    if group_name in NAV_GROUPS:
        tabs = [
            html.A(
                label,
                href=path,
                className=("tab tab--selected" if pathname == path else "tab"),
            )
            for path, label in NAV_GROUPS[group_name]
        ]
        nav_style = {}
    elif sudors_group_name in SUDORS_NAV_GROUPS:
        tabs = [
            html.A(
                label,
                href=path,
                className=("tab tab--selected" if pathname == path else "tab"),
            )
            for path, label in SUDORS_NAV_GROUPS[sudors_group_name]
        ]
        nav_style = {}
    else:
        nav_style = {"display": "none"}

    title = TAB_PATHS.get(pathname, "Substance Use Dashboards")

    return tabs, nav_style, title

if __name__ == "__main__":
    app.run(debug=True)
