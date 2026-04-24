from dash import register_page

import discharges_dashboard

register_page(
    __name__,
    path="/discharges",
    name="Any Discharge Related to Substance Use",
    title="Any Discharge Related to Substance Use",
)

layout = discharges_dashboard.layout
