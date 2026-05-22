# camhd_cooccurring_dashboard.py — CAMHD Co-Occurring Clients Served page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
from dashboard_utils import (
    load_sql_query,
    make_kpi_card,
    make_filters_card,
    make_last_updated_block,
    compute_last_updated_value,
    compute_adaptive_horizontal_bar_height,
    dropdown_filter,
    format_count_display,
    opts_list,
    apply_standard_bar_layout,
    apply_standard_single_series_bar_trace,
)

register_template()

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


def load_camhd_cooccurring_dataframe():
    sql = load_sql_query("load_camhd_cooccurring")
    df = execute_query(sql)
    print(f"load_camhd_cooccurring returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("CAMHD co-occurring query returned 0 rows.")

    if "service_date" not in df.columns and "date" in df.columns:
        df = df.rename(columns={"date": "service_date"})

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df = df[df["service_date"].notna()].copy()

    df["year"] = df["service_date"].dt.year.astype("Int64")
    df["month_num"] = df["service_date"].dt.month.astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)

    return df


df_raw = load_camhd_cooccurring_dataframe()
last_updated_value = compute_last_updated_value(df_raw)

year_opts = sorted(df_raw["year"].dropna().unique().tolist(), reverse=True)
min_date = df_raw["service_date"].min().date()
max_date = df_raw["service_date"].max().date()


kpi_card = make_kpi_card(
    label="Number of Distinct Clients",
    count_id="camhd-cooccurring-kpi-total",
)

view_toggle_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("View By", className="mb-2 text-center"),
            dbc.RadioItems(
                id="camhd-cooccurring-view-toggle",
                options=[
                    {"label": "Year View", "value": "year"},
                    {"label": "Month View", "value": "month"},
                    {"label": "Day View", "value": "day"},
                ],
                value="year",
                class_name="spaced-radio-buttons d-flex justify-content-center gap-3",
                input_class_name="btn-check",
                label_class_name="btn btn-outline-success",
                label_checked_class_name="btn-success text-white active",
            ),
        ]
    ),
    className="mb-3",
)

filters_card = make_filters_card(
    card_id="camhd-cooccurring-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Year",
            "camhd-cooccurring-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        (
            "Custom Date Range",
            dcc.DatePickerRange(
                id="camhd-cooccurring-date-range",
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


def layout():
    last_updated_block = make_last_updated_block(last_updated_value)
    left_col = dbc.Col(
        [
            kpi_card,
            view_toggle_card,
            filters_card,
            last_updated_block,
        ],
        xs=12,
        md=3,
    )

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Number of Clients Served", id="camhd-cooccurring-bar-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="camhd-cooccurring-bar-chart",
                        style={"width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
        ],
        xs=12,
        md=9,
    )

    return dbc.Container(
        dbc.Row([left_col, center_col], className="g-3"),
        fluid=True,
    )


layout = layout()


@callback(
    Output("camhd-cooccurring-bar-chart", "figure"),
    Output("camhd-cooccurring-kpi-total", "children"),
    Input("camhd-cooccurring-view-toggle", "value"),
    Input("camhd-cooccurring-year-filter", "value"),
    Input("camhd-cooccurring-date-range", "start_date"),
    Input("camhd-cooccurring-date-range", "end_date"),
)
def update_camhd_cooccurring(view, sel_years, start_date, end_date):
    dff = df_raw.copy()

    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]

    if start_date:
        dff = dff[dff["service_date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["service_date"] <= pd.to_datetime(end_date)]

    total_clients = dff["client_id"].nunique()

    if view == "year":
        grouped = (
            dff.groupby("year", as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values("year")
        )
        grouped["period"] = grouped["year"].astype(str)
        y_title = "Calendar Year of Service"
    elif view == "month":
        grouped = (
            dff.groupby(["year", "month_num", "month"], as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values(["year", "month_num"])
        )
        grouped["period"] = grouped["year"].astype(str) + ", " + grouped["month"]
        y_title = "Month of Service"
    else:
        grouped = (
            dff.groupby("service_date", as_index=False)["client_id"]
            .nunique()
            .rename(columns={"client_id": "client_count"})
            .sort_values("service_date", ascending=True)
        )
        grouped["period"] = grouped["service_date"].dt.strftime("%Y-%m-%d")
        y_title = "Date of Service"

    grouped["label"] = grouped["client_count"].apply(format_count_display)
    chart_height = compute_adaptive_horizontal_bar_height(
        len(grouped),
    )
    y_order = grouped["period"].tolist()

    bar_fig = px.bar(
        grouped,
        x="client_count",
        y="period",
        orientation="h",
        text="label",
        labels={"client_count": "Number of Clients", "period": y_title},
    )
    apply_standard_bar_layout(
        bar_fig,
        xaxis=dict(title="Number of Clients"),
        yaxis=dict(
            title=y_title,
            type="category",
            categoryorder="array",
            categoryarray=y_order,
            autorange=True,
        ),
        height=chart_height,
    )
    apply_standard_single_series_bar_trace(bar_fig)
    bar_fig.update_traces(hovertemplate="%{y}: %{text}<extra></extra>")

    return bar_fig, format_count_display(total_clients)
