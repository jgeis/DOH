# cares_dashboard.py — Hawaiʻi CARES Crisis Center Volume page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
from dashboard_utils import (
    load_sql_query,
    make_kpi_card,
    make_left_sidebar,
    compute_last_updated_value,
    make_filters_card,
    dropdown_filter,
    format_count_display,
    opts_list,
)

register_template()

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

# ----------------------------
# Data load
# ----------------------------

def load_cares_dataframe():
    sql = load_sql_query("load_cares_calls")
    df = execute_query(sql)
    print(f"load_cares_calls returned {len(df):,} rows")
    if df.empty:
        raise RuntimeError("cares_calls query returned 0 rows.")
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    df["year"] = df["day"].dt.year.astype("Int64")
    df["month_num"] = df["day"].dt.month.astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)
    return df


df_raw = load_cares_dataframe()
last_updated_value = compute_last_updated_value(df_raw)

year_opts = sorted(df_raw["year"].dropna().unique().tolist())
month_nums_present = sorted(df_raw["month_num"].dropna().unique().tolist())
month_opts = [MONTH_NAMES[m] for m in month_nums_present]
crisis_line_opts = sorted(df_raw["origin_of_call"].dropna().unique().tolist())

# ----------------------------
# UI Components
# ----------------------------

reset_button = dbc.Button(
    "Reset All Filters",
    id="cares-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Total Crisis Center Contacts",
    count_id="cares-kpi-total",
)

# "Year View / Month View" toggle rendered as a pill button group.
view_toggle_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("View By", className="mb-2 text-center"),
            dbc.RadioItems(
                id="cares-view-toggle",
                options=[
                    {"label": "Year", "value": "year"},
                    {"label": "Month", "value": "month"},
                ],
                value="month",
                class_name="btn-group d-flex justify-content-center",
                input_class_name="btn-check",
                label_class_name="btn btn-outline-success",
                label_checked_class_name="btn-success text-white active",
            ),
        ]
    ),
    className="mb-3",
)

filters_card = make_filters_card(
    card_id="cares-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Calendar Years",
            "cares-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Month",
            "cares-month-filter",
            options=opts_list(month_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Crisis Line",
            "cares-crisis-line-filter",
            options=opts_list(crisis_line_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
    ],
)

from section_texts import SECTION_TEXTS
cares_sidebar_text = SECTION_TEXTS.get("cares", [])

# ----------------------------
# Layout
# ----------------------------

def layout():
    left_col = make_left_sidebar(
        kpi_card,
        reset_button,
        filters_card,
        helper_text=cares_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )
    left_col.children.insert(2, view_toggle_card)

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Number of Calls", id="cares-bar-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="cares-bar-chart",
                        style={"width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
            html.P(
                "Horizontal bar chart showing total crisis center contacts.",
                className="visually-hidden",
            ),
        ],
        xs=12, md=6,
    )

    right_col = dbc.Col(
        [
            html.H5("Calls by Crisis Line", className="mb-2"),
            html.Div(
                id="cares-crisis-table",
                style={"overflowX": "auto"},
            ),
        ],
        xs=12, md=3,
    )

    return dbc.Container(
        dbc.Row([left_col, center_col, right_col]),
        fluid=True,
    )

# ----------------------------
# Callbacks
# ----------------------------

@callback(
    Output("cares-year-filter", "value"),
    Output("cares-month-filter", "value"),
    Output("cares-crisis-line-filter", "value"),
    Input("cares-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_cares_filters(_n_clicks):
    return None, None, None


@callback(
    Output("cares-bar-chart", "figure"),
    Output("cares-kpi-total", "children"),
    Output("cares-crisis-table", "children"),
    Input("cares-view-toggle", "value"),
    Input("cares-year-filter", "value"),
    Input("cares-month-filter", "value"),
    Input("cares-crisis-line-filter", "value"),
)
def update_cares(view, sel_years, sel_months, sel_crisis):
    dff = df_raw.copy()

    # Apply filters (None / empty → show all)
    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]
    if sel_months:
        dff = dff[dff["month"].isin(sel_months)]
    if sel_crisis:
        dff = dff[dff["origin_of_call"].isin(sel_crisis)]

    total = int(dff["count_of_users"].sum())

    # --- Bar chart ---
    if view == "year":
        grouped = (
            dff.groupby("year", as_index=False)["count_of_users"]
            .sum()
            .sort_values("year", ascending=True)
        )
        grouped["y_label"] = grouped["year"].astype(str)
        y_col = "y_label"
        y_title = "Year"
    else:
        grouped = (
            dff.groupby(["year", "month_num", "month"], as_index=False)["count_of_users"]
            .sum()
            .sort_values(["year", "month_num"], ascending=True)
        )
        grouped["y_label"] = grouped["year"].astype(str) + ", " + grouped["month"]
        y_col = "y_label"
        y_title = "Year, Month"

    n_bars = len(grouped)
    # Give each bar ~32px of height, with a minimum floor.
    chart_height = max(320, n_bars * 32)

    # Build the display order: categoryarray[0] = bottom, last = top.
    # Ascending order means oldest at bottom, newest at top.
    y_order = grouped[y_col].tolist()

    fig = px.bar(
        grouped,
        x="count_of_users",
        y=y_col,
        orientation="h",
        text="count_of_users",
        labels={"count_of_users": "Number of Calls", y_col: y_title},
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Number of Calls",
        yaxis_title=y_title,
        yaxis=dict(categoryorder="array", categoryarray=y_order),
        height=chart_height,
    )
    fig.update_traces(
        marker_color="#22767C",
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:,}<extra></extra>",
    )

    # --- Crisis line table ---
    crisis_totals = (
        dff.groupby("origin_of_call", as_index=False)["count_of_users"]
        .sum()
        .rename(columns={"origin_of_call": "Crisis Line", "count_of_users": "Total Calls"})
        .sort_values("Total Calls", ascending=False)
    )
    crisis_totals["Total Calls"] = crisis_totals["Total Calls"].apply(format_count_display)

    table = dbc.Table.from_dataframe(
        crisis_totals,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )

    return fig, format_count_display(total), table
