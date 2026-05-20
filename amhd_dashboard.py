# amhd_dashboard.py — AMHD Clients Served page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from functools import lru_cache
from time import perf_counter
from config import USE_MSSQL
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
def _sql_quote(text):
    return "'" + str(text).replace("'", "''") + "'"


def _year_date_range_clauses(years_key):
    """Build SARGable service_date range predicates for selected years."""
    clauses = []
    for year_value in years_key:
        start_date = f"{int(year_value)}-01-01"
        next_year = f"{int(year_value) + 1}-01-01"
        clauses.append(f"(service_date >= {_sql_quote(start_date)} AND service_date < {_sql_quote(next_year)})")
    return clauses


@lru_cache(maxsize=512)
def _amhd_query_context_cached(
    years_key,
    service_categories_key,
    start_date,
    end_date,
):
    """Build the named-query substitution context for the current AMHD filters."""
    year_expr = "CAST(service_year AS INTEGER)"
    month_period_expr = "DATEFROMPARTS(YEAR(service_date), MONTH(service_date), 1)" if USE_MSSQL else "DATE(service_date, 'start of month')"
    day_period_expr = "CAST(service_date AS date)" if USE_MSSQL else "DATE(service_date)"
    service_category_expr = "LTRIM(RTRIM(service_category))" if USE_MSSQL else "TRIM(service_category)"
    where_parts = []

    if years_key:
        year_ranges = _year_date_range_clauses(years_key)
        where_parts.append("(" + " OR ".join(year_ranges) + ")")

    if service_categories_key:
        cats_sql = ",".join(_sql_quote(v) for v in service_categories_key)
        where_parts.append(f"{service_category_expr} IN ({cats_sql})")

    if start_date:
        where_parts.append(f"service_date >= {_sql_quote(start_date)}")

    if end_date:
        where_parts.append(f"service_date <= {_sql_quote(end_date)}")

    where_filters = ("\nAND " + "\nAND ".join(where_parts)) if where_parts else ""
    return {
        "year_expr": year_expr,
        "month_period_expr": month_period_expr,
        "day_period_expr": day_period_expr,
        "service_category_expr": service_category_expr,
        "where_filters": where_filters,
    }


@lru_cache(maxsize=256)
def _run_named_amhd_query_cached(query_name, context_items):
    sql = load_sql_query(query_name)
    query_context = dict(context_items)
    return execute_query(sql.format(**query_context))


def _run_named_amhd_query(query_name, query_context):
    started = perf_counter()
    result = _run_named_amhd_query_cached(query_name, tuple(sorted(query_context.items()))).copy()
    elapsed_ms = (perf_counter() - started) * 1000
    print(f"[amhd_dashboard] {query_name} took {elapsed_ms:.1f} ms")
    return result


def _count_distinct_consumers_cached(
    years_key,
    service_categories_key,
    start_date,
    end_date,
):
    query_context = _amhd_query_context_cached(
        years_key,
        service_categories_key,
        start_date,
        end_date,
    )
    result_df = _run_named_amhd_query("load_amhd_consumers_total", query_context)
    if result_df.empty or "total_consumers" not in result_df.columns:
        return 0
    return int(result_df.iloc[0]["total_consumers"])


def get_true_consumer_count(sel_years, sel_service_categories, start_date, end_date):
    years_key = tuple(sorted(int(y) for y in (sel_years or [])))
    service_categories_key = tuple(sorted(str(v) for v in (sel_service_categories or [])))
    return _count_distinct_consumers_cached(
        years_key,
        service_categories_key,
        str(start_date) if start_date else "",
        str(end_date) if end_date else "",
    )
def load_amhd_dataframe():
    sql = load_sql_query("load_amhd_day")
    df = execute_query(sql)
    print(f"load_amhd_day returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("AMHD query returned 0 rows.")

    # Normalize source column names across SQL backends/casing.
    df.columns = [str(c).strip().lower() for c in df.columns]

    required_cols = {
        "service_category",
        "service_date",
    }
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"AMHD query missing required columns: {missing}")

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df = df[df["service_date"].notna()].copy()

    if "service_year" not in df.columns:
        df["service_year"] = df["service_date"].dt.year
    if "service_month" not in df.columns:
        df["service_month"] = df["service_date"].dt.month
    if "service_day" not in df.columns:
        df["service_day"] = df["service_date"].dt.day

    df["year"] = pd.to_numeric(df["service_year"], errors="coerce").astype("Int64")
    df["month_num"] = pd.to_numeric(df["service_month"], errors="coerce").astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)

    for col in ["service_category", "co_category"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    return df


df_day = load_amhd_dataframe()

# Use day-level data as the superset for option lists.
df_raw = df_day
last_updated_value = compute_last_updated_value(df_raw)

year_opts = sorted(df_raw["year"].dropna().unique().tolist(), reverse=True)
service_category_opts = sorted(df_raw["service_category"].dropna().unique().tolist())

min_date = df_day["service_date"].min().date()
max_date = df_day["service_date"].max().date()


reset_button = dbc.Button(
    "Reset All Filters",
    id="amhd-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Number of AMHD Consumers",
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

from section_texts import SECTION_TEXTS
amhd_sidebar_text = SECTION_TEXTS.get("amhd", [])


def layout():
    left_col = make_left_sidebar(
        kpi_card,
        reset_button,
        filters_card,
        helper_text=amhd_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

    left_col.children.insert(2, view_toggle_card)

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Number of AMHD Consumers", id="amhd-bar-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="amhd-bar-chart",
                        style={"width": "100%"},
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
    Output("amhd-service-category-filter", "value"),
    Output("amhd-date-range", "start_date"),
    Output("amhd-date-range", "end_date"),
    Input("amhd-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_amhd_filters(_n_clicks):
    return None, None, str(min_date), str(max_date)


@callback(
    Output("amhd-kpi-total", "children"),
    Input("amhd-year-filter", "value"),
    Input("amhd-service-category-filter", "value"),
    Input("amhd-date-range", "start_date"),
    Input("amhd-date-range", "end_date"),
)
def update_amhd_kpi(sel_years, sel_service_categories, start_date, end_date):
    total_consumers = get_true_consumer_count(
        sel_years,
        sel_service_categories,
        start_date,
        end_date,
    )
    return format_count_display(total_consumers)


def _build_amhd_query_context(sel_years, sel_service_categories, start_date, end_date):
    return _amhd_query_context_cached(
        tuple(sorted(int(y) for y in (sel_years or []))),
        tuple(sorted(str(v) for v in (sel_service_categories or []))),
        str(start_date) if start_date else "",
        str(end_date) if end_date else "",
    )


def _build_amhd_figures(view, query_context):

    if view == "year":
        bar_grouped = _run_named_amhd_query("load_amhd_consumers_by_year", query_context)
        bar_grouped["period"] = bar_grouped["year"].astype(int).astype(str)
        period_title = "Calendar Year of Service"
    elif view == "month":
        bar_grouped = _run_named_amhd_query("load_amhd_consumers_by_month", query_context)
        bar_grouped["period_date"] = pd.to_datetime(bar_grouped["period_date"], errors="coerce")
        bar_grouped["year"] = bar_grouped["period_date"].dt.year
        bar_grouped["month_num"] = bar_grouped["period_date"].dt.month
        bar_grouped["month"] = bar_grouped["month_num"].map(MONTH_NAMES)
        bar_grouped["period"] = bar_grouped["year"].astype(int).astype(str) + ", " + bar_grouped["month"]
        period_title = "Month of Service"
    else:
        bar_grouped = _run_named_amhd_query("load_amhd_consumers_by_date", query_context)
        bar_grouped["service_date"] = pd.to_datetime(bar_grouped["service_date"], errors="coerce")
        bar_grouped["period"] = bar_grouped["service_date"].dt.strftime("%Y-%m-%d")
        period_title = "Date of Service"

    bar_grouped["label"] = bar_grouped["consumer_count"].apply(lambda v: f"{int(v):,}")
    bar_height = max(320, len(bar_grouped) * 30)
    y_order = bar_grouped["period"].tolist()

    bar_fig = px.bar(
        bar_grouped,
        x="consumer_count",
        y="period",
        orientation="h",
        text="label",
        labels={"consumer_count": "Number of AMHD Consumers", "period": period_title},
    )
    bar_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Number of AMHD Consumers",
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

    return bar_fig


def _build_amhd_tables(query_context):
    service_category_tbl = _run_named_amhd_query("load_amhd_consumers_by_service_category", query_context)
    service_category_tbl = service_category_tbl.rename(columns={"service_category": "Service Category", "consumer_count": "Number of AMHD Consumers"})

    service_category_tbl["Number of AMHD Consumers"] = service_category_tbl["Number of AMHD Consumers"].apply(format_count_display)

    service_category_table = dbc.Table.from_dataframe(service_category_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")

    return service_category_table


@callback(
    Output("amhd-bar-chart", "figure"),
    Input("amhd-view-toggle", "value"),
    Input("amhd-year-filter", "value"),
    Input("amhd-service-category-filter", "value"),
    Input("amhd-date-range", "start_date"),
    Input("amhd-date-range", "end_date"),
)
def update_amhd_figures(view, sel_years, sel_service_categories, start_date, end_date):
    query_context = _build_amhd_query_context(
        sel_years,
        sel_service_categories,
        start_date,
        end_date,
    )
    return _build_amhd_figures(view, query_context)


@callback(
    Output("amhd-service-category-table", "children"),
    Input("amhd-year-filter", "value"),
    Input("amhd-service-category-filter", "value"),
    Input("amhd-date-range", "start_date"),
    Input("amhd-date-range", "end_date"),
)
def update_amhd_tables(sel_years, sel_service_categories, start_date, end_date):
    query_context = _build_amhd_query_context(
        sel_years,
        sel_service_categories,
        start_date,
        end_date,
    )
    return _build_amhd_tables(query_context)
