from dash import register_page

import mental_health_primary_dashboard as mental_dash

register_page(
    __name__,
    path="/mental-health",
    name="Related to co-occuring MH disorder (primary) and SUD (secondary)",
    title="Related to co-occuring MH disorder (primary) and SUD (secondary)",
)

layout = mental_dash.layout
