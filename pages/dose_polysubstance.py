from dash import register_page

import dose_polysubstance_dashboard

register_page(
    __name__,
    path="/dose-polysubstance",
    name="DOSE Polysubstance Co-occurrence",
    title="DOSE Polysubstance Co-occurrence",
)

layout = dose_polysubstance_dashboard.layout
