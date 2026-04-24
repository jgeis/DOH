from dash import register_page

import dose_dashboard

register_page(
    __name__,
    path="/dose",
    name="Drug Overdose Surveillance and Epidemiology (DOSE)",
    title="Drug Overdose Surveillance and Epidemiology (DOSE)",
)

layout = dose_dashboard.layout
