from dash import register_page

import sicm_dashboard

register_page(
    __name__,
    path="/sicm",
    name="Stabilization Bed Facilities Occupancy Rates",
    title="Stabilization Bed Facilities Occupancy Rates",
)

layout = sicm_dashboard.layout