from dash import register_page

import lcrf_dashboard

register_page(
    __name__,
    path="/lcrs",
    name="Licensed Crisis Residential Facility Occupancy Rates",
    title="Licensed Crisis Residential Facility Occupancy Rates",
)

layout = lcrf_dashboard.layout