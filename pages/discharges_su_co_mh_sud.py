from dash import register_page

import discharges_su_co_mh_sud_dashboard as su_co_mental_dash

register_page(
    __name__,
    path="/discharges-su-co-mh-sud",
    name="Related to co-occurring MH disorder (primary) and SUD (secondary)",
    title="Related to co-occurring MH disorder (primary) and SUD (secondary)",
)

layout = su_co_mental_dash.layout
