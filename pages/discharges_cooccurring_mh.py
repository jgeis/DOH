from dash import register_page

import discharges_cooccurring_dashboard as mh_co_dash

register_page(
    __name__,
    path="/discharges-cooccurring-mh",
    name="Related to co-occurring mental health and substance use disorders",
    title="Related to co-occurring mental health and substance use disorders",
)

layout = mh_co_dash.layout()
