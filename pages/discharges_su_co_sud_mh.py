from dash import register_page

import discharges_su_co_sud_mh_dashboard as sub_dash

register_page(
    __name__,
    path="/discharges-su-co-sud-mh",
    name="Related to co-occuring SUD (primary) and MH disorder (secondary)",
    title="Related to co-occuring SUD (primary) and MH disorder (secondary)",
)

layout = sub_dash.layout
