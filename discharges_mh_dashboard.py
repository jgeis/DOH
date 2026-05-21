# discharges_mh_dashboard.py — Discharges Related to Mental Health Disorders page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template
import textwrap
from dashboard_utils import (
    load_sql_query,
    sort_opts,
    opts_list,
    statewide_first,
    apply_county_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    graph_block,
    make_kpi_card,
    make_left_sidebar,
    make_right_summary_tables_col,
    compute_last_updated_value,
    make_filters_card,
    dropdown_filter,
    format_count_display,
    apply_standard_bar_layout,
    apply_standard_line_layout,
)

register_template()

# ----------------------------
# Data helpers
# ----------------------------

def load_discharge_mh_dataframe_from_db():
    """
    This helper:
      1. Loads the main SQL query by name.
      2. Connects to the database and runs the query.
      3. Cleans up some columns so the rest of the app is easier to write.

    Why: having this in one place avoids repeating the same database
    logic in multiple callbacks.
    
    Note: Uses either SQLite or MSSQL automatically based on config.
    """
    # Grab the SQL for our main data
    sql = load_sql_query("load_discharge_data_view_diag_mh")
    
    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)
    print(f"load_discharge_data_view_diag_mh returned {len(df):,} rows")

    # If there is no data, we stop early instead of showing a broken page
    if df.empty:
        raise RuntimeError("Query returned 0 rows.")

    # Make the year column numeric when possible so graphs treat it as numbers
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # For these columns, replace missing values with "Unknown"
    # so we don't get blank labels in filters and tables.
    for col in ["county", "city", "zip", "hawaii_residency", "age_group", "sex", "diagnosis", "year"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_discharge_mh_dataframe_from_db()
last_updated_value = compute_last_updated_value(df_raw)

# Normalize ZIP values (5-digit strings) so they look cleaner in the filters and tables.
if "zip" in df_raw.columns:
    df_raw["zip"] = (
        df_raw["zip"]
        .astype(str)
        .str.extract(r"(\d{5})", expand=False)
        .fillna("")
    )

# Count how many unique records we have to show on the KPI card.
total_unique = df_raw["record_id"].nunique()

# Build the lists of choices for each filter only if the column exists.
diagnosis_opts = sort_opts(df_raw["diagnosis"])                  if "diagnosis"          in df_raw.columns else []
county_opts    = sort_opts(df_raw["county"])                     if "county"             in df_raw.columns else []
city_opts      = sort_opts(df_raw["city"])                       if "city"               in df_raw.columns else []
zip_opts       = sort_opts(df_raw["zip"])                        if "zip"                in df_raw.columns else []
year_opts      = sorted(df_raw["year"].dropna().unique().tolist())  if "year"           in df_raw.columns else []
hawaii_residency_opts = sort_opts(df_raw["hawaii_residency"])    if "hawaii_residency"   in df_raw.columns else []
age_opts       = sort_opts(df_raw["age_group"])                  if "age_group"          in df_raw.columns else []
sex_opts       = sort_opts(df_raw["sex"])                        if "sex"                in df_raw.columns else []
race_ethnicity_opts = sort_opts(df_raw["race_ethnicity"])        if "race_ethnicity"     in df_raw.columns else []

# ----------------------------
# UI Components
# ----------------------------

# This link helps keyboard and screen reader users jump straight to the filters.
skip_link = html.A(
    "Skip to filters",
    href="#discharges-mh-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

reset_filters_button = dbc.Button(
    "Reset All Filters",
    id="discharges-mh-reset-filters-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

# Big green card that shows the total number of discharges.
kpi_card = make_kpi_card(
    label="Number of Emergency Discharges Related to Mental Health Disorders",
    count_id="kpi-total-discharges-mh",
)

# Card holding all the filter controls down the left side.
# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card = make_filters_card(
    card_id="discharges-mh-filters",
    title="Filter Data",
    filters=[
        dropdown_filter("Mental Health Diagnosis", "discharges-mh-diagnosis-filter", options=opts_list(diagnosis_opts), multi=True, placeholder="All"),
        dropdown_filter("County", "discharges-mh-county-filter", options=opts_list(county_opts), multi=True, placeholder="All"),
        dropdown_filter("City", "discharges-mh-city-filter", options=opts_list(city_opts), multi=True, placeholder="All"),
        dropdown_filter("Year", "discharges-mh-year-filter", options=opts_list(year_opts), multi=True, placeholder="All"),
        dropdown_filter("Age Group", "discharges-mh-age-filter", options=opts_list(age_opts), multi=True, placeholder="All"),
        dropdown_filter("Sex", "discharges-mh-sex-filter", options=opts_list(sex_opts), multi=True, placeholder="All"),
        dropdown_filter("Race/Ethnicity", "discharges-mh-race-ethnicity-filter", options=opts_list(race_ethnicity_opts), multi=True, placeholder="All"),
        dropdown_filter("Hawaii Resident", "discharges-mh-hawaii-residency-filter", options=opts_list(hawaii_residency_opts), multi=True, placeholder="All"),
    ],
)

from section_texts import SECTION_TEXTS
discharges_mh_sidebar_text = SECTION_TEXTS.get("discharges_mh", [])

# ----------------------------
# Layout
# ----------------------------

def layout():
    """
    Build the discharges MH dashboard layout.
    """
    # Adjust plot heights for desktop
    line_h = "400px"
    bar_h  = "360px"

    # Left column: KPI, reset button, and filters.
    left_col = make_left_sidebar(
        kpi_card,
        reset_filters_button,
        filters_card,
        helper_text=discharges_mh_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

    # Center column: the main line and bar charts.
    center_col = dbc.Col(
        [
            graph_block("bar-diagnoses-mh", "Discharges by Mental Health Diagnosis", "800px"),
            html.P("Bar chart showing discharges by mental health diagnosis.", className="visually-hidden"),
            graph_block("diagnosis-year-lines-mh", "Yearly Discharges by Mental Health Diagnosis", line_h),
            html.P("Line chart showing yearly discharges by mental health diagnosis.", className="visually-hidden"),
            graph_block("county-year-lines-mh", "Yearly Discharges by County", line_h),
            html.P("Line chart showing yearly discharges by county.", className="visually-hidden"),
            graph_block("age-year-lines-mh", "Yearly Discharges by Age Group", line_h),
            html.P("Line chart showing yearly discharges by age group.", className="visually-hidden"),
            graph_block("sex-year-stacked-mh", "Yearly Discharges by Gender", bar_h),
            html.P("Stacked bar chart showing yearly discharges by gender.", className="visually-hidden"),
        ],
        xs=12, md=6
    )

    # Right column: summary tables (ordered by shared site-wide utility)
    right_col = make_right_summary_tables_col(
        [
            ("Calendar Year", "table-year-mh"),
            ("County", "table-county-mh"),
            ("Age Group", "table-age-mh"),
            ("Sex", "table-sex-mh"),
            ("Race/Ethnicity", "table-race-ethnicity-mh"),
            ("Hawaii Resident", "table-hawaii-residency-mh"),
        ],
        xs=12,
        md=3,
    )

    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([left_col, center_col, right_col], className="g-3"),
            id="discharges-mh-section",
        ),
    ], fluid=True, className="p-2")


# This is the default layout used when the app imports this file.
layout = layout()

# ----------------------------
# Callbacks for discharges MH
# ----------------------------

@callback(
    Output("discharges-mh-diagnosis-filter", "value"),
    Output("discharges-mh-county-filter", "value"),
    Output("discharges-mh-city-filter", "value"),
    Output("discharges-mh-year-filter", "value"),
    Output("discharges-mh-age-filter", "value"),
    Output("discharges-mh-sex-filter", "value"),
    Output("discharges-mh-race-ethnicity-filter", "value"),
    Output("discharges-mh-hawaii-residency-filter", "value"),
    Input("discharges-mh-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_discharges_mh_filters(_n_clicks):
    return None, None, None, None, None, None, None, None


@callback(
    Output("kpi-total-discharges-mh", "children"),
    Output("bar-diagnoses-mh", "figure"),
    Output("diagnosis-year-lines-mh", "figure"),
    Output("county-year-lines-mh", "figure"),
    Output("age-year-lines-mh", "figure"),
    Output("sex-year-stacked-mh", "figure"),
    Output("table-year-mh", "children"),
    Output("table-county-mh", "children"),
    Output("table-age-mh", "children"),
    Output("table-sex-mh", "children"),
    Output("table-race-ethnicity-mh", "children"),
    Output("table-hawaii-residency-mh", "children"),
    Input("discharges-mh-diagnosis-filter", "value"),
    Input("discharges-mh-county-filter", "value"),
    Input("discharges-mh-city-filter", "value"),
    Input("discharges-mh-year-filter", "value"),
    Input("discharges-mh-hawaii-residency-filter", "value"),
    Input("discharges-mh-age-filter", "value"),
    Input("discharges-mh-sex-filter", "value"),
    Input("discharges-mh-race-ethnicity-filter", "value"),
)

def update_dashboard(diagnosis, county, city, year, hawaii_residency, age, sex, race_ethnicity):
    """
    This function runs every time the user changes a filter.
    It updates all the discharge MH visualizations and tables.
    """

    def apply_filter(frame, col, val):
        """Small helper for filter logic."""
        if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
            return frame
        if isinstance(val, (list, tuple)):
            return frame[frame[col].isin(val)]
        return frame[frame[col] == val]

    # Start from the full dataset each time.
    dff = df_raw.copy()

    # Only apply filters for columns that actually exist.
    if "diagnosis" in dff.columns:          dff = apply_filter(dff, "diagnosis", diagnosis)
    if "county" in dff.columns:             dff = apply_county_filter(dff, county)
    if "city" in dff.columns:               dff = apply_filter(dff, "city", city)
    if "year" in dff.columns:               dff = apply_filter(dff, "year", year)
    if "hawaii_residency" in dff.columns:   dff = apply_filter(dff, "hawaii_residency", hawaii_residency)
    if "age_group" in dff.columns:          dff = apply_filter(dff, "age_group", age)
    if "sex" in dff.columns:                dff = apply_filter(dff, "sex", sex)
    if "race_ethnicity" in dff.columns:     dff = apply_filter(dff, "race_ethnicity", race_ethnicity)

    include_statewide_county_outputs = county_output_should_include_statewide(county)

    filter_total = dff["record_id"].nunique()

    # ---------- Bar chart: Discharges by Mental Health Diagnosis ----------
    if {"diagnosis"}.issubset(dff.columns):
        by_dx = (
            dff.groupby("diagnosis")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
            .tail(10)
        )

        def wrap_diagnosis_label(label: str, max_len: int = 45):
            """
            Break long labels into multiple lines so they don't stretch the chart.
            Using textwrap ensures even exceptionally long labels wrap completely.
            """
            # textwrap.wrap returns a list of strings chunked by max_len
            return "<br>".join(textwrap.wrap(str(label), width=max_len))

        by_dx["diagnosis_label"] = by_dx["diagnosis"].apply(wrap_diagnosis_label)
        by_dx["display_count"] = by_dx["count"].apply(format_count_display)

        dx_bar = px.bar(
            by_dx,
            x="count",
            y="diagnosis_label",
            text="display_count",
            labels={"count": "Number of Discharges", "diagnosis_label": "Mental Health Diagnosis"},
        )

        dx_bar.update_traces(
            marker_color="#22767C",
            textposition="inside",
            cliponaxis=False,
            hovertemplate="Diagnosis: %{customdata}<br>Number of discharges: %{text}<extra></extra>",
            customdata=by_dx["diagnosis"]
        )

        apply_standard_bar_layout(
            dx_bar,
            margin=dict(b=20),
            yaxis=dict(title_standoff=20),
            width=None,
        )
    else:
        dx_bar = px.bar()

    # ---------- Line chart: Yearly Discharges by Mental Health Diagnosis ----------
    if {"year", "diagnosis"}.issubset(dff.columns):
        by_ydx = (
            dff.groupby(["year", "diagnosis"])["record_id"].nunique()
            .reset_index(name="count")
            .sort_values(["year", "diagnosis"])
        )
        by_ydx["display_count"] = by_ydx["count"].apply(format_count_display)

        diagnoses = sort_opts(by_ydx["diagnosis"]) if "diagnosis" in by_ydx.columns else []
        if diagnoses:
            by_ydx["diagnosis"] = pd.Categorical(
                by_ydx["diagnosis"],
                categories=diagnoses,
                ordered=True,
            )

        diagnosis_line_fig = px.line(
            by_ydx,
            x="year",
            y="count",
            color="diagnosis",
            markers=True,
            custom_data=["display_count"],
            labels={"year": "Year", "count": "Discharges", "diagnosis": "Mental Health Diagnosis"},
            category_orders={"diagnosis": diagnoses} if diagnoses else None,
        )
        diagnosis_line_fig.update_traces(
            hovertemplate="Year %{x}<br>Diagnosis: %{fullData.name}<br>Discharges: %{customdata[0]}<extra></extra>"
        )
        max_y = int(by_ydx["count"].max()) if not by_ydx.empty else 0
        apply_standard_line_layout(
            diagnosis_line_fig,
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, max_y * 1.05 if max_y else 1], autorange=False),
            legend=dict(
                title_text="Mental Health Diagnosis",
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="left",
                x=0,
            ),
        )
    else:
        diagnosis_line_fig = px.line()

    # ---------- Line chart: Yearly Discharges by County ----------
    if {"county", "year"}.issubset(dff.columns):
        by_cy = (
            dff.groupby(["year", "county"])["record_id"].nunique()
            .reset_index(name="count")
        )
        if include_statewide_county_outputs:
            by_cy = append_statewide_aggregate_rows(by_cy, value_col="count", county_col="county")

        by_cy["display_count"] = by_cy["count"].apply(format_count_display)

        counties = statewide_first(sort_opts(by_cy["county"])) if "county" in by_cy.columns else []
        if counties:
            by_cy["county"] = pd.Categorical(by_cy["county"], categories=counties, ordered=True)

        line_fig = px.line(
            by_cy,
            x="year",
            y="count",
            color="county",
            markers=True,
            custom_data=["display_count"],
            labels={"year": "Year", "count": "Discharges", "county": "County"},
        )
        line_fig.update_traces(
            hovertemplate="Year %{x}<br>%{customdata[0]} discharges<extra></extra>"
        )
        max_y = int(by_cy["count"].max()) if not by_cy.empty else 0
        apply_standard_line_layout(
            line_fig,
            margin=dict(b=0),
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, max_y * 1.05 if max_y else 1], autorange=False),
        )
    else:
        line_fig = px.line()

    # ---------- Line chart: Yearly Discharges by Age Group ----------
    if {"year", "age_group"}.issubset(dff.columns):
        by_ya = (
            dff.groupby(["year", "age_group"])["record_id"].nunique()
            .reset_index(name="count")
        )
        by_ya["display_count"] = by_ya["count"].apply(format_count_display)

        age_groups = sort_opts(by_ya["age_group"]) if "age_group" in by_ya.columns else []
        if age_groups:
            by_ya["age_group"] = pd.Categorical(by_ya["age_group"], categories=age_groups, ordered=True)

        age_line_fig = px.line(
            by_ya,
            x="year",
            y="count",
            color="age_group",
            markers=True,
            custom_data=["display_count"],
            labels={"year": "Year", "count": "Discharges", "age_group": "Age Group"},
            category_orders={"age_group": age_groups} if age_groups else None,
        )
        age_line_fig.update_traces(
            hovertemplate="Year %{x}<br>Age Group: %{fullData.name}<br>Discharges: %{customdata[0]}<extra></extra>"
        )
        max_y = int(by_ya["count"].max()) if not by_ya.empty else 0
        apply_standard_line_layout(
            age_line_fig,
            margin=dict(b=0),
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, max_y * 1.05 if max_y else 1], autorange=False),
            legend=dict(title_text="Age Group"),
        )
    else:
        age_line_fig = px.line()

    # ---------- Stacked bar chart: Yearly Discharges by Sex at Birth ----------
    if {"year", "sex"}.issubset(dff.columns):
        by_ys = (
            dff.groupby(["year", "sex"])["record_id"].nunique()
            .reset_index(name="count")
            .sort_values(["year", "sex"])
        )
        sex_bar = px.bar(
            by_ys,
            x="year",
            y="count",
            color="sex",
            barmode="stack",
            labels={"year": "Year", "count": "Discharges", "sex": "Sex at Birth"},
            text=by_ys["count"].map(format_count_display)
        )
        sex_bar.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            cliponaxis=False
        )

        totals = by_ys.groupby("year")["count"].sum().reset_index()
        for _, row in totals.iterrows():
            sex_bar.add_annotation(
                x=row["year"],
                y=row["count"],
                text=format_count_display(row["count"]),
                showarrow=False,
                yshift=10,
                font=dict(size=12)
            )

        max_y = int(totals["count"].max()) if not totals.empty else 0
        apply_standard_bar_layout(
            sex_bar,
            margin=dict(b=0),
            yaxis=dict(range=[0, max_y * 1.15 if max_y else 1]),
        )
    else:
        sex_bar = px.bar()

    # ---------- Helper for the summary tables ----------
    def tbl(column, categories=None):
        """Build a small table for the summary."""
        if column not in dff.columns:
            return dbc.Alert(
                f"Column '{column}' not found.",
                color="warning",
                className="mb-0"
            )

        g = dff.groupby(column)["record_id"].nunique().reset_index(name="count")

        if column == "county" and include_statewide_county_outputs:
            g = append_statewide_aggregate_rows(g, value_col="count", county_col="county")

        if column == "county":
            categories = statewide_first(sort_opts(g[column]))

        if column == "year":
            g = g.sort_values(column, ascending=False)
        elif categories:
            g[column] = pd.Categorical(g[column], categories=categories, ordered=True)
            g = g.sort_values(column)
        else:
            g = g.sort_values("count", ascending=False)

        g["count"] = g["count"].map(format_count_display)

        header_labels = {
            "year": "Calendar Year",
            "age_group": "Age Group",
            "county": "County",
            "sex": "Sex at Birth",
            "race_ethnicity": "Race/Ethnicity",
            "hawaii_residency": "Hawaii Resident",
        }
        display_column = header_labels.get(column, column)
        g = g.rename(columns={column: display_column, "count": "Discharges"})

        return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)

    # Extract age groups dynamically from the filtered data using shared sort rules.
    age_groups = sort_opts(dff["age_group"]) if "age_group" in dff.columns and not dff.empty else None

    # Return all the updated visuals and tables to Dash
    return (
        format_count_display(filter_total),
        dx_bar,
        diagnosis_line_fig,
        line_fig,
        age_line_fig,
        sex_bar,
        tbl("year"),
        tbl("county"),
        tbl("age_group", age_groups),
        tbl("sex"),
        tbl("race_ethnicity"),
        tbl("hawaii_residency"),
    )
