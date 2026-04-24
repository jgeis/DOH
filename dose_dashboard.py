# dose_dashboard.py — Drug Overdose Surveillance and Epidemiology (DOSE) page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import json
from dashboard_utils import (
    load_sql_query, sort_opts, opts_list, graph_block
)

# ----------------------------
# Data helpers
# ----------------------------

# Load the DOSE dataset once at startup.
sql_dose = load_sql_query("load_dose_data")
df_dose_raw = execute_query(sql_dose)

# Make the year column numeric when possible so graphs treat it as numbers
if "year" in df_dose_raw.columns:
    df_dose_raw["year"] = pd.to_numeric(df_dose_raw["year"], errors="coerce")

# For these columns, replace missing values with "Unknown"
for col in ["county", "city", "zip", "hawaii_residency", "age_group", "sex", "substance", "year", "race_ethnicity"]:
    if col in df_dose_raw.columns:
        df_dose_raw[col] = df_dose_raw[col].fillna("Unknown")

# Normalize ZIP values (5-digit strings) so they match the GeoJSON
if "zip" in df_dose_raw.columns:
    df_dose_raw["zip"] = (
        df_dose_raw["zip"]
        .astype(str)
        .str.extract(r"(\d{5})", expand=False)
        .fillna("")
    )

# Count how many unique DOSE records we have to show on the KPI card.
total_dose_unique = df_dose_raw["record_id"].nunique()

# Build the lists of choices for DOSE filters
dose_substance_opts = sort_opts(df_dose_raw["substance"])                       if "substance"  in df_dose_raw.columns else []
dose_county_opts    = sort_opts(df_dose_raw["county"])                          if "county"     in df_dose_raw.columns else []
dose_city_opts      = sort_opts(df_dose_raw["city"])                            if "city"       in df_dose_raw.columns else []
dose_zip_opts       = sort_opts(df_dose_raw["zip"])                             if "zip"        in df_dose_raw.columns else []
dose_year_opts      = sorted(df_dose_raw["year"].dropna().unique().tolist())    if "year"       in df_dose_raw.columns else []
dose_residency_opts = sort_opts(df_dose_raw["hawaii_residency"])                if "hawaii_residency" in df_dose_raw.columns else []
dose_age_opts       = sort_opts(df_dose_raw["age_group"])                       if "age_group"  in df_dose_raw.columns else []
dose_sex_opts       = sort_opts(df_dose_raw["sex"])                             if "sex"        in df_dose_raw.columns else []
dose_race_ethnicity_opts = sort_opts(df_dose_raw["race_ethnicity"])             if "race_ethnicity" in df_dose_raw.columns else []

# ----------------------------
# UI Components
# ----------------------------

# This link helps keyboard and screen reader users jump straight to the filters.
skip_link = html.A(
    "Skip to filters",
    href="#dose-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

reset_filters_button_dose = dbc.Button(
    "Reset All Filters",
    id="dose-reset-filters-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)

# Big green card for DOSE total
kpi_card_dose = dbc.Card(
    dbc.CardBody([
        html.H2(id="kpi-total-dose-discharges", className="text-white"),
        html.Small("Distinct discharges per Drug Overdose Surveillance and Epidemiology (DOSE) definitions", className="card-title text-white")
    ]),
    className="bg-success text-center mb-4"
)

# Card holding all the DOSE filter controls
filters_card_dose = dbc.Card(
    dbc.CardBody([
        html.H5("Filter DOSE Data"),

        html.Label("Substance", htmlFor="dose-substance-filter", className="form-label"),
        dcc.Dropdown(
            id="dose-substance-filter",
            options=opts_list(dose_substance_opts),
            multi=True,
            placeholder="Substance",
            className="mb-2"
        ),

        html.Label("County", htmlFor="dose-county-filter", className="form-label"),
        dcc.Dropdown(
            id="dose-county-filter",
            options=opts_list(dose_county_opts),
            multi=True,
            placeholder="County",
            className="mb-2"
        ),
        html.Label("City", htmlFor="dose-city-filter", tabIndex=3, className="form-label"),
        dcc.Dropdown(
            id="dose-city-filter", options=opts_list(dose_city_opts), multi=True,
            placeholder="City", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Year", htmlFor="dose-year-filter", tabIndex=3, className="form-label"),
        dcc.Dropdown(
            id="dose-year-filter", options=opts_list(dose_year_opts), multi=True,
            placeholder="Year", className="mb-2",
            persistence=True, persistence_type="session"
        ),
        html.Label("Hawaii Resident", htmlFor="dose-hawaii-residency-filter", tabIndex=4, className="form-label"),
        dcc.Dropdown(
            id="dose-hawaii-residency-filter", options=opts_list(dose_residency_opts), multi=True,
            placeholder="Hawaii Resident", className="mb-2",
            persistence=True, persistence_type="session"
        ),

        html.Label("Age Group", htmlFor="dose-age-filter", tabIndex=5, className="form-label"),
        dcc.Dropdown(
            id="dose-age-filter", options=opts_list(dose_age_opts), multi=True,
            placeholder="Age Group", className="mb-2",
            persistence=True, persistence_type="session"
        ),

        html.Label("Sex", htmlFor="dose-sex-filter", tabIndex=6, className="form-label"),
        dcc.Dropdown(
            id="dose-sex-filter", options=opts_list(dose_sex_opts), multi=True,
            placeholder="Sex", className="mb-2",
            persistence=True, persistence_type="session"
        ),

        html.Label("Race/Ethnicity", htmlFor="dose-race-ethnicity-filter", tabIndex=7, className="form-label"),
        dcc.Dropdown(
            id="dose-race-ethnicity-filter", options=opts_list(dose_race_ethnicity_opts), multi=True,
            placeholder="Race/Ethnicity", className="mb-0",
            persistence=True, persistence_type="session"
        ),
    ]),
    id="dose-filters",
    className="mb-4"
)

# ----------------------------
# Layout
# ----------------------------

def layout():
    """
    Build the DOSE dashboard layout.
    """
    line_h = "400px"
    bar_h  = "360px"
    pie_h  = "260px"
    map_h  = "500px"

    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([
                dbc.Col([
                    kpi_card_dose,
                    reset_filters_button_dose,
                    filters_card_dose,
                    html.Div(
                        className="mt-3 text-muted small",
                        children=[
                            html.P("* Values less than 10 are suppressed for privacy reasons and are displayed as <10.", className="mb-2"),
                            html.P("† Unintentional and undetermined intent drug overdose death data sourced from the State Unintentional Drug Overdose Reporting System (SUDORS).", className="mb-2"),
                            html.P("‡ Overdose death data sourced from the CDC Wide-ranging ONline Data for Epidemiologic Research (WONDER).", className="mb-0"),
                        ]
                    )
                ], xs=12, md=3),

                dbc.Col([
                    graph_block("bar-dose", "Nonfatal Overdoses Related to Drug Poisonings", bar_h),
                    graph_block("year-diagnosis-lines-dose", "DOSE Discharges by Year and Substance", line_h),
                    dbc.Row([
                        graph_block("map-county", "Discharges by County", map_h),
                    ]),
                ], xs=12, md=6),

                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6("By County", className="mb-2"),
                                        html.Div(
                                            id="table-county-dose",
                                            className="mobile-side-table",
                                            style={"overflowX": "auto"}
                                        ),
                                    ],
                                    xs=6, md=12, className="pe-1 mb-3",
                                ),
                                dbc.Col(
                                    [
                                        html.H6("By Age Group", className="mb-2"),
                                        html.Div(
                                            id="table-age-dose",
                                            className="mobile-side-table",
                                            style={"overflowX": "auto"}
                                        ),
                                    ],
                                    xs=6, md=12, className="ps-1 mb-3",
                                ),
                            ],
                            className="g-2"
                        ),
                        graph_block("sex-pie-dose", "Discharges by Gender", pie_h),
                    ],
                    xs=12, md=3
                )
            ], className="g-3"),
            id="dose-section",
        ),
        html.Hr(className="my-5"),
        html.P(
            "This section presents emergency department (ED) discharge data categorized according to CDC's Drug Overdose "
            "Surveillance and Epidemiology (DOSE) definitions and tracks nonfatal overdoses by specific types—such as opioids, "
            "stimulants, and other substances—using standardized CDC criteria to ensure accuracy and comparability. Data elements "
            "include patient demographics (i.e., age, sex at birth), discharge outcomes, and temporal trends by month and year.",
            className="mt-4 text-muted small"
        ),
    ], fluid=True, className="p-2")


# This is the default layout used when the app imports this file.
layout = layout()

# ----------------------------
# Callbacks for DOSE
# ----------------------------

@callback(
    Output("dose-substance-filter", "value"),
    Output("dose-county-filter", "value"),
    Output("dose-city-filter", "value"),
    Output("dose-year-filter", "value"),
    Output("dose-hawaii-residency-filter", "value"),
    Output("dose-age-filter", "value"),
    Output("dose-sex-filter", "value"),
    Output("dose-race-ethnicity-filter", "value"),
    Input("dose-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_dose_filters(_n_clicks):
    return None, None, None, None, None, None, None, None


@callback(
    Output("kpi-total-dose-discharges", "children"),
    Output("bar-dose", "figure"),
    Output("year-diagnosis-lines-dose", "figure"),
    Output("map-county", "figure"),
    Output("table-county-dose", "children"),
    Output("table-age-dose", "children"),
    Output("sex-pie-dose", "figure"),
    Input("dose-substance-filter", "value"),
    Input("dose-county-filter", "value"),
    Input("dose-city-filter", "value"),
    Input("dose-year-filter", "value"),
    Input("dose-hawaii-residency-filter", "value"),
    Input("dose-age-filter", "value"),
    Input("dose-sex-filter", "value"),
    Input("dose-race-ethnicity-filter", "value"),
)

def update_dose_section(substance, county, city, year, hawaii_residency, age, sex, race_ethnicity):
    """
    This function runs every time the user changes a DOSE filter.
    It updates all the DOSE visualizations and tables.
    """
    
    def apply_filter(frame, col, val):
        """Small helper for filter logic."""
        if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
            return frame
        if isinstance(val, (list, tuple)):
            return frame[frame[col].isin(val)]
        return frame[frame[col] == val]
    
    # DOSE data
    dose_df = df_dose_raw.copy()

    # Only apply filters for columns that actually exist.
    if "substance" in dose_df.columns:          dose_df = apply_filter(dose_df, "substance", substance)
    if "county" in dose_df.columns:             dose_df = apply_filter(dose_df, "county", county)
    if "city" in dose_df.columns:               dose_df = apply_filter(dose_df, "city", city)
    if "year" in dose_df.columns:               dose_df = apply_filter(dose_df, "year", year)
    if "hawaii_residency" in dose_df.columns:   dose_df = apply_filter(dose_df, "hawaii_residency", hawaii_residency)
    if "age_group" in dose_df.columns:          dose_df = apply_filter(dose_df, "age_group", age)
    if "sex" in dose_df.columns:                dose_df = apply_filter(dose_df, "sex", sex)
    if "race_ethnicity" in dose_df.columns:     dose_df = apply_filter(dose_df, "race_ethnicity", race_ethnicity)
    
    filter_dose_total = dose_df["record_id"].nunique()
    kpi_dose_display = "<11" if filter_dose_total < 11 else f"{filter_dose_total:,}"

    # ---------- Bar chart: Nonfatal overdoses related to poisonings ----------
    if {"substance"}.issubset(dose_df.columns):
        by_dose = (
            dose_df.groupby("substance")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )

        def ellipsize(text, max_len=25):
            if text is None:
                return text
            return text if len(text) <= max_len else text[:max_len] + "..."
        
        by_dose["substance_label"] = by_dose["substance"].apply(ellipsize)

        by_dose["display_count"] = by_dose["count"].apply(
            lambda x: "<11" if x < 11 else f"{int(x):,}"
        )

        dose_bar = px.bar(
            by_dose,
            x="count",
            y="substance_label",
            text="display_count",
            labels={"count": "Number of Discharges (Not mutually exclusive)", "substance_label": "Substance Type"},
        )
        
        dose_bar.update_traces(
            textposition="outside",
            cliponaxis=False,
            customdata=dose_df["substance"],
            hovertemplate="Substance: %{customdata}<br>Count: %{text}<extra></extra>"
        )

        dose_bar.update_layout(margin=dict(l=0, r=40, t=10, b=10))
    else:
        dose_bar = px.bar()

    # ---------- Line chart: Discharges by Year and Substance ----------
    if {"year", "substance"}.issubset(dose_df.columns):
        by_year_substance = (
            dose_df.groupby(["year", "substance"])["record_id"].nunique()
            .reset_index(name="count")
        )
        substances = sort_opts(dose_df["substance"]) if "substance" in dose_df.columns else []
        if substances:
            by_year_substance["substance"] = pd.Categorical(by_year_substance["substance"], categories=substances, ordered=True)

        dose_line = px.line(
            by_year_substance,
            x="year",
            y="count",
            color="substance",
            markers=True,
            labels={"year": "Year", "count": "Discharges", "substance": "Substance"},
        )
        dose_line.update_traces(
            hovertemplate="Year %{x}<br>%{y:,} discharges<extra></extra>"
        )
        dose_line.update_layout(
            margin=dict(l=0, r=20, t=10, b=0),
            xaxis=dict(dtick=1)
        )
    else:
        dose_line = px.line()

    # ---------- Helper for the summary tables ----------
    def tbl(column, categories=None):
        """Build a small table for the DOSE summary."""
        if column not in dose_df.columns:
            return dbc.Alert(
                f"Column '{column}' not found.",
                color="warning",
                className="mb-0"
            )

        g = dose_df.groupby(column)["record_id"].nunique().reset_index(name="count")

        if categories:
            g[column] = pd.Categorical(g[column], categories=categories, ordered=True)
            g = g.sort_values(column)
        else:
            g = g.sort_values("count", ascending=False)

        g["count"] = g["count"].map(lambda x: "<11" if x < 11 else f"{int(x):,}")

        header_labels = {
            "age_group": "Age Group",
            "county": "County"
        }
        display_column = header_labels.get(column, column)
        g = g.rename(columns={column: display_column, "count": "Discharges"})

        return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)
    
    # ---------- Pie chart: Discharges by Gender ----------
    if "sex" in dose_df.columns:
        pie_df = (
            dose_df.groupby("sex")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        pie_df["display_count"] = pie_df["count"].apply(
            lambda x: "<11" if x < 11 else f"{int(x):,}"
        )
        dose_sex_pie = px.pie(
            pie_df,
            names="sex",
            values="count",
            hole=0.35,
            custom_data=["display_count"],
        )
        dose_sex_pie.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%} (%{customdata[0]})",
            hovertemplate="%{label}: %{customdata[0]} (%{percent:.1%})<extra></extra>"
        )
        dose_sex_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    else:
        dose_sex_pie = px.pie()

    # Extract age groups dynamically from the filtered DOSE data
    if "age_group" in dose_df.columns and not dose_df.empty:
        _dag_sorted = sorted([v for v in dose_df["age_group"].unique() if v not in ("<18", "Unknown")])
        _dag_prefix = ["<18"] if "<18" in dose_df["age_group"].values else []
        _dag_unknown = ["Unknown"] if "Unknown" in dose_df["age_group"].values else []
        dose_age_groups = _dag_prefix + _dag_sorted + _dag_unknown
    else:
        dose_age_groups = None

    # ---------- Map: Discharges by ZIP Code ----------
    try:
        with open("assets/hawaii_zipcodes.geojson") as f:
            zips_geo = json.load(f)
        print(f"[MAP] Loaded GeoJSON with {len(zips_geo.get('features', []))} features")
    except Exception as e:
        print(f"[MAP ERROR] Failed to load GeoJSON: {e}")
        zips_geo = None
    
    if {"zip"}.issubset(dose_df.columns) and zips_geo:
        by_zip = (
            dose_df[dose_df["zip"] != ""]
            .groupby("zip")["record_id"]
            .nunique()
            .reset_index(name="count")
        )
        print(f"[MAP] by_zip has {len(by_zip)} rows")
        print(f"[MAP] Sample ZIPs: {by_zip['zip'].head(3).tolist()}")
        
        if not by_zip.empty:
            by_zip["display_count"] = by_zip["count"].apply(lambda x: "<11" if x < 11 else str(x))
            
            map_fig = px.choropleth_mapbox(
                by_zip,
                geojson=zips_geo,
                locations="zip",
                featureidkey="properties.geoid20",
                color="count",
                color_continuous_scale="Blues",
                mapbox_style="carto-positron",
                zoom=6.2,
                center={"lat": 20.8, "lon": -157.1},
                opacity=0.7,
                custom_data=["display_count"],
                labels={"count": "Discharges", "zip": "ZIP Code"},
            )
            
            map_fig.update_traces(
                hovertemplate="<b>ZIP Code: %{location}</b><br>Discharges: %{customdata[0]}<extra></extra>"
            )
            
            map_fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0)
            )
        else:
            print("[MAP] by_zip is empty!")
            map_fig = px.choropleth_mapbox()
    else:
        print(f"[MAP] Missing zip column or no GeoJSON: zip in columns: {'zip' in dose_df.columns}, zips_geo: {zips_geo is not None}")
        map_fig = px.choropleth_mapbox()

    # Return all the updated visuals and tables to Dash
    return (
        kpi_dose_display,
        dose_bar,
        dose_line,
        map_fig,
        tbl("county"),
        tbl("age_group", dose_age_groups),
        dose_sex_pie,
    )
