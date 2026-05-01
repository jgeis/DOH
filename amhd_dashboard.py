# amhd_dashboard.py — AMHD Clients Served page

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
    make_filters_card,
    dropdown_filter,
    format_count_display,
    opts_list,
    sort_opts,
)

register_template()

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


def load_amhd_dataframe():
    sql = load_sql_query("load_amhd")
    df = execute_query(sql)
    print(f"load_amhd returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("AMHD query returned 0 rows.")

    # Normalize source column names across SQL backends/casing.
    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {
        "patid": "client_id",
        "date_of_service": "service_date",
    }
    df = df.rename(columns=rename_map)

    required_cols = {"client_id", "service_date", "service_category", "county"}
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"AMHD query missing required columns: {missing}")

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df = df[df["service_date"].notna()].copy()

    df["year"] = df["service_date"].dt.year.astype("Int64")
    df["month_num"] = df["service_date"].dt.month.astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)

    for col in ["county", "service_category"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df


df_raw = load_amhd_dataframe()

year_opts = sorted(df_raw["year"].dropna().unique().tolist(), reverse=True)
month_nums_present = sorted(df_raw["month_num"].dropna().unique().tolist())
month_opts = [MONTH_NAMES[m] for m in month_nums_present]
service_category_opts = sorted(df_raw["service_category"].dropna().unique().tolist())
county_opts = sorted(df_raw["county"].dropna().unique().tolist())

min_date = df_raw["service_date"].min().date()
max_date = df_raw["service_date"].max().date()


reset_button = dbc.Button(
    "Reset All Filters",
    id="amhd-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Number of Clients Served",
    count_id="amhd-kpi-total",
)

view_toggle_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("View By", className="mb-2 text-center"),
            dbc.RadioItems(
                id="amhd-view-toggle",
                options=[
                    {"label": "Year View", "value": "year"},
                    {"label": "Month View", "value": "month"},
                    {"label": "Day View", "value": "day"},
                ],
                value="year",
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
    card_id="amhd-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Year",
            "amhd-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Month",
            "amhd-month-filter",
            options=opts_list(month_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "County",
            "amhd-county-filter",
            options=opts_list(county_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Service Category",
            "amhd-service-category-filter",
            options=opts_list(service_category_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        (
            "Custom Date Range",
            dcc.DatePickerRange(
                id="amhd-date-range",
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                display_format="YYYY-MM-DD",
                className="mb-0",
            ),
        ),
    ],
)

amhd_sidebar_text = [
    "AMHD client service volume shown by year, month, or date.",
    "Use filters and custom date range to narrow clients served.",
]


def layout():
    left_col = make_left_sidebar(
        kpi_card,
        reset_button,
        filters_card,
        helper_text=amhd_sidebar_text,
        xs=12,
        md=3,
    )

    left_col.children.insert(2, view_toggle_card)

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Number of Clients Served", id="amhd-bar-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="amhd-bar-chart",
                        style={"width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
            html.Div(
                [
                    html.H5("Clients Served by County and Selected Time Period", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="amhd-county-line-chart",
                        style={"width": "100%", "height": "520px"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
        ],
        xs=12,
        md=6,
    )

    right_col = dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(id="amhd-service-category-table", style={"overflowX": "auto"}),
                        xs=12,
                        md=12,
                        className="mb-3",
                    ),
                    dbc.Col(
                        html.Div(id="amhd-year-table", style={"overflowX": "auto"}),
                        xs=12,
                        md=12,
                        className="mb-3",
                    ),
                    dbc.Col(
                        html.Div(id="amhd-county-table", style={"overflowX": "auto"}),
                        xs=12,
                        md=12,
                        className="mb-3",
                    ),
                ],
                className="g-2",
            )
        ],
        xs=12,
        md=3,
    )

    return dbc.Container(
        dbc.Row([left_col, center_col, right_col], className="g-3"),
        fluid=True,
    )


layout = layout()


@callback(
    Output("amhd-year-filter", "value"),
    Output("amhd-month-filter", "value"),
    Output("amhd-service-category-filter", "value"),
    Output("amhd-county-filter", "value"),
    Output("amhd-date-range", "start_date"),
    Output("amhd-date-range", "end_date"),
    Input("amhd-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_amhd_filters(_n_clicks):
    return None, None, None, None, str(min_date), str(max_date)


@callback(
    Output("amhd-bar-chart", "figure"),
    Output("amhd-county-line-chart", "figure"),
    Output("amhd-kpi-total", "children"),
    Output("amhd-service-category-table", "children"),
    Output("amhd-year-table", "children"),
    Output("amhd-county-table", "children"),
    Input("amhd-view-toggle", "value"),
    Input("amhd-year-filter", "value"),
    Input("amhd-month-filter", "value"),
    Input("amhd-service-category-filter", "value"),
    Input("amhd-county-filter", "value"),
    Input("amhd-date-range", "start_date"),
    Input("amhd-date-range", "end_date"),
)
def update_amhd(view, sel_years, sel_months, sel_service_categories, sel_counties, start_date, end_date):
    dff = df_raw.copy()

    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]
    if sel_months:
        dff = dff[dff["month"].isin(sel_months)]
    if sel_service_categories:
        dff = dff[dff["service_category"].isin(sel_service_categories)]
    if sel_counties:
        dff = dff[dff["county"].isin(sel_counties)]

    if start_date:
        dff = dff[dff["service_date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["service_date"] <= pd.to_datetime(end_date)]

    total_clients = dff["client_id"].nunique()

    if view == "year":
        bar_grouped = (
            dff.groupby("year", as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values("year")
        )
        bar_grouped["period"] = bar_grouped["year"].astype(str)
        period_title = "Calendar Year of Service"
        line_grouped = (
            dff.groupby(["year", "county"], as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values(["year", "county"])
        )
        line_grouped["period"] = line_grouped["year"].astype(str)
        line_x = "year"
    elif view == "month":
        bar_grouped = (
            dff.groupby(["year", "month_num", "month"], as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values(["year", "month_num"])
        )
        bar_grouped["period"] = bar_grouped["year"].astype(str) + ", " + bar_grouped["month"]
        period_title = "Month of Service"
        line_grouped = (
            dff.groupby(["year", "month_num", "month", "county"], as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values(["year", "month_num", "county"])
        )
        line_grouped["period"] = line_grouped["year"].astype(str) + ", " + line_grouped["month"]
        line_x = "period"
    else:
        bar_grouped = (
            dff.groupby("service_date", as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values("service_date", ascending=True)
        )
        bar_grouped["period"] = bar_grouped["service_date"].dt.strftime("%Y-%m-%d")
        period_title = "Date of Service"
        line_grouped = (
            dff.groupby(["service_date", "county"], as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values(["service_date", "county"])
        )
        line_grouped["period"] = line_grouped["service_date"].dt.strftime("%Y-%m-%d")
        line_x = "period"

    bar_grouped["label"] = bar_grouped["client_count"].apply(lambda v: f"{int(v):,}")
    bar_height = max(320, len(bar_grouped) * 30)
    y_order = bar_grouped["period"].tolist()

    bar_fig = px.bar(
        bar_grouped,
        x="client_count",
        y="period",
        orientation="h",
        text="label",
        labels={"client_count": "Number of Clients", "period": period_title},
    )
    bar_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Number of Clients",
        yaxis_title=period_title,
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=y_order,
            autorange=True,
        ),
        height=bar_height,
    )
    bar_fig.update_traces(
        marker_color="#22767C",
        texttemplate="%{text}",
        textposition="auto",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:,}<extra></extra>",
    )

    line_grouped = line_grouped.dropna(subset=["county"]).copy()
    if "year" in line_grouped.columns and not line_grouped.empty:
        line_grouped["year"] = line_grouped["year"].astype(int)

    line_fig = px.line(
        line_grouped,
        x=line_x,
        y="client_count",
        color="county",
        markers=True,
        labels={
            "year": "Year",
            "period": period_title,
            "client_count": "Number of Clients",
            "county": "County",
        },
    )
    line_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=120),
        xaxis_title=("Year" if line_x == "year" else period_title),
        yaxis_title="Number of Clients",
        legend_title_text="County",
        legend=dict(
            orientation="h",
            x=0,
            y=-0.22,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.9)",
        ),
        hovermode="closest",
        height=520,
    )
    line_fig.update_traces(
        hovertemplate="%{fullData.name}<br>%{x}<br>Clients: %{y:,}<extra></extra>"
    )

    service_category_tbl = (
        dff.groupby("service_category", as_index=False)["client_id"]
        .nunique()
        .rename(columns={"service_category": "Service Category", "client_id": "Number of Clients"})
        .sort_values("Number of Clients", ascending=False)
        .reset_index(drop=True)
    )

    year_tbl = (
        dff.groupby("year", as_index=False)["client_id"]
        .nunique()
        .rename(columns={"year": "Calendar Year", "client_id": "Number of Clients"})
        .sort_values("Calendar Year", ascending=False)
        .reset_index(drop=True)
    )

    county_order = sort_opts(dff["county"])
    county_tbl = (
        dff.groupby("county", as_index=False)["client_id"]
        .nunique()
        .rename(columns={"county": "County", "client_id": "Number of Clients"})
    )
    county_tbl["County"] = pd.Categorical(county_tbl["County"], categories=county_order, ordered=True)
    county_tbl = county_tbl.sort_values("County").reset_index(drop=True)

    for tbl_df in (service_category_tbl, year_tbl, county_tbl):
        tbl_df["Number of Clients"] = tbl_df["Number of Clients"].apply(format_count_display)

    service_category_table = dbc.Table.from_dataframe(service_category_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")
    year_table = dbc.Table.from_dataframe(year_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")
    county_table = dbc.Table.from_dataframe(county_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")

    return bar_fig, line_fig, format_count_display(total_clients), service_category_table, year_table, county_table
