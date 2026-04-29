# adad_cooccurring_dashboard.py — ADAD Co-Occurring Clients Served page

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


def load_adad_cooccurring_dataframe():
    sql = load_sql_query("load_adad_cooccurring")
    df = execute_query(sql)
    print(f"load_adad_cooccurring returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("ADAD co-occurring query returned 0 rows.")

    if "service_date" not in df.columns and "date" in df.columns:
        df = df.rename(columns={"date": "service_date"})

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df = df[df["service_date"].notna()].copy()

    df["year"] = df["service_date"].dt.year.astype("Int64")
    df["month_num"] = df["service_date"].dt.month.astype("Int64")
    df["month"] = df["month_num"].map(MONTH_NAMES)

    for col in ["county", "modality"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df


df_raw = load_adad_cooccurring_dataframe()

year_opts = sorted(df_raw["year"].dropna().unique().tolist(), reverse=True)
month_nums_present = sorted(df_raw["month_num"].dropna().unique().tolist())
month_opts = [MONTH_NAMES[m] for m in month_nums_present]
modality_opts = sorted(df_raw["modality"].dropna().unique().tolist())
county_opts = sorted(df_raw["county"].dropna().unique().tolist())

min_date = df_raw["service_date"].min().date()
max_date = df_raw["service_date"].max().date()


reset_button = dbc.Button(
    "Reset All Filters",
    id="adad-cooccurring-reset-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

kpi_card = make_kpi_card(
    label="Number of Clients Served",
    count_id="adad-cooccurring-kpi-total",
)

view_toggle_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("View By", className="mb-2 text-center"),
            dbc.RadioItems(
                id="adad-cooccurring-view-toggle",
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
    card_id="adad-cooccurring-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Year",
            "adad-cooccurring-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Month",
            "adad-cooccurring-month-filter",
            options=opts_list(month_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "County",
            "adad-cooccurring-county-filter",
            options=opts_list(county_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Service Modality",
            "adad-cooccurring-modality-filter",
            options=opts_list(modality_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        (
            "Custom Date Range",
            dcc.DatePickerRange(
                id="adad-cooccurring-date-range",
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

adad_cooccurring_sidebar_text = [
    "ADAD co-occurring client service volume shown by year, month, or date.",
    "Use filters and custom date range to narrow clients served.",
]


def layout():
    left_col = make_left_sidebar(
        kpi_card,
        reset_button,
        filters_card,
        helper_text=adad_cooccurring_sidebar_text,
        xs=12,
        md=3,
    )

    left_col.children.insert(2, view_toggle_card)

    center_col = dbc.Col(
        [
            html.Div(
                [
                    html.H5("Number of Clients Served", id="adad-cooccurring-bar-chart-title", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="adad-cooccurring-bar-chart",
                        style={"width": "100%"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
            html.Div(
                [
                    html.H5("Clients Served by Modality and Year (Top 10 Modalities)", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="adad-cooccurring-modality-line-chart",
                        style={"width": "100%", "height": "520px"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
            html.Div(
                [
                    html.H5("Clients Served by County and Year", className="plot-card-header mb-2"),
                    dcc.Graph(
                        id="adad-cooccurring-county-line-chart",
                        style={"width": "100%", "height": "520px"},
                        config={"displayModeBar": True, "displaylogo": False},
                    ),
                ],
                className="mb-4",
                style={"overflow": "visible"},
            ),
            html.P(
                "Horizontal bar chart showing number of clients served by selected time period.",
                className="visually-hidden",
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
                        html.Div(id="adad-cooccurring-modality-table", style={"overflowX": "auto"}),
                        xs=12,
                        md=12,
                        className="mb-3",
                    ),
                    dbc.Col(
                        html.Div(id="adad-cooccurring-year-table", style={"overflowX": "auto"}),
                        xs=12,
                        md=12,
                        className="mb-3",
                    ),
                    dbc.Col(
                        html.Div(id="adad-cooccurring-county-table", style={"overflowX": "auto"}),
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
    Output("adad-cooccurring-year-filter", "value"),
    Output("adad-cooccurring-month-filter", "value"),
    Output("adad-cooccurring-modality-filter", "value"),
    Output("adad-cooccurring-county-filter", "value"),
    Output("adad-cooccurring-date-range", "start_date"),
    Output("adad-cooccurring-date-range", "end_date"),
    Input("adad-cooccurring-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_adad_cooccurring_filters(_n_clicks):
    return None, None, None, None, str(min_date), str(max_date)


@callback(
    Output("adad-cooccurring-bar-chart", "figure"),
    Output("adad-cooccurring-modality-line-chart", "figure"),
    Output("adad-cooccurring-county-line-chart", "figure"),
    Output("adad-cooccurring-kpi-total", "children"),
    Output("adad-cooccurring-modality-table", "children"),
    Output("adad-cooccurring-year-table", "children"),
    Output("adad-cooccurring-county-table", "children"),
    Input("adad-cooccurring-view-toggle", "value"),
    Input("adad-cooccurring-year-filter", "value"),
    Input("adad-cooccurring-month-filter", "value"),
    Input("adad-cooccurring-modality-filter", "value"),
    Input("adad-cooccurring-county-filter", "value"),
    Input("adad-cooccurring-date-range", "start_date"),
    Input("adad-cooccurring-date-range", "end_date"),
)
def update_adad_cooccurring(view, sel_years, sel_months, sel_modalities, sel_counties, start_date, end_date):
    dff = df_raw.copy()

    if sel_years:
        dff = dff[dff["year"].isin(sel_years)]
    if sel_months:
        dff = dff[dff["month"].isin(sel_months)]
    if sel_modalities:
        dff = dff[dff["modality"].isin(sel_modalities)]
    if sel_counties:
        dff = dff[dff["county"].isin(sel_counties)]

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

    grouped["label"] = grouped["client_count"].apply(lambda v: f"{int(v):,}")
    chart_height = max(320, len(grouped) * 30)
    y_order = grouped["period"].tolist()

    bar_fig = px.bar(
        grouped,
        x="client_count",
        y="period",
        orientation="h",
        text="label",
        labels={"client_count": "Number of Clients", "period": y_title},
    )
    bar_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Number of Clients",
        yaxis_title=y_title,
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=y_order,
            autorange=True,
        ),
        height=chart_height,
    )
    bar_fig.update_traces(
        marker_color="#22767C",
        texttemplate="%{text}",
        textposition="auto",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:,}<extra></extra>",
    )

    top_modalities = (
        dff.dropna(subset=["modality"])
        .groupby("modality")["client_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    line_grouped = (
        dff[dff["modality"].isin(top_modalities)]
        .groupby(["year", "modality"], as_index=False)["client_id"]
        .nunique()
        .rename(columns={"client_id": "client_count"})
        .sort_values(["year", "modality"])
    )
    line_grouped = line_grouped.dropna(subset=["year", "modality"]).copy()
    if not line_grouped.empty:
        line_grouped["year"] = line_grouped["year"].astype(int)

    modality_line_fig = px.line(
        line_grouped,
        x="year",
        y="client_count",
        color="modality",
        markers=True,
        category_orders={"modality": top_modalities},
        labels={
            "year": "Year",
            "client_count": "Number of Clients",
            "modality": "Modality",
        },
    )
    modality_line_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=120),
        xaxis_title="Year",
        yaxis_title="Number of Clients",
        legend_title_text="Modality",
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
    modality_line_fig.update_traces(
        hovertemplate="%{fullData.name}<br>Year: %{x}<br>Clients: %{y:,}<extra></extra>"
    )

    county_line_grouped = (
        dff.groupby(["year", "county"], as_index=False)["client_id"]
        .nunique()
        .rename(columns={"client_id": "client_count"})
        .sort_values(["year", "county"])
    )
    county_line_grouped = county_line_grouped.dropna(subset=["year", "county"]).copy()
    if not county_line_grouped.empty:
        county_line_grouped["year"] = county_line_grouped["year"].astype(int)

    county_line_fig = px.line(
        county_line_grouped,
        x="year",
        y="client_count",
        color="county",
        markers=True,
        labels={
            "year": "Year",
            "client_count": "Number of Clients",
            "county": "County",
        },
    )
    county_line_fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=120),
        xaxis_title="Year",
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
    county_line_fig.update_traces(
        hovertemplate="%{fullData.name}<br>Year: %{x}<br>Clients: %{y:,}<extra></extra>"
    )

    modality_tbl = (
        dff.groupby("modality", as_index=False)["client_id"]
        .nunique()
        .rename(columns={"modality": "Modality", "client_id": "Number of Clients"})
        .sort_values("Number of Clients", ascending=False)
        .reset_index(drop=True)
    )

    year_tbl = (
        dff.groupby("year", as_index=False)["client_id"]
        .nunique()
        .rename(columns={"year": "Year", "client_id": "Number of Clients"})
        .sort_values("Year", ascending=False)
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

    for tbl_df in (modality_tbl, year_tbl, county_tbl):
        tbl_df["Number of Clients"] = tbl_df["Number of Clients"].apply(format_count_display)

    modality_table = dbc.Table.from_dataframe(modality_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")
    year_table = dbc.Table.from_dataframe(year_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")
    county_table = dbc.Table.from_dataframe(county_tbl, striped=True, bordered=True, hover=True, responsive=True, size="sm")

    return bar_fig, modality_line_fig, county_line_fig, format_count_display(total_clients), modality_table, year_table, county_table