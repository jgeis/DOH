from dash import register_page

import camhd_cooccurring_dashboard

register_page(
    __name__,
    path="/camhd-cooccurring",
    name="CAMHD Co-Occurring Clients Served",
    title="CAMHD Co-Occurring Clients Served",
)

layout = camhd_cooccurring_dashboard.layout
