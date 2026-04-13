from dash import register_page

import wonder_overview_dashboard as wonder_dash

register_page(
    __name__,
    path="/wonder-overview",
    name="CDC WONDER Overdose Deaths Overview",
    title="CDC WONDER Overdose Deaths Overview",
)

layout = wonder_dash.layout
