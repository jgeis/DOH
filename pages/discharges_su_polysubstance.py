from dash import register_page

import discharges_su_polysubstance_dashboard as poly

register_page(
    __name__,
    path="/discharges-su-polysubstance",
    name="Related to Polysubstance Use",
    title="Related to Polysubstance Use",
)

layout = poly.layout
