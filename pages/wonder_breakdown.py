from dash import register_page

import wonder_breakdown_dashboard as wonder_dash

register_page(
    __name__,
    path="/wonder-breakdown",
    name="WONDER Breakdown",
    title="WONDER Breakdown",
)

layout = wonder_dash.layout
