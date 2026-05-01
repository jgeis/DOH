from dash import register_page

import amhd_dashboard

register_page(
    __name__,
    path="/amhd",
    name="AMHD Clients Served",
    title="AMHD Clients Served",
)

layout = amhd_dashboard.layout
