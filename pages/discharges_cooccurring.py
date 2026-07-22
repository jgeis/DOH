from dash import register_page

import discharges_cooccurring_dashboard as su_co_dash

register_page(
    __name__,
    path="/discharges-cooccurring",
    name="Related to co-occurring substance use and mental health disorders",
    title="Related to co-occurring substance use and mental health disorders",
)

layout = su_co_dash.layout
