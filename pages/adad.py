from dash import register_page

import adad_dashboard

register_page(
    __name__,
    path="/adad",
    name="ADAD Clients Served",
    title="ADAD Clients Served",
)

layout = adad_dashboard.layout
