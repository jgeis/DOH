from dash import register_page

import discharges_su_dashboard

register_page(
    __name__,
    path="/discharges-su",
    name="Any Discharge Related to Substance Use",
    title="Any Discharge Related to Substance Use",
)

layout = discharges_su_dashboard.layout
