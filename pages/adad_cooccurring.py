from dash import register_page

import adad_cooccurring_dashboard

register_page(
    __name__,
    path="/adad-cooccurring",
    name="ADAD Co-Occurring Clients Served",
    title="ADAD Co-Occurring Clients Served",
)

layout = adad_cooccurring_dashboard.layout