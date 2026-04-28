from dash import register_page

import cares_dashboard

register_page(
    __name__,
    path="/cares-call-volume",
    name="Hawaiʻi CARES Crisis Center Volume",
    title="Hawaiʻi CARES Crisis Center Volume",
)

layout = cares_dashboard.layout
