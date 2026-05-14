from dash import register_page

import camhd_dashboard

register_page(
    __name__,
    path="/camhd",
    name="CAMHD Clients Served",
    title="CAMHD Clients Served",
)

layout = camhd_dashboard.layout