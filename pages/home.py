from dash import register_page, html
import dash_bootstrap_components as dbc

register_page(
    __name__,
    path="/",
    name="Home",
    title="Substance Use Dashboards",
)

layout = dbc.Container(
    [
        html.H4("Dashboard Pages", className="mb-3"),
        html.P("Choose a page:"),
        dbc.ListGroup(
            [
                dbc.ListGroupItem(html.A("Any Discharge Related to Substance Use", href="/discharges")),
                dbc.ListGroupItem(html.A("SUDORS", href="/sudors")),
                dbc.ListGroupItem(html.A("Drug Overdose Surveillance and Epidemiology (DOSE)", href="/dose")),
                dbc.ListGroupItem(html.A("Related to Polysubstance Use", href="/polysubstance")),
                dbc.ListGroupItem(html.A("CARES call volume", href="/cares-call-volume")),
                dbc.ListGroupItem(html.A("Referral Destinations for Crisis Mobile Outreach Clients", href="/crisis-mobile-outreach")),
                dbc.ListGroupItem(html.A("Alcohol and Drug Abuse Division (ADAD)", href="/adad")),
                dbc.ListGroupItem(html.A("Adult Mental Health Division (AMHD)", href="/amhd")),
                dbc.ListGroupItem(html.A("Child and Adolescent Mental Health Division (CAMHD)", href="/camhd")),
                dbc.ListGroupItem(html.A("Licensed Crisis Residential Services (LCRS)", href="/lcrs")),

            ]
        ),
    ],
    fluid=True,
    className="p-2",
)
