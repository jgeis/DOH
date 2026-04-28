from dash import register_page

import crisis_mobile_outreach_dashboard

register_page(
    __name__,
    path="/crisis-mobile-outreach",
    name="Crisis Mobile Outreach Referrals",
    title="Referral Destinations for Crisis Mobile Outreach Clients",
)

layout = crisis_mobile_outreach_dashboard.layout
