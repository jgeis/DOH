from dash import register_page

import discharges_mh_dashboard

register_page(
    __name__,
    path="/discharges-mh",
    name="Any Discharge Related to Mental Health Disorders",
    title="Any Discharge Related to Mental Health Disorders",
)

layout = discharges_mh_dashboard.layout
