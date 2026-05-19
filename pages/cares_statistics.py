from dash import register_page

import cares_statistics_dashboard

register_page(
    __name__,
    path="/cares-statistics",
    name="Hawai'i CARES 988 Statistics",
    title="Hawai'i CARES 988 Statistics",
)

layout = cares_statistics_dashboard.layout
