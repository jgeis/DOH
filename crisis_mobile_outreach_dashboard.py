# crisis_mobile_outreach_dashboard.py — Crisis Mobile Outreach referrals page

import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback
import plotly.express as px

from config import USE_MSSQL
from db_utils import execute_query
from dashboard_utils import (
    load_sql_query,
    graph_block,
    make_kpi_card,
    make_left_sidebar,
    make_filters_card,
    dropdown_filter,
    format_count_display,
    opts_list,
    apply_standard_bar_layout,
)
from theme import register_template

register_template()


def load_cmo_referrals_dataframe():
    """Load referral destinations for Crisis Mobile Outreach over the past 6 months."""
    sql = load_sql_query("load_crisis_mobile_outreach")

    # The named query is authored in T-SQL. For local SQLite runs, adjust only the date expression.
    if not USE_MSSQL:
        sql = sql.replace(
            "DATEADD(month, -6, CAST(GETDATE() AS DATE))",
            "date('now', '-6 months')",
        )

    df = execute_query(sql)
    print(f"load_crisis_mobile_outreach returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("load_crisis_mobile_outreach returned 0 rows.")

    df["referral_destination"] = df["referral_destination"].fillna("Unknown")
    df["ct"] = pd.to_numeric(df["ct"], errors="coerce").fillna(0).astype(int)
    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce").fillna(0.0)
    return df.sort_values("ct", ascending=False).reset_index(drop=True)


def load_cmo_last_updated_value():
    """Fetch the most recent DispatchDate from the source table for Last Updated."""
    query_name = (
        "load_crisis_mobile_outreach_last_updated"
        if USE_MSSQL
        else "load_crisis_mobile_outreach_last_updated_sqlite"
    )
    sql = load_sql_query(query_name)
    result = execute_query(sql)
    if result.empty or "last_updated" not in result.columns:
        return None

    parsed = pd.to_datetime(result.iloc[0]["last_updated"], errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


df_raw = load_cmo_referrals_dataframe()
referral_opts = sorted(df_raw["referral_destination"].dropna().unique().tolist())
last_updated_value = load_cmo_last_updated_value()

# ----------------------------
# UI Components
# ----------------------------

reset_button = dbc.Button(
    "Reset All Filters",
    id="cmo-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Distinct Crisis Mobile Outreach Clients (Past 6 Months)",
    count_id="cmo-kpi-total",
)

filters_card = make_filters_card(
    card_id="cmo-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Referral Destination",
            "cmo-destination-filter",
            options=opts_list(referral_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
    ],
)

from section_texts import SECTION_TEXTS
sidebar_text = SECTION_TEXTS.get("crisis_mobile_outreach", [])


# ----------------------------
# Layout
# ----------------------------

def layout():
    left_col = make_left_sidebar(
        kpi_card,
        reset_button,
        filters_card,
        helper_text=sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

    center_col = dbc.Col(
        [
            graph_block("cmo-referral-bar", "Referral Destinations (Past 6 Months)", "520px"),
            html.P(
                "Bar chart showing referral destinations for Crisis Mobile Outreach clients over the past 6 months.",
                className="visually-hidden",
            ),
        ],
        xs=12,
        md=6,
    )

    right_col = dbc.Col(
        [
            html.H5("Referral Destination Summary", className="mb-2"),
            html.Div(id="cmo-summary-table", style={"overflowX": "auto"}),
        ],
        xs=12,
        md=3,
    )

    return dbc.Container(
        dbc.Row([left_col, center_col, right_col]),
        fluid=True,
    )


# ----------------------------
# Callbacks
# ----------------------------

@callback(
    Output("cmo-destination-filter", "value"),
    Input("cmo-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_cmo_filters(_n_clicks):
    return None


@callback(
    Output("cmo-kpi-total", "children"),
    Output("cmo-referral-bar", "figure"),
    Output("cmo-summary-table", "children"),
    Input("cmo-destination-filter", "value"),
)
def update_cmo_dashboard(selected_destinations):
    dff = df_raw.copy()

    if selected_destinations:
        dff = dff[dff["referral_destination"].isin(selected_destinations)]

    total_clients = int(dff["ct"].sum())
    dff = dff.sort_values("ct", ascending=False).copy()

    # For horizontal bar charts, categoryarray[0] is rendered at the bottom.
    # Reverse here so the highest-count destination appears at the top.
    y_order = dff["referral_destination"].tolist()[::-1]

    fig = px.bar(
        dff,
        x="ct",
        y="referral_destination",
        orientation="h",
        text="ct",
        labels={
            "ct": "Number of Clients",
            "referral_destination": "Referral Destination",
        },
    )
    apply_standard_bar_layout(
        fig,
        xaxis=dict(title="Number of Clients"),
        yaxis=dict(title="Referral Destination", categoryorder="array", categoryarray=y_order),
        height=max(360, len(dff) * 30),
    )
    fig.update_traces(
        marker_color="#22767C",
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        customdata=dff[["percentage"]],
        hovertemplate="%{y}: %{x:,} clients (%{customdata[0]:.2f}%)<extra></extra>",
    )

    table_df = dff[["referral_destination", "ct", "percentage"]].rename(
        columns={
            "referral_destination": "Referral Destination",
            "ct": "Distinct Clients",
            "percentage": "Percent of Total",
        }
    )
    table_df["Distinct Clients"] = table_df["Distinct Clients"].apply(format_count_display)
    table_df["Percent of Total"] = table_df["Percent of Total"].map(lambda v: f"{v:.2f}%")

    table = dbc.Table.from_dataframe(
        table_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )

    return format_count_display(total_clients), fig, table
