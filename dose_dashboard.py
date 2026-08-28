# dose_dashboard.py — Drug Overdose Surveillance and Epidemiology (DOSE) page

from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import json
from theme import register_template
from dashboard_utils import (
    load_sql_query,
    sort_opts,
    opts_list,
    statewide_first,
    apply_county_filter,
    apply_year_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    make_kpi_card,
    make_left_sidebar,
    make_right_summary_tables_col,
    compute_last_updated_value,
    compute_adaptive_horizontal_bar_height,
    make_filters_card,
    dropdown_filter,
    format_count_display,
    wrap_axis_label,
    apply_standard_bar_layout,
    apply_standard_line_layout,
    apply_standard_map_layout,
    apply_standard_single_series_bar_trace,
    build_summary_count_table,
)

register_template()

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

# Trim whitespace from text columns (fixes issue where trailing spaces prevent filter matches)
for col in ["county", "city", "zip", "hawaii_residency", "age_group", "sex", "substance", "race_ethnicity"]:
    if col in df_dose_raw.columns:
        df_dose_raw[col] = df_dose_raw[col].astype(str).str.strip()

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
last_updated_value = compute_last_updated_value(df_dose_raw)

# Build the lists of choices for DOSE filters
dose_substance_opts = sort_opts(df_dose_raw["substance"])                       if "substance"  in df_dose_raw.columns else []
dose_county_opts    = sort_opts(df_dose_raw["county"])                           if "county"     in df_dose_raw.columns else []
dose_city_opts      = sort_opts(df_dose_raw["city"])                            if "city"       in df_dose_raw.columns else []
dose_zip_opts       = sort_opts(df_dose_raw["zip"])                             if "zip"        in df_dose_raw.columns else []
dose_year_opts      = sort_opts(df_dose_raw["year"])                             if "year"       in df_dose_raw.columns else []
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
kpi_card_dose = make_kpi_card(
    label="Distinct discharges per Drug Overdose Surveillance and Epidemiology (DOSE) definitions",
    count_id="kpi-total-dose-discharges",
)

# Card holding all the DOSE filter controls
# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card_dose = make_filters_card(
    card_id="dose-filters",
    title="Filter DOSE Data",
    filters=[
        dropdown_filter("Substance", "dose-substance-filter", options=opts_list(dose_substance_opts), multi=True, placeholder="All"),
        dropdown_filter("County", "dose-county-filter", options=opts_list(dose_county_opts), multi=True, placeholder="All"),
        dropdown_filter("City", "dose-city-filter", options=opts_list(dose_city_opts), multi=True, placeholder="All"),
        dropdown_filter("Calendar Year", "dose-year-filter", options=opts_list(dose_year_opts), multi=True, placeholder="All"),
        dropdown_filter("Hawaii Resident", "dose-hawaii-residency-filter", options=opts_list(dose_residency_opts), multi=True, placeholder="All"),
        dropdown_filter("Age Group", "dose-age-filter", options=opts_list(dose_age_opts), multi=True, placeholder="All"),
        dropdown_filter("Sex", "dose-sex-filter", options=opts_list(dose_sex_opts), multi=True, placeholder="All"),
        dropdown_filter("Race/Ethnicity", "dose-race-ethnicity-filter", options=opts_list(dose_race_ethnicity_opts), multi=True, placeholder="All"),
    ],
)

from section_texts import SECTION_TEXTS
dose_sidebar_text = SECTION_TEXTS.get("dose", [])

# ----------------------------
# Layout
# ----------------------------

def layout():
    """
    Build the DOSE dashboard layout.
    """
    line_h = "400px"
    bar_h = f"{compute_adaptive_horizontal_bar_height(len(dose_substance_opts))}px"
    map_h  = "500px"

    left_col = make_left_sidebar(
        kpi_card_dose,
        reset_filters_button_dose,
        filters_card_dose,
        helper_text=dose_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )

    def graph_panel(graph_id: str, height_px: str | None = None):
        return html.Div(
            [
                dcc.Graph(
                    id=graph_id,
                    style=({"height": height_px, "width": "100%"} if height_px else {"width": "100%"}),
                    config={"displayModeBar": True, "displaylogo": False},
                ),
            ],
            className="mb-4 p-2 bg-white rounded-2",
            style={"overflow": "visible"},
        )

    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([
                left_col,

                dbc.Col([
                    graph_panel("bar-dose"),
                    html.P("Bar chart showing nonfatal overdoses related to drug poisonings.", className="visually-hidden"),
                    graph_panel("year-diagnosis-lines-dose", line_h),
                    html.P("Line chart showing DOSE discharges by year and substance.", className="visually-hidden"),
                    dbc.Row([
                        graph_panel("map-county", map_h),
                        html.P("Choropleth map showing discharges by county.", className="visually-hidden"),
                    ]),
                ], xs=12, md=6),

                make_right_summary_tables_col(
                    [
                        ("County", "table-county-dose"),
                        ("Age Group", "table-age-dose"),
                        ("Sex", "table-sex-dose"),
                        ("Race/Ethnicity", "table-race-ethnicity-dose"),
                        ("Hawaii Resident", "table-hawaii-residency-dose"),
                    ],
                    xs=12,
                    md=3,
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
    Output("table-sex-dose", "children"),
    Output("table-race-ethnicity-dose", "children"),
    Output("table-hawaii-residency-dose", "children"),
    Input("dose-substance-filter", "value"),
    Input("dose-county-filter", "value"),
    Input("dose-city-filter", "value"),
    Input("dose-year-filter", "value"),
    Input("dose-hawaii-residency-filter", "value"),
    Input("dose-age-filter", "value"),
    Input("dose-sex-filter", "value"),
    Input("dose-race-ethnicity-filter", "value"),
)

def update_dashboard(substance, county, city, year, hawaii_residency, age, sex, race_ethnicity):
    """
    This function runs every time the user changes a DOSE filter.
    It updates all the DOSE visualizations and tables.
    """
    
    def apply_filter(frame, col, val):
        """Small helper for filter logic."""
        if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
            return frame
        if col == "city":
            # Normalize both city column and filter value(s) for robust matching
            def norm(s):
                return str(s).strip().lower() if s is not None else ""
            city_col = frame["city"].astype(str).apply(norm)
            if isinstance(val, (list, tuple)):
                norm_vals = set(norm(v) for v in val if v is not None)
                return frame[city_col.isin(norm_vals)]
            else:
                return frame[city_col == norm(val)]
        if isinstance(val, (list, tuple)):
            return frame[frame[col].isin(val)]
        return frame[frame[col] == val]
    
    # DOSE data
    dose_df = df_dose_raw.copy()

    # Only apply filters for columns that actually exist.
    if "substance" in dose_df.columns:          dose_df = apply_filter(dose_df, "substance", substance)
    if "county" in dose_df.columns:             dose_df = apply_county_filter(dose_df, county)
    if "city" in dose_df.columns:               dose_df = apply_filter(dose_df, "city", city)
    if "year" in dose_df.columns:               dose_df = apply_year_filter(dose_df, "year", year)
    if "hawaii_residency" in dose_df.columns:   dose_df = apply_filter(dose_df, "hawaii_residency", hawaii_residency)
    if "age_group" in dose_df.columns:          dose_df = apply_filter(dose_df, "age_group", age)
    if "sex" in dose_df.columns:                dose_df = apply_filter(dose_df, "sex", sex)
    if "race_ethnicity" in dose_df.columns:     dose_df = apply_filter(dose_df, "race_ethnicity", race_ethnicity)

    include_statewide_county_outputs = county_output_should_include_statewide(county)
    middle_title_margin = {"t": 60, "b": 50}
    
    filter_dose_total = dose_df["record_id"].nunique()
    kpi_dose_display = format_count_display(filter_dose_total)

    # ---------- Bar chart: Nonfatal overdoses related to poisonings ----------
    dose_bar = px.bar()
    bar_category_count = 1
    if {"substance"}.issubset(dose_df.columns):
        by_dose = (
            dose_df.groupby("substance")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )
        bar_category_count = max(1, len(by_dose))

        by_dose["substance_label"] = by_dose["substance"].apply(wrap_axis_label)

        by_dose["display_count"] = by_dose["count"].apply(format_count_display)

        dose_bar = px.bar(
            by_dose,
            x="count",
            y="substance_label",
            text="display_count",
            labels={"count": "Number of Discharges (Not mutually exclusive)", "substance_label": "Substance Type"},
        )
        
        apply_standard_single_series_bar_trace(dose_bar)

    apply_standard_bar_layout(
        dose_bar,
        title="Nonfatal Overdoses Related to Drug Poisonings (DOSE)",
        margin=middle_title_margin,
        height=compute_adaptive_horizontal_bar_height(
            bar_category_count,
            pixels_per_bar=30,
            base_padding=130,
        ),
    )

    # ---------- Line chart: Discharges by Year and Substance ----------
    dose_line = px.line()
    if {"year", "substance"}.issubset(dose_df.columns):
        by_year_substance = (
            dose_df.groupby(["year", "substance"])["record_id"].nunique()
            .reset_index(name="count")
        )

        # Exclude "All Drugs" from the line chart to improve visibility of individual substances
        by_year_substance = by_year_substance[
            by_year_substance["substance"].astype(str).str.strip().str.lower() != "all drugs"
        ]

        substances = sort_opts(dose_df["substance"]) if "substance" in dose_df.columns else []
        # Remove "All Drugs" from the category list as well
        substances = [s for s in substances if str(s).strip().lower() != "all drugs"]
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
            hovertemplate="Year %{x}<br>Substance: %{fullData.name}<br>%{y:,} discharges<extra></extra>"
        )

    apply_standard_line_layout(
        dose_line,
        title="DOSE Discharges by Year and Substance",
        margin=middle_title_margin,
    )

    # ---------- Helper for the summary tables ----------
    # Use shared build_summary_count_table for summary tables
    def summary_table(group_col, categories=None, filter_selection=None):
        return build_summary_count_table(
            dose_df,
            group_col=group_col,
            id_col="record_id",
            categories=categories,
            filter_selection=filter_selection,
            include_statewide_county=(group_col == "county" and include_statewide_county_outputs),
        )
    
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
            by_zip["display_count"] = by_zip["count"].apply(format_count_display)
            
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
            
            apply_standard_map_layout(
                map_fig,
                title="DOSE Discharges by County",
                margin=middle_title_margin,
            )
        else:
            print("[MAP] by_zip is empty!")
            map_fig = px.choropleth_mapbox()
            apply_standard_map_layout(
                map_fig,
                title="DOSE Discharges by County",
                margin=middle_title_margin,
            )
    else:
        print(f"[MAP] Missing zip column or no GeoJSON: zip in columns: {'zip' in dose_df.columns}, zips_geo: {zips_geo is not None}")
        map_fig = px.choropleth_mapbox()
        apply_standard_map_layout(
            map_fig,
            title="DOSE Discharges by County",
            margin=middle_title_margin,
        )

    # Return all the updated visuals and tables to Dash
    return (
        kpi_dose_display,
        dose_bar,
        dose_line,
        map_fig,
        summary_table("county", dose_county_opts, filter_selection=county),
        summary_table("age_group", dose_age_opts, filter_selection=age),
        summary_table("sex", dose_sex_opts, filter_selection=sex),
        summary_table("race_ethnicity", dose_race_ethnicity_opts, filter_selection=race_ethnicity),
        summary_table("hawaii_residency", dose_residency_opts, filter_selection=hawaii_residency),
    )