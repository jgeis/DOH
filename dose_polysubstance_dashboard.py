# dose_polysubstance_dashboard.py — DOSE polysubstance co-occurrence dashboard

from pathlib import Path
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from theme import register_template
from db_utils import execute_query
from dashboard_utils import (
    apply_year_filter,
    make_kpi_card,
    make_left_sidebar,
    make_right_summary_tables_col,
    compute_last_updated_value,
    compute_adaptive_horizontal_bar_height,
    make_filters_card,
    dropdown_filter,
    graph_block,
    sort_opts,
    statewide_first,
    apply_county_filter,
    county_output_should_include_statewide,
    append_statewide_aggregate_rows,
    format_count_display,
    build_suppressed_percentage_columns,
    format_display_list,
    wrap_axis_label,
    apply_standard_single_series_bar_trace,
    apply_standard_bar_layout,
    apply_standard_line_layout,
    apply_standard_non_axis_layout,
    build_summary_count_table,
    load_sql_query,
)

register_template()

# ---------- DB → DataFrame ----------
def load_df():
    """Load DOSE polysubstance data from the database."""
    sql = load_sql_query("load_dose_polysubstance_data")
    df = execute_query(sql)
    
    if df.empty:
        raise RuntimeError("Query returned 0 rows. Check DB and queries.sql.")
    
    # Clean up text columns
    want_obj = ["county", "city", "hawaii_residency", "age_group", "sex", "substance", "race_ethnicity"]
    for c in want_obj:
        if c in df.columns:
            df[c] = (
                df[c].astype(str).str.strip()
                .replace({"nan": np.nan, "None": np.nan})
                .fillna("Unknown")
            )
    
    # Make year numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    
    print(f"[load_df] DOSE polysubstance rows={len(df):,}  cols={list(df.columns)}")
    return df


# ---------- Helper functions ----------
def apply_filter(frame: pd.DataFrame, col: str, val) -> pd.DataFrame:
    """Apply a filter to a column."""
    if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
        return frame.copy()
    if isinstance(val, (list, tuple)):
        return frame[frame[col].isin(val)].copy()
    return frame[frame[col] == val].copy()


def records_matching_selected_substances(frame: pd.DataFrame, selected_values) -> pd.DataFrame:
    """
    Return rows from records that contain ANY of the selected substances.
    This keeps all rows for those records (including co-occurring substances).
    """
    if not selected_values:
        return frame.copy()
    
    if not {"record_id", "substance"}.issubset(frame.columns):
        return frame.iloc[0:0].copy()
    
    selected = [str(v).strip() for v in selected_values if str(v).strip()]
    if not selected:
        return frame.copy()
    
    # Find records that contain any of the selected substances
    selected_set = set(selected)
    matched_ids = frame[frame["substance"].astype(str).isin(selected_set)]["record_id"].unique()
    
    # Return all rows for those records (including co-occurring substances)
    return frame[frame["record_id"].isin(matched_ids)].copy()


def build_sunburst_cooccurrence_data(df):
    """Build Primary -> Also Found rows for sunburst co-occurrence visualization."""
    results = []
    grouped = df.groupby("record_id")["substance"].unique()
    for record_id, substances in grouped.items():
        for i in range(len(substances)):
            for j in range(len(substances)):
                if i != j:
                    results.append({
                        "record_id": record_id,
                        "Primary": substances[i],
                        "Also Found": substances[j],
                    })
    
    if not results:
        # Return empty DataFrame with proper columns
        return pd.DataFrame(columns=['record_id', 'Primary', 'Also Found'])
    
    return pd.DataFrame(results)


def build_cooccurrence_data(df):
    """Build data for bar chart showing co-occurrence percentages."""
    results = []
    
    for primary_substance in df['substance'].unique():
        records = df[df['substance'] == primary_substance]['record_id'].unique()
        total = len(records)
        
        if total == 0:
            continue
        
        for other_substance in df['substance'].unique():
            if other_substance != primary_substance:
                count = df[
                    (df['record_id'].isin(records)) & 
                    (df['substance'] == other_substance)
                ]['record_id'].nunique()
                
                results.append({
                    'Primary': primary_substance,
                    'Also Found': other_substance,
                    'Percentage': (count / total) * 100,
                    'Count': count,
                    'Total': total
                })
    
    if not results:
        # Return empty DataFrame with proper columns
        return pd.DataFrame(columns=['Primary', 'Also Found', 'Percentage', 'Count', 'Total'])
    
    return pd.DataFrame(results)


# Load data
df_raw = load_df()

# Filter out unknown ages and invalid years
if "year" in df_raw.columns:
    mask_year = df_raw["year"].notna()
else:
    mask_year = True

def is_unknown_age(val):
    s = (str(val) if val is not None else "").strip().lower()
    return s in {"", "unknown", "unk", "n/a", "na"}

mask_age = ~df_raw["age_group"].apply(is_unknown_age) if "age_group" in df_raw.columns else True

df_raw = df_raw[mask_year & mask_age].copy()
last_updated_value = compute_last_updated_value(df_raw)

# Build filter options
def opts(values):
    return [{"label": v, "value": v} for v in values]

substance_opts = sort_opts(df_raw["substance"]) if "substance" in df_raw.columns else []
county_opts = sort_opts(df_raw["county"]) if "county" in df_raw.columns else []
city_opts = sort_opts(df_raw["city"]) if "city" in df_raw.columns else []
age_opts = sort_opts(df_raw["age_group"]) if "age_group" in df_raw.columns else []
sex_opts = sort_opts(df_raw["sex"]) if "sex" in df_raw.columns else []
race_ethnicity_opts = sort_opts(df_raw["race_ethnicity"]) if "race_ethnicity" in df_raw.columns else []
year_opts = sort_opts(df_raw["year"]) if "year" in df_raw.columns else []
residency_opts = sort_opts(df_raw["hawaii_residency"]) if "hawaii_residency" in df_raw.columns else []

kpi_total = df_raw["record_id"].nunique() if "record_id" in df_raw.columns else 0

from section_texts import SECTION_TEXTS
dose_polysubstance_sidebar_text = SECTION_TEXTS.get("dose-polysubstance", [])

# Filters card
filters_card = make_filters_card(
    card_id="dose-polysubstance-filters",
    title="Filter Data",
    filters=[
        dropdown_filter("Substance Type", "dose-polysubstance-substance-filter", options=opts(substance_opts), multi=True, placeholder="All"),
        dropdown_filter("Calendar Year", "dose-polysubstance-year-filter", options=opts(year_opts), multi=True, placeholder="All"),
        dropdown_filter("County", "dose-polysubstance-county-filter", options=opts(county_opts), multi=True, placeholder="All"),
        dropdown_filter("City", "dose-polysubstance-city-filter", options=opts(city_opts), multi=True, placeholder="All"),
        dropdown_filter("Age Group", "dose-polysubstance-age-filter", options=opts(age_opts), multi=True, placeholder="All"),
        dropdown_filter("Sex", "dose-polysubstance-sex-filter", options=opts(sex_opts), multi=True, placeholder="All"),
        dropdown_filter("Race/Ethnicity", "dose-polysubstance-race-filter", options=opts(race_ethnicity_opts), multi=True, placeholder="All"),
        dropdown_filter("Hawaii Resident", "dose-polysubstance-residency-filter", options=opts(residency_opts), multi=True, placeholder="All"),
    ],
)

# ---------- UI Layout ----------
skip_link = html.A(
    "Skip to filters",
    href="#dose-polysubstance-filters",
    className="visually-hidden-focusable",
    tabIndex=0
)

kpi_card = make_kpi_card(
    label="DOSE Polysubstance Records",
    count_id="dose-polysubstance-kpi-total",
)

reset_filters_button = dbc.Button(
    "Reset All Filters",
    id="dose-polysubstance-reset-filters-btn",
    color="secondary",
    outline=True,
    className="w-100 mb-3",
    n_clicks=0,
)


def layout():
    """Build the DOSE polysubstance dashboard layout."""
    
    left_col = make_left_sidebar(
        kpi_card,
        reset_filters_button,
        filters_card,
        helper_text=dose_polysubstance_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=3,
    )
    
    center_col = dbc.Col([
        graph_block("dose-polysubstance-substance-bar", "DOSE Discharges by Substance Type"),
        html.P("Bar chart showing DOSE discharges by substance type.", className="visually-hidden"),
        
        graph_block("dose-polysubstance-year-line", "Yearly DOSE Discharges by Substance", "400px"),
        html.P("Line chart showing yearly DOSE discharges by substance.", className="visually-hidden"),
        
        graph_block("dose-polysubstance-county-line", "Yearly DOSE Discharges by County", "400px"),
        html.P("Line chart showing yearly DOSE discharges by county.", className="visually-hidden"),
        
        graph_block("dose-polysubstance-sunburst", "Substance Co-occurrence Sunburst", "500px"),
        html.P("Sunburst chart showing substance co-occurrence patterns.", className="visually-hidden"),
        
        graph_block("dose-polysubstance-cooccurrence-bar", "Co-occurrence by Selected Substance", "500px"),
        html.P("Bar chart showing co-occurrence percentages for selected substance.", className="visually-hidden"),
    ], xs=12, md=6)
    
    right_col = make_right_summary_tables_col([
        ("County", "dose-polysubstance-table-county"),
        ("Age Group", "dose-polysubstance-table-age"),
        ("Sex", "dose-polysubstance-table-sex"),
        ("Race/Ethnicity", "dose-polysubstance-table-race"),
        ("Hawaii Resident", "dose-polysubstance-table-residency"),
    ], xs=12, md=3)
    
    return dbc.Container([
        skip_link,
        html.Div(
            dbc.Row([left_col, center_col, right_col], className="g-3"),
            id="dose-polysubstance-section",
        ),
        html.Hr(className="my-5"),
        html.P(
            "This section analyzes polysubstance patterns in DOSE (Drug Overdose Surveillance and Epidemiology) data, "
            "showing which substances commonly occur together in overdose events.",
            className="mt-4 text-muted small"
        ),
    ], fluid=True, className="p-2")


layout = layout()

# ---------- Callbacks ----------
@callback(
    Output("dose-polysubstance-substance-filter", "value"),
    Output("dose-polysubstance-year-filter", "value"),
    Output("dose-polysubstance-county-filter", "value"),
    Output("dose-polysubstance-city-filter", "value"),
    Output("dose-polysubstance-age-filter", "value"),
    Output("dose-polysubstance-sex-filter", "value"),
    Output("dose-polysubstance-race-filter", "value"),
    Output("dose-polysubstance-residency-filter", "value"),
    Input("dose-polysubstance-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_n_clicks):
    return None, None, None, None, None, None, None, None


@callback(
    Output("dose-polysubstance-kpi-total", "children"),
    Output("dose-polysubstance-substance-bar", "figure"),
    Output("dose-polysubstance-year-line", "figure"),
    Output("dose-polysubstance-county-line", "figure"),
    Output("dose-polysubstance-sunburst", "figure"),
    Output("dose-polysubstance-cooccurrence-bar", "figure"),
    Output("dose-polysubstance-table-county", "children"),
    Output("dose-polysubstance-table-age", "children"),
    Output("dose-polysubstance-table-sex", "children"),
    Output("dose-polysubstance-table-race", "children"),
    Output("dose-polysubstance-table-residency", "children"),
    Input("dose-polysubstance-substance-filter", "value"),
    Input("dose-polysubstance-year-filter", "value"),
    Input("dose-polysubstance-county-filter", "value"),
    Input("dose-polysubstance-city-filter", "value"),
    Input("dose-polysubstance-age-filter", "value"),
    Input("dose-polysubstance-sex-filter", "value"),
    Input("dose-polysubstance-race-filter", "value"),
    Input("dose-polysubstance-residency-filter", "value"),
)
def update_dashboard(substance, year, county, city, age, sex, race, residency):
    """Update all visualizations based on filter selections."""
    
    # Apply filters
    df = df_raw.copy()
    
    # For polysubstance dashboard, we need to handle substance filter specially:
    # Keep all rows for records that contain the selected substance(s)
    has_substance_filter = substance is not None and len(substance) > 0
    if has_substance_filter and "substance" in df.columns:
        df = records_matching_selected_substances(df, substance)
    
    # Apply other filters normally
    if "year" in df.columns:
        df = apply_year_filter(df, "year", year)
    if "county" in df.columns:
        df = apply_county_filter(df, county)
    if "city" in df.columns:
        df = apply_filter(df, "city", city)
    if "age_group" in df.columns:
        df = apply_filter(df, "age_group", age)
    if "sex" in df.columns:
        df = apply_filter(df, "sex", sex)
    if "race_ethnicity" in df.columns:
        df = apply_filter(df, "race_ethnicity", race)
    if "hawaii_residency" in df.columns:
        df = apply_filter(df, "hawaii_residency", residency)
    
    include_statewide_county_outputs = county_output_should_include_statewide(county)
    
    # KPI
    filter_total = df["record_id"].nunique()
    kpi_display = format_count_display(filter_total)
    
    # Substance bar chart - show all or co-occurring
    if has_substance_filter:
        # Show co-occurring substances (exclude the selected ones)
        cooccur_df = df[~df['substance'].isin(substance)]
        by_substance = (
            cooccur_df.groupby("substance")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )
        chart_title_suffix = f" (co-occurring with {format_display_list(substance)})"
    else:
        # Show all substances
        by_substance = (
            df.groupby("substance")["record_id"].nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )
        chart_title_suffix = ""
    
    by_substance["substance_label"] = by_substance["substance"].apply(wrap_axis_label)
    by_substance["display_count"] = by_substance["count"].apply(format_count_display)
    
    substance_bar = px.bar(
        by_substance,
        x="count",
        y="substance_label",
        text="display_count",
        labels={"count": "Number of Records", "substance_label": "Substance"},
    )
    apply_standard_single_series_bar_trace(substance_bar)
    apply_standard_bar_layout(substance_bar)
    
    # Year line chart - by polysubstance or co-occurring
    if {"year", "substance"}.issubset(df.columns):
        if has_substance_filter:
            # Show co-occurring substances (exclude the selected ones)
            year_df = df[~df['substance'].isin(substance)]
        else:
            year_df = df.copy()
        
        by_year_substance = (
            year_df.groupby(["year", "substance"])["record_id"].nunique()
            .reset_index(name="count")
        )
        
        substances = sort_opts(year_df["substance"])
        if substances:
            by_year_substance["substance"] = pd.Categorical(
                by_year_substance["substance"], categories=substances, ordered=True
            )
        
        year_line = px.line(
            by_year_substance,
            x="year",
            y="count",
            color="substance",
            markers=True,
            labels={"year": "Year", "count": "Records", "substance": "Substance"},
        )
        year_line.update_traces(
            hovertemplate="Year %{x}<br>Substance: %{fullData.name}<br>%{y:,} records<extra></extra>"
        )
        apply_standard_line_layout(year_line)
    else:
        year_line = px.line()
    
    # County line chart
    if {"year", "county"}.issubset(df.columns):
        by_year_county = (
            df.groupby(["year", "county"])["record_id"].nunique()
            .reset_index(name="count")
        )
        
        counties = sort_opts(df["county"])
        if counties:
            by_year_county["county"] = pd.Categorical(
                by_year_county["county"], categories=counties, ordered=True
            )
        
        county_line = px.line(
            by_year_county,
            x="year",
            y="count",
            color="county",
            markers=True,
            labels={"year": "Year", "count": "Records", "county": "County"},
        )
        county_line.update_traces(
            hovertemplate="Year %{x}<br>County: %{fullData.name}<br>%{y:,} records<extra></extra>"
        )
        apply_standard_line_layout(county_line)
    else:
        county_line = px.line()
    
    # Sunburst
    sunburst_data = build_sunburst_cooccurrence_data(df)
    if not sunburst_data.empty:
        agg = sunburst_data.groupby(["Primary", "Also Found"])["record_id"].nunique().reset_index(name="count")
        
        sunburst_fig = px.sunburst(
            agg,
            path=["Primary", "Also Found"],
            values="count",
            labels={"count": "Records", "Primary": "Primary Substance", "Also Found": "Co-occurring Substance"},
        )
        sunburst_fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Records: %{value:,}<extra></extra>"
        )
        apply_standard_non_axis_layout(sunburst_fig)
    else:
        sunburst_fig = go.Figure()
    

# Co-occurrence bar chart
    if has_substance_filter and len(substance) == 1:
        # Show detailed co-occurrence for single selected substance
        cooccur_data = build_cooccurrence_data(df)
        selected_substance = substance[0]
        
        if not cooccur_data.empty and 'Primary' in cooccur_data.columns:
            cooccur_filtered = cooccur_data[cooccur_data['Primary'] == selected_substance].copy()
        else:
            cooccur_filtered = pd.DataFrame()
        
        print(f"[update_dashboard] cooccur_filtered rows={len(cooccur_filtered)} for substance={selected_substance}")

        if not cooccur_filtered.empty:
            cooccur_filtered = cooccur_filtered.sort_values("Percentage", ascending=True)
            cooccur_filtered["display_pct"] = cooccur_filtered["Percentage"].apply(lambda x: f"{x:.1f}%")
            
            cooccur_bar = px.bar(
                cooccur_filtered,
                x="Percentage",
                y="Also Found",
                text="display_pct",
                orientation="h",
                labels={"Percentage": "Co-occurrence %", "Also Found": "Co-occurring Substance"},
            )
            apply_standard_single_series_bar_trace(cooccur_bar)
            apply_standard_bar_layout(cooccur_bar)
        else:
            cooccur_bar = px.bar()
            
    elif has_substance_filter:
        # Multiple substances selected - show grouped bar
        cooccur_data = build_cooccurrence_data(df)
        
        if not cooccur_data.empty and 'Primary' in cooccur_data.columns:
            cooccur_filtered = cooccur_data[cooccur_data['Primary'].isin(substance)].copy()
        else:
            cooccur_filtered = pd.DataFrame()
        
        if not cooccur_filtered.empty:
            cooccur_bar = px.bar(
                cooccur_filtered,
                x="Percentage",
                y="Also Found",
                color="Primary",
                barmode="group",
                orientation="h",
                labels={"Percentage": "Co-occurrence %", "Also Found": "Co-occurring Substance", "Primary": "Primary Substance"},
            )
            apply_standard_bar_layout(cooccur_bar)
        else:
            cooccur_bar = px.bar()
            
    else:
        # No substance filter - show grouped bar for ALL substances
        cooccur_data = build_cooccurrence_data(df)
        
        if not cooccur_data.empty and 'Primary' in cooccur_data.columns:
            cooccur_bar = px.bar(
                cooccur_data, # Use the full, unfiltered dataframe here
                x="Percentage",
                y="Also Found",
                color="Primary",
                barmode="group",
                orientation="h",
                labels={"Percentage": "Co-occurrence %", "Also Found": "Co-occurring Substance", "Primary": "Primary Substance"},
            )
            apply_standard_bar_layout(cooccur_bar)
        else:
            cooccur_bar = px.bar()
    
    # Summary tables
    def summary_table(group_col, categories=None):
        return build_summary_count_table(
            df,
            group_col=group_col,
            id_col="record_id",
            categories=categories,
            include_statewide_county=(group_col == "county" and include_statewide_county_outputs),
            count_label="Records",
        )
    
    dose_age_groups = sort_opts(df["age_group"]) if "age_group" in df.columns and not df.empty else None
    
    return (
        kpi_display,
        substance_bar,
        year_line,
        county_line,
        sunburst_fig,
        cooccur_bar,
        summary_table("county", county_opts),
        summary_table("age_group", dose_age_groups),
        summary_table("sex", sex_opts),
        summary_table("race_ethnicity", race_ethnicity_opts),
        summary_table("hawaii_residency", residency_opts),
    )
