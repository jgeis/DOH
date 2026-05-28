from dash import register_page

import discharges_su_co_sud_mh_dashboard as su_sub_dash

register_page(
    __name__,
    path="/discharges-su-co-sud-mh",
    name="Related to co-occurring SUD (primary) and MH disorder (secondary)",
    title="Related to co-occurring SUD (primary) and MH disorder (secondary)",
)

layout = su_sub_dash.layout
