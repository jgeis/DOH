from dash import register_page

import sudors_polysubstance_dashboard as sudo_poly

register_page(
    __name__,
    path="/sudors-polysubstance",
    name="SUDORS with Polysubstance Use",
    title="SUDORS with Polysubstance Use",
)

layout = sudo_poly.layout
