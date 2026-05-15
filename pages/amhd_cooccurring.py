from dash import register_page

import amhd_cooccurring_dashboard

register_page(
    __name__,
    path="/amhd-cooccurring",
    name="AMHD Co-Occurring Clients Served",
    title="AMHD Co-Occurring Clients Served",
)

layout = amhd_cooccurring_dashboard.layout
