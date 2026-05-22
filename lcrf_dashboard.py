# lcrf_dashboard.py — Licensed Crisis Residential Facility Occupancy Rates

from pathlib import Path
from functools import lru_cache
from time import perf_counter

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
    make_right_summary_tables_col,
    make_last_updated_block,
    compute_last_updated_value,
    dropdown_filter,
    opts_list,
    apply_standard_line_layout,
)

register_template()

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

DATA_PATH = Path(__file__).resolve().parent / "data" / "lcrs.csv"


def _parse_percent(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce") / 100.0


def _clean_column_name(value) -> str:
    return str(value).strip().strip("'").strip('"').lower()


def _format_rate(rate_value) -> str:
    if rate_value is None or pd.isna(rate_value):
        return "0.0%"
    return f"{float(rate_value):.1%}"


def _load_lcrf_raw():
    sql = load_sql_query("load_lcrf_occupancy")
    try:
        df = execute_query(sql)
        print(f"load_lcrf_occupancy returned {len(df):,} rows")
    except Exception:
        df = pd.read_csv(DATA_PATH)
        print(f"load_lcrf_occupancy fallback csv returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("LCRF query returned 0 rows.")

    df.columns = [_clean_column_name(c) for c in df.columns]

    rename_map = {
        "report date": "date",
        "daily occ rate": "daily_occupancy_rate",
        "daily occupancy rate": "daily_occupancy_rate",
        "occ": "occupied",
        "actual = max minus offline": "actual_available",
        "actual available": "actual_available",
    }
    df = df.rename(columns=rename_map)

    required_cols = [
        "date",
        "facility",
        "daily_occupancy_rate",
        "max",
        "occupied",
        "available",
        "offline",
        "actual_available",
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise RuntimeError(f"LCRF data missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()].copy()

    for col in ["max", "occupied", "available", "offline", "actual_available"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["daily_occupancy_rate"] = _parse_percent(df["daily_occupancy_rate"])
    df["facility"] = df["facility"].astype(str).str.strip()
    df["county"] = df["facility"]
    df["is_invalid"] = df[["max", "occupied", "available", "offline", "actual_available"]].eq(-1).any(axis=1)
    df["year"] = df["date"].dt.year.astype("Int64")
    df["month_num"] = df["date"].dt.month.astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)
    df["occupancy_rate"] = df["occupied"] / df["actual_available"]
    df.loc[df["actual_available"].isna() | (df["actual_available"] <= 0) | df["is_invalid"], "occupancy_rate"] = pd.NA

    return df


@lru_cache(maxsize=1)
def _load_lcrf_dataframe_cached():
    return _load_lcrf_raw()


def load_lcrf_dataframe():
    return _load_lcrf_dataframe_cached().copy()


df_raw = load_lcrf_dataframe()
last_updated_value = compute_last_updated_value(df_raw)

year_opts = sorted(df_raw["year"].dropna().unique().tolist(), reverse=True)
month_nums_present = sorted(df_raw["month_num"].dropna().unique().tolist())
month_opts = [MONTH_NAMES[m] for m in month_nums_present]
county_opts = sorted(df_raw["county"].dropna().unique().tolist())

min_date = df_raw["date"].min().date()
max_date = df_raw["date"].max().date()


reset_button = dbc.Button(
    "Reset All Filters",
    id="lcrf-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Overall Occupancy Rate",
    count_id="lcrf-kpi-total",
)

view_toggle_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("View By", className="mb-2 text-center"),
            dbc.RadioItems(
                id="lcrf-view-toggle",
                options=[
                    {"label": "Year View", "value": "year"},
                    {"label": "Month View", "value": "month"},
                    {"label": "Day View", "value": "day"},
                ],
                value="year",
                persistence="lcrf-view-toggle",
                persistence_type="session",
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
    card_id="lcrf-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Year",
            "lcrf-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Month",
            "lcrf-month-filter",
            options=opts_list(month_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "County",
            "lcrf-county-filter",
            options=opts_list(county_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        (
            "Custom Date Range",
            dcc.DatePickerRange(
                id="lcrf-date-range",
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                display_format="YYYY-MM-DD",
                persistence=True,
                persistence_type="session",
                className="mb-0",
            ),
        ),
    ],
)

from section_texts import SECTION_TEXTS
lcrf_sidebar_text = SECTION_TEXTS.get("lcrf", [])


def build_layout():
    last_updated_block = make_last_updated_block(last_updated_value)
    left_col = dbc.Col(
        [
            kpi_card,
            reset_button,
            view_toggle_card,
            filters_card,
            last_updated_block,
            html.Div(
                [html.P(text, className="mb-1") for text in lcrf_sidebar_text],
                className="small text-muted px-1",
            ),
        ],
        xs=12,
        md=3,
    )

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Facility Occupancy Rates", id="lcrf-facility-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="lcrf-facility-line-chart",
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

    right_col = make_right_summary_tables_col(
        [
            ("Aggregate Occupancy Rates", "lcrf-aggregate-table"),
        ],
        xs=12,
        md=3,
    )

    return dbc.Container(
        dbc.Row([left_col, center_col, right_col], className="g-3"),
        fluid=True,
    )


layout = build_layout()


@callback(
    Output("lcrf-year-filter", "value"),
    Output("lcrf-month-filter", "value"),
    Output("lcrf-county-filter", "value"),
    Output("lcrf-date-range", "start_date"),
    Output("lcrf-date-range", "end_date"),
    Input("lcrf-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_lcrf_filters(_n_clicks):
    return None, None, None, str(min_date), str(max_date)


@callback(
    Output("lcrf-kpi-total", "children"),
    Input("lcrf-year-filter", "value"),
    Input("lcrf-month-filter", "value"),
    Input("lcrf-county-filter", "value"),
    Input("lcrf-date-range", "start_date"),
    Input("lcrf-date-range", "end_date"),
)
def update_lcrf_kpi(sel_years, sel_months, sel_counties, start_date, end_date):
    dff = df_raw.copy()

    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]
    if sel_months:
        dff = dff[dff["month"].isin(sel_months)]
    if sel_counties:
        dff = dff[dff["county"].isin(sel_counties)]
    if start_date:
        dff = dff[dff["date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["date"] <= pd.to_datetime(end_date)]

    valid_dff = dff[~dff["is_invalid"]]
    rate = 0 if valid_dff.empty else (valid_dff["occupied"].sum() / valid_dff["actual_available"].sum() if valid_dff["actual_available"].sum() else 0)
    return _format_rate(rate)


def _filter_lcrf_frame(sel_years, sel_months, sel_counties, start_date, end_date):
    dff = df_raw.copy()

    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]
    if sel_months:
        dff = dff[dff["month"].isin(sel_months)]
    if sel_counties:
        dff = dff[dff["county"].isin(sel_counties)]
    if start_date:
        dff = dff[dff["date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["date"] <= pd.to_datetime(end_date)]

    return dff


def _valid_lcrf_frame(dff):
    return dff[~dff["is_invalid"]].copy()


def _build_period_frame(dff, view):
    dff = _valid_lcrf_frame(dff)

    if view == "year":
        group_cols = ["year", "facility"]
        period_title = "Calendar Year of Service"
    elif view == "month":
        group_cols = ["year", "month_num", "month", "facility"]
        period_title = "Month of Service"
    else:
        group_cols = ["date", "facility"]
        period_title = "Date of Service"

    grouped = (
        dff.groupby(group_cols, as_index=False)
        .agg({"occupied": "sum", "actual_available": "sum"})
        .copy()
    )
    grouped["occupancy_rate"] = grouped.apply(
        lambda row: (row["occupied"] / row["actual_available"]) if row["actual_available"] else pd.NA,
        axis=1,
    )

    if view == "year":
        grouped["period"] = grouped["year"].astype(int).astype(str)
        grouped = grouped.sort_values(["year", "facility"])
    elif view == "month":
        grouped["period"] = grouped["year"].astype(int).astype(str) + ", " + grouped["month"]
        grouped = grouped.sort_values(["year", "month_num", "facility"])
    else:
        grouped["period"] = pd.to_datetime(grouped["date"]).dt.strftime("%Y-%m-%d")
        grouped = grouped.sort_values(["date", "facility"])

    return grouped, period_title


def _build_aggregate_frame(dff, view):
    dff = _valid_lcrf_frame(dff)

    if view == "year":
        grouped = (
            dff.groupby(["year"], as_index=False)
            .agg({"occupied": "sum", "actual_available": "sum"})
            .copy()
        )
        grouped["period"] = grouped["year"].astype(int).astype(str)
        grouped = grouped.sort_values("year")
        period_title = "Calendar Year of Service"
    elif view == "month":
        grouped = (
            dff.groupby(["year", "month_num", "month"], as_index=False)
            .agg({"occupied": "sum", "actual_available": "sum"})
            .copy()
        )
        grouped["period"] = grouped["year"].astype(int).astype(str) + ", " + grouped["month"]
        grouped = grouped.sort_values(["year", "month_num"])
        period_title = "Month of Service"
    else:
        grouped = (
            dff.groupby(["date"], as_index=False)
            .agg({"occupied": "sum", "actual_available": "sum"})
            .copy()
        )
        grouped["period"] = pd.to_datetime(grouped["date"]).dt.strftime("%Y-%m-%d")
        grouped = grouped.sort_values("date")
        period_title = "Date of Service"

    grouped["occupancy_rate"] = grouped.apply(
        lambda row: (row["occupied"] / row["actual_available"]) if row["actual_available"] else pd.NA,
        axis=1,
    )
    return grouped, period_title


def _build_aggregate_table(dff, view):
    valid_dff = _valid_lcrf_frame(dff)

    if view == "year":
        period_cols = ["year"]
        period_title = "Calendar Year of Service"
    elif view == "month":
        period_cols = ["year", "month_num", "month"]
        period_title = "Month of Service"
    else:
        period_cols = ["date"]
        period_title = "Date of Service"

    invalid_flags = dff.groupby(period_cols, as_index=False).agg(has_invalid=("is_invalid", "max")).copy()
    valid_grouped = (
        valid_dff.groupby(period_cols, as_index=False)
        .agg({"occupied": "sum", "actual_available": "sum"})
        .copy()
    )
    grouped = invalid_flags.merge(valid_grouped, on=period_cols, how="left")

    if view == "year":
        grouped["period"] = grouped["year"].astype(int).astype(str)
        grouped = grouped.sort_values("year")
    elif view == "month":
        grouped["period"] = grouped["year"].astype(int).astype(str) + ", " + grouped["month"]
        grouped = grouped.sort_values(["year", "month_num"])
    else:
        grouped["period"] = pd.to_datetime(grouped["date"]).dt.strftime("%Y-%m-%d")
        grouped = grouped.sort_values("date")

    grouped["occupancy_rate"] = grouped.apply(
        lambda row: (row["occupied"] / row["actual_available"]) if pd.notna(row.get("actual_available")) and row["actual_available"] else pd.NA,
        axis=1,
    )
    if view == "day":
        grouped["status"] = grouped["has_invalid"].map({True: "Data not available", False: "Valid"})
    else:
        grouped["status"] = grouped["has_invalid"].map({True: "Invalid rows excluded", False: "Valid"})
    grouped.loc[grouped["occupied"].isna() | grouped["actual_available"].isna(), "occupancy_rate"] = pd.NA

    # Always show period and occupancy rate. For day view, show 'Data not available' in Occupancy Rate if invalid.
    display_cols = ["period", "occupancy_rate"]
    col_rename = {"period": period_title, "occupancy_rate": "Occupancy Rate"}
    display = grouped[display_cols + (["has_invalid"] if view == "day" else [])].copy()
    if view == "day":
        # Show 'Data not available' for invalid rows in day view
        display["Occupancy Rate"] = display.apply(
            lambda row: "Data not available" if row.get("has_invalid") else _format_rate(row["occupancy_rate"]), axis=1
        )
        display = display.drop(columns=["occupancy_rate", "has_invalid"])
        display = display.rename(columns={"period": period_title})
    else:
        display["occupancy_rate"] = display["occupancy_rate"].apply(_format_rate)
        display = display.rename(columns=col_rename)
    return display, period_title


def _line_chart(grouped, period_title, color_col=None, chart_title="Occupancy Rate"):
    if color_col:
        fig = px.line(
            grouped,
            x="period",
            y="occupancy_rate",
            color=color_col,
            markers=True,
            labels={"period": period_title, "occupancy_rate": "Occupancy Rate", color_col: "Facility"},
        )
        fig.update_layout(legend_title_text="Facility")
        fig.update_traces(hovertemplate="%{fullData.name}<br>%{x}<br>Occupancy Rate: %{y:.1%}<extra></extra>")
    else:
        fig = px.line(
            grouped,
            x="period",
            y="occupancy_rate",
            markers=True,
            labels={"period": period_title, "occupancy_rate": "Occupancy Rate"},
        )
        fig.update_traces(hovertemplate="%{x}<br>Occupancy Rate: %{y:.1%}<extra></extra>")

    apply_standard_line_layout(
        fig,
    )

    return fig


def _render_table(df):
    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
    body_rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                value = ""
            cells.append(html.Td(value))
        body_rows.append(html.Tr(cells))
    return dbc.Table([header, html.Tbody(body_rows)], bordered=True, hover=True, responsive=True, size="sm", className="mb-0")


@callback(
    Output("lcrf-facility-line-chart", "figure"),
    Output("lcrf-aggregate-table", "children"),
    Input("lcrf-view-toggle", "value"),
    Input("lcrf-year-filter", "value"),
    Input("lcrf-month-filter", "value"),
    Input("lcrf-county-filter", "value"),
    Input("lcrf-date-range", "start_date"),
    Input("lcrf-date-range", "end_date"),
)
def update_lcrf_figures(view, sel_years, sel_months, sel_counties, start_date, end_date):
    dff = _filter_lcrf_frame(sel_years, sel_months, sel_counties, start_date, end_date)

    facility_grouped, period_title = _build_period_frame(dff, view)
    agg_table, _agg_period_title = _build_aggregate_table(dff, view)

    facility_fig = _line_chart(facility_grouped, period_title, color_col="facility")

    apply_standard_line_layout(facility_fig)

    return facility_fig, html.Div(_render_table(agg_table), className="table-responsive")
