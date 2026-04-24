from dash import register_page

import discharges_dashboard

register_page(
    __name__,
    path="/discharges",
    name="Discharges related to substance use",
    title="Discharges related to substance use",
)

layout = discharges_dashboard.layout
