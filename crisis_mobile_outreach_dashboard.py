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
    make_right_summary_tables_col,
    make_filters_card,
    dropdown_filter,
    format_count_display,
    format_percentage_display,
    opts_list,
    sort_opts,
    compute_adaptive_horizontal_bar_height,
    apply_standard_bar_layout,
    apply_standard_single_series_bar_trace,
    apply_standard_line_layout,
)
from theme import register_template

register_template()


def load_cmo_referrals_dataframe():
    """Load referral destinations for Crisis Mobile Outreach."""
    sql = load_sql_query("load_crisis_mobile_outreach")
    df = execute_query(sql)
    print(f"load_crisis_mobile_outreach returned {len(df):,} rows")

    if df.empty:
        raise RuntimeError("load_crisis_mobile_outreach returned 0 rows.")

    df = df.copy()
    df['program_city'] = df['program_city'].str.title()
    df['program_county'] = df['program_county'].str.title()
    df["referral_destination"] = df["referral_destination"].fillna("Unknown")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year.astype("Int64")

    for column in ["age_group", "sex", "program_city", "program_county", "is_homeless"]:
        if column in df.columns:
            df[column] = df[column].fillna("Unknown").astype(str).str.strip()

    return df


def _six_months_earlier(value):
    return pd.Timestamp(value) - pd.DateOffset(months=6)


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
year_opts = sort_opts(df_raw["year"]) if "year" in df_raw.columns else []
county_opts = sort_opts(df_raw["program_county"]) if "program_county" in df_raw.columns else []
city_opts = sort_opts(df_raw["program_city"]) if "program_city" in df_raw.columns else []
homeless_opts = sort_opts(df_raw["is_homeless"]) if "is_homeless" in df_raw.columns else []
age_opts = sort_opts(df_raw["age_group"]) if "age_group" in df_raw.columns else []
sex_opts = sort_opts(df_raw["sex"]) if "sex" in df_raw.columns else []
referral_opts = sort_opts(df_raw["referral_destination"])
cmo_bar_h = f"{compute_adaptive_horizontal_bar_height(len(referral_opts))}px"
min_date = df_raw["date"].min().date()
max_date = df_raw["date"].max().date()
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
    label="Distinct Crisis Mobile Outreach Clients",
    count_id="cmo-kpi-total",
)

filters_card = make_filters_card(
    card_id="cmo-filters",
    title="Filter Data",
    filters=[
        dropdown_filter(
            "Year",
            "cmo-year-filter",
            options=opts_list(year_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        (
            "Custom Date Range",
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Start Date", className="form-label mb-1 text-muted small"),
                            dbc.Input(
                                id="cmo-start-date",
                                type="date",
                                value=None,
                                min=str(min_date),
                                max=str(max_date),
                                persistence=True,
                                persistence_type="session",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("End Date", className="form-label mb-1 text-muted small"),
                            dbc.Input(
                                id="cmo-end-date",
                                type="date",
                                value=None,
                                min=str(min_date),
                                max=str(max_date),
                                persistence=True,
                                persistence_type="session",
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="g-2",
            ),
        ),
        dropdown_filter(
            "County",
            "cmo-county-filter",
            options=opts_list(county_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "City",
            "cmo-city-filter",
            options=opts_list(city_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Homeless Status",
            "cmo-homeless-filter",
            options=opts_list(homeless_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Age Group",
            "cmo-age-filter",
            options=opts_list(age_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
        dropdown_filter(
            "Sex",
            "cmo-sex-filter",
            options=opts_list(sex_opts),
            multi=True,
            placeholder="All",
            value=None,
        ),
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
            graph_block("cmo-referral-bar", "Referral Destinations for Crisis Mobile Outreach Clients"),
            html.P(
                "Bar chart showing referral destinations for Crisis Mobile Outreach clients.",
                className="visually-hidden",
            ),
            graph_block("cmo-referral-year-line", "Top Referral Destinations by Year (Over 5% of Total)"),
            html.P(
                "Line chart showing top referral destinations by year.",
                className="visually-hidden",
            ),
            graph_block("cmo-county-year-line", "County by Year"),
            html.P(
                "Line chart showing county trends by year.",
                className="visually-hidden",
            ),
            graph_block("cmo-age-year-line", "Age Group by Year"),
            html.P(
                "Line chart showing age group trends by year.",
                className="visually-hidden",
            ),
        ],
        xs=12,
        md=6,
    )

    right_col = make_right_summary_tables_col(
        [
            ("Year", "cmo-year-table"),
            ("County", "cmo-county-table"),
            ("Age Group", "cmo-age-table"),
            ("Sex", "cmo-sex-table"),
            ("Homeless", "cmo-homeless-table"),
            ("Referral Destination", "cmo-summary-table"),
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
    Output("cmo-start-date", "value"),
    Output("cmo-end-date", "value"),
    Output("cmo-year-filter", "value"),
    Output("cmo-county-filter", "value"),
    Output("cmo-city-filter", "value"),
    Output("cmo-homeless-filter", "value"),
    Output("cmo-age-filter", "value"),
    Output("cmo-sex-filter", "value"),
    Output("cmo-destination-filter", "value"),
    Input("cmo-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_cmo_filters(_n_clicks):
    return None, None, None, None, None, None, None, None, None


@callback(
    Output("cmo-kpi-total", "children"),
    Output("cmo-referral-bar", "figure"),
    Output("cmo-referral-year-line", "figure"),
    Output("cmo-age-year-line", "figure"),
    Output("cmo-county-year-line", "figure"),
    Output("cmo-year-table", "children"),
    Output("cmo-county-table", "children"),
    Output("cmo-age-table", "children"),
    Output("cmo-sex-table", "children"),
    Output("cmo-homeless-table", "children"),
    Output("cmo-summary-table", "children"),
    Input("cmo-start-date", "value"),
    Input("cmo-end-date", "value"),
    Input("cmo-year-filter", "value"),
    Input("cmo-county-filter", "value"),
    Input("cmo-city-filter", "value"),
    Input("cmo-homeless-filter", "value"),
    Input("cmo-age-filter", "value"),
    Input("cmo-sex-filter", "value"),
    Input("cmo-destination-filter", "value"),
)
def update_cmo_dashboard(
    start_date,
    end_date,
    selected_years,
    selected_counties,
    selected_cities,
    selected_homeless_status,
    selected_age_groups,
    selected_sex,
    selected_destinations,
):
    dff = df_raw.copy()

    if start_date and end_date:
        start_ts = pd.to_datetime(min(start_date, end_date))
        end_ts = pd.to_datetime(max(start_date, end_date))
    else:
        start_ts = pd.to_datetime(start_date) if start_date else None
        end_ts = pd.to_datetime(end_date) if end_date else None

    if start_ts is not None:
        dff = dff[dff["date"] >= start_ts]
    if end_ts is not None:
        dff = dff[dff["date"] <= end_ts]
    if selected_years:
        dff = dff[dff["year"].isin(selected_years)]
    if selected_counties:
        dff = dff[dff["program_county"].isin(selected_counties)]
    if selected_cities:
        dff = dff[dff["program_city"].isin(selected_cities)]
    if selected_homeless_status:
        dff = dff[dff["is_homeless"].isin(selected_homeless_status)]
    if selected_age_groups:
        dff = dff[dff["age_group"].isin(selected_age_groups)]
    if selected_sex:
        dff = dff[dff["sex"].isin(selected_sex)]
    if selected_destinations:
        dff = dff[dff["referral_destination"].isin(selected_destinations)]

    agg = (
        dff.groupby("referral_destination", as_index=False)["patid"]
        .nunique()
        .rename(columns={"patid": "ct"})
    )

    total_clients = int(agg["ct"].sum())
    agg["percentage"] = (agg["ct"] / total_clients * 100) if total_clients > 0 else 0.0
    agg = agg.sort_values("ct", ascending=False).copy()
    agg["ct_display"] = agg["ct"].apply(format_count_display)
    agg["percentage_display"] = agg.apply(
        lambda row: format_percentage_display(
            row["percentage"],
            count_display=row["ct_display"],
            decimals=2,
        ),
        axis=1,
    )
    agg["bar_label"] = agg.apply(
        lambda row: f"{row['percentage_display']} ({row['ct_display']})"
        if row["percentage_display"]
        else row["ct_display"],
        axis=1,
    )
    agg["percentage_table_display"] = agg.apply(
        lambda row: format_percentage_display(
            row["percentage"],
            count_display=row["ct_display"],
            decimals=2,
            suppressed_output="N/A",
        ),
        axis=1,
    )

    # For horizontal bar charts, categoryarray[0] is rendered at the bottom.
    # Reverse here so the highest-count destination appears at the top.
    y_order = agg["referral_destination"].tolist()[::-1]

    fig = px.bar(
        agg,
        x="percentage",
        y="referral_destination",
        orientation="h",
        text="bar_label",
        labels={
            "percentage": "Percent of Total",
            "referral_destination": "Referral Destination",
        },
    )
    apply_standard_bar_layout(
        fig,
        xaxis=dict(title="Percent of Total", ticksuffix="%", rangemode="tozero"),
        yaxis=dict(title="Referral Destination", categoryorder="array", categoryarray=y_order),
        height=compute_adaptive_horizontal_bar_height(
            len(agg),
        ),
    )
    apply_standard_single_series_bar_trace(
        fig,
        customdata=agg[["ct_display"]],
        hovertemplate="%{y}: %{x:.2f}% (%{customdata[0]} clients)<extra></extra>",
    )

    referral_totals = (
        dff.groupby("referral_destination", as_index=False)["patid"]
        .nunique()
        .rename(columns={"patid": "ct"})
    )
    referral_total_ct = int(referral_totals["ct"].sum())
    referral_totals["pct"] = (
        referral_totals["ct"] / referral_total_ct * 100 if referral_total_ct > 0 else 0.0
    )
    top_referrals = referral_totals[referral_totals["pct"] > 5]["referral_destination"].tolist()

    referral_line_df = (
        dff[dff["referral_destination"].isin(top_referrals)]
        .groupby(["year", "referral_destination"], as_index=False)["patid"]
        .nunique()
        .rename(columns={"patid": "Distinct Clients"})
        .dropna(subset=["year"])
        .sort_values(["year", "referral_destination"])
    )

    if referral_line_df.empty:
        referral_line_fig = px.line()
    else:
        referral_line_df["year"] = referral_line_df["year"].astype(int)
        referral_line_fig = px.line(
            referral_line_df,
            x="year",
            y="Distinct Clients",
            color="referral_destination",
            markers=True,
            labels={
                "year": "Year",
                "Distinct Clients": "Distinct Clients",
                "referral_destination": "Referral Destination",
            },
        )
        referral_line_fig.update_traces(
            hovertemplate="%{fullData.name}<br>Year: %{x}<br>Distinct Clients: %{y:,}<extra></extra>"
        )

    apply_standard_line_layout(
        referral_line_fig,
        xaxis=dict(dtick=1),
    )

    age_line_df = (
        dff.groupby(["year", "age_group"], as_index=False)["patid"]
        .nunique()
        .rename(columns={"patid": "Distinct Clients"})
        .dropna(subset=["year", "age_group"])
        .sort_values(["year", "age_group"])
    )

    if age_line_df.empty:
        age_line_fig = px.line()
    else:
        age_line_df["year"] = age_line_df["year"].astype(int)
        age_order = sort_opts(dff["age_group"])
        age_line_fig = px.line(
            age_line_df,
            x="year",
            y="Distinct Clients",
            color="age_group",
            category_orders={"age_group": age_order},
            markers=True,
            labels={
                "year": "Year",
                "Distinct Clients": "Distinct Clients",
                "age_group": "Age Group",
            },
        )
        age_line_fig.update_traces(
            hovertemplate="%{fullData.name}<br>Year: %{x}<br>Distinct Clients: %{y:,}<extra></extra>"
        )

    apply_standard_line_layout(
        age_line_fig,
        xaxis=dict(dtick=1),
    )

    county_line_df = (
        dff.groupby(["year", "program_county"], as_index=False)["patid"]
        .nunique()
        .rename(columns={"patid": "Distinct Clients"})
        .dropna(subset=["year", "program_county"])
        .sort_values(["year", "program_county"])
    )

    if county_line_df.empty:
        county_line_fig = px.line()
    else:
        county_line_df["year"] = county_line_df["year"].astype(int)
        county_order = sort_opts(dff["program_county"])
        county_line_fig = px.line(
            county_line_df,
            x="year",
            y="Distinct Clients",
            color="program_county",
            category_orders={"program_county": county_order},
            markers=True,
            labels={
                "year": "Year",
                "Distinct Clients": "Distinct Clients",
                "program_county": "County",
            },
        )
        county_line_fig.update_traces(
            hovertemplate="%{fullData.name}<br>Year: %{x}<br>Distinct Clients: %{y:,}<extra></extra>"
        )

    apply_standard_line_layout(
        county_line_fig,
        xaxis=dict(dtick=1),
    )

    table_df = agg[["referral_destination", "ct", "percentage"]].rename(
        columns={
            "referral_destination": "Referral Destination",
            "ct": "Distinct Clients",
            "percentage": "Percent of Total",
        }
    )
    table_df["Distinct Clients"] = table_df["Distinct Clients"].apply(format_count_display)
    table_df["Percent of Total"] = agg["percentage_table_display"].values

    table = dbc.Table.from_dataframe(
        table_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )

    def _build_dimension_table(column_name, label_name):
        dim_df = (
            dff.groupby(column_name, as_index=False)["patid"]
            .nunique()
            .rename(columns={column_name: label_name, "patid": "Distinct Clients"})
            .reset_index(drop=True)
        )

        if column_name == "year":
            # Keep year numeric and sort descending so values render correctly.
            dim_df[label_name] = pd.to_numeric(dim_df[label_name], errors="coerce").astype("Int64")
            dim_df = dim_df.sort_values(label_name, ascending=False).reset_index(drop=True)
            dim_df[label_name] = dim_df[label_name].astype(str)
        else:
            category_order = sort_opts(dff[column_name])
            dim_df[label_name] = pd.Categorical(dim_df[label_name], categories=category_order, ordered=True)
            dim_df = dim_df.sort_values(label_name).reset_index(drop=True)

        dim_total = int(dim_df["Distinct Clients"].sum())
        dim_df["Percent of Total"] = (
            dim_df["Distinct Clients"] / dim_total * 100 if dim_total > 0 else 0.0
        )
        dim_df["Distinct Clients"] = dim_df["Distinct Clients"].apply(format_count_display)
        dim_df["Percent of Total"] = dim_df["Percent of Total"].apply(
            lambda pct: format_percentage_display(pct, decimals=2)
        )
        return dbc.Table.from_dataframe(
            dim_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size="sm",
        )

    year_table = _build_dimension_table("year", "Year")
    county_table = _build_dimension_table("program_county", "County")
    age_table = _build_dimension_table("age_group", "Age Group")
    sex_table = _build_dimension_table("sex", "Sex")
    homeless_table = _build_dimension_table("is_homeless", "Homeless Status")

    return (
        format_count_display(total_clients),
        fig,
        referral_line_fig,
        age_line_fig,
        county_line_fig,
        year_table,
        county_table,
        age_table,
        sex_table,
        homeless_table,
        table,
    )
