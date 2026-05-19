from dash import register_page

import discharges_su_co_mh_sud_dashboard as mh_co_mental_dash

register_page(
    __name__,
    path="/discharges-mh-co-mh-sud",
    name="Related to co-occuring MH disorder (primary) and SUD (secondary)",
    title="Related to co-occuring MH disorder (primary) and SUD (secondary)",
)

layout = mh_co_mental_dash.layout