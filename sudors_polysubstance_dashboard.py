# sudors_polysubstance_dashboard.py — Alternative visualizations for substance co-occurrence patterns


import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from theme import register_template
from db_utils import execute_query
import re
from dashboard_utils import (
   load_sql_query,
   sort_opts,
   opts_list,
   graph_block,
   make_kpi_card,
   make_left_sidebar,
    compute_last_updated_value,
    make_right_summary_tables_col,
    compute_adaptive_horizontal_bar_height,
   make_filters_card,
   dropdown_filter,
   format_count_display,
    build_suppressed_percentage_columns,
    format_display_list,
    wrap_axis_label,
    apply_standard_bar_layout,
    apply_standard_single_series_bar_trace,
    apply_standard_non_axis_layout,
    build_summary_count_table,
)

register_template()

# ----------------------------
# Data helpers
# ----------------------------

def load_sudors_dataframe_from_db():
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
   sql = load_sql_query("load_sudors_polysubstance_data")
  
   # Execute query using db_utils (automatically uses correct database)
   df = execute_query(sql)
   print(f"load_sudors_polysubstance_data returned {len(df):,} rows")

    # If there is no data, we stop early instead of showing a broken page
   if df.empty:
       raise RuntimeError("Query returned 0 rows.")

   # Make the year column numeric for sorting, then string for filtering
   if "year" in df.columns:
       df["year"] = pd.to_numeric(df["year"], errors="coerce")
       # Now convert to string for filtering and UI consistency
       df["year"] = df["year"].fillna("Unknown").astype(int).astype(str)

   # For these columns, replace missing values with "Unknown"
   # so we don't get blank labels in filters and tables.
   for col in ["substance", "homeless", "sex", "age_cat", "race_ethnicity", "year"]:
       if col in df.columns:
           df[col] = df[col].fillna("Unknown")
   return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_sudors_dataframe_from_db()
last_updated_value = compute_last_updated_value(df_raw)

# Total unique incidents for the static KPI card.
total_unique = df_raw["incident_id"].nunique() if "incident_id" in df_raw.columns else 0

# Build the lists of choices for each filter only if the column exists.
substance_opts  = sort_opts(df_raw["substance"])                     if "substance"         in df_raw.columns else []
homeless_opts   = sort_opts(df_raw["homeless"])                      if "homeless"          in df_raw.columns else []
sex_opts        = sort_opts(df_raw["sex"])                           if "sex"               in df_raw.columns else []
age_opts        = sort_opts(df_raw["age_cat"])                       if "age_cat"           in df_raw.columns else []
race_opts       = sort_opts(df_raw["race_ethnicity"])                if "race_ethnicity"    in df_raw.columns else []
year_opts       = sort_opts(df_raw["year"])                          if "year"              in df_raw.columns else []


# ----------------------------
# Helper Functions
# ----------------------------

def build_cooccurrence_matrix(df):
   """
   Build a co-occurrence matrix showing how often substances appear together.
  
   Returns a DataFrame where rows and columns are substances, and values are
   the count of records where both substances appear together.
   """
   # Create a pivot table: rows=record_id, columns=substance, values=1 if present
   substance_matrix = df.pivot_table(
       index='incident_id',
       columns='substance',
       aggfunc='size',
       fill_value=0
   ).clip(upper=1)  # Convert to binary (0 or 1)
  
   # Calculate co-occurrence: matrix multiplication
   cooccurrence = substance_matrix.T.dot(substance_matrix)
  
   return cooccurrence

def build_correlation_matrix(df):
   """
   Build a correlation matrix showing the correlation between substance occurrences.
   """
   substance_matrix = df.pivot_table(
       index='incident_id',
       columns='substance',
       aggfunc='size',
       fill_value=0
   ).clip(upper=1)
  
   return substance_matrix.corr()

def build_cooccurrence_data(df):
   """
   Build data for grouped bar chart showing co-occurrence percentages.

   For each substance, calculate what % of records also have other substances.
   """
   results = []
  
   for primary_substance in df['substance'].unique():
       # Get all records with this primary substance
       records = df[df['substance'] == primary_substance]['incident_id'].unique()
       total = len(records)
      
       if total == 0:
           continue
      
       # For each other substance, count how many of these records also have it
       for other_substance in df['substance'].unique():
           if other_substance != primary_substance:
               count = df[
                   (df['incident_id'].isin(records)) &
                   (df['substance'] == other_substance)
               ]['incident_id'].nunique()
              
               results.append({
                   'Primary': primary_substance,
                   'Also Found': other_substance,
                   'Percentage': (count / total) * 100,
                   'Count': count,
                   'Total': total
               })
  
   return pd.DataFrame(results)

def build_sunburst_cooccurrence_data(df):
   results = []

   grouped = df.groupby("incident_id")["substance"].unique()

   for substances in grouped:
       for i in range(len(substances)):
           for j in range(len(substances)):
               if i != j:
                   results.append({
                       'Primary': substances[i],
                       'Also Found': substances[j]
                   })

   return pd.DataFrame(results)


def _records_matching_all_selected_substances(frame: pd.DataFrame, selected_values) -> pd.DataFrame:
   """Return rows from incidents that contain ALL selected substances."""
   if not selected_values:
       return frame.copy()

   if not {"incident_id", "substance"}.issubset(frame.columns):
       return frame.iloc[0:0].copy()

   selected = [str(v).strip() for v in selected_values if str(v).strip()]
   if not selected:
       return frame.copy()

   selected_set = set(selected)
   hits = (
       frame[frame["substance"].astype(str).isin(selected_set)][["incident_id", "substance"]]
       .drop_duplicates()
   )
   required_count = len(selected_set)
   incident_match_counts = hits.groupby("incident_id")["substance"].nunique()
   matched_ids = incident_match_counts[incident_match_counts == required_count].index
   return frame[frame["incident_id"].isin(matched_ids)].copy()


# ----------------------------
# UI Components
# ----------------------------

# This link helps keyboard and screen reader users jump straight to the filters.
skip_link = html.A(
  "Skip to filters",
  href="#sudors-cooccurrence-filters",
  className="visually-hidden-focusable",
  tabIndex=0
)

reset_filters_button = dbc.Button(
   "Reset All Filters",
   id="sudors-cooccurrence-reset-filters-btn",
   color="secondary",
   outline=True,
   className="w-100 mb-3",
   n_clicks=0,
)

# Big green card that shows the total number of deaths.
kpi_card = make_kpi_card(
   label="Number of Unintentional or Undetermined Overdose Deaths (Polysubstance)",
   count_id="sudors-cooccurrence-kpi-total",
)

# Card holding all the filter controls down the left side.
# Filter display order is managed centrally in dashboard_utils.make_filters_card.
filters_card = make_filters_card(
   card_id="sudors-cooccurrence-filters",
   title="Filter Data",
   filters=[
       dropdown_filter("Substance", "sudors-cooccurrence-substance-filter", options=opts_list(substance_opts), multi=True, placeholder="All"),
       dropdown_filter("Homeless", "sudors-cooccurrence-homeless-filter", options=opts_list(homeless_opts), multi=True, placeholder="All"),
       dropdown_filter("Race/Ethnicity", "sudors-cooccurrence-race-filter", options=opts_list(race_opts), multi=True, placeholder="All"),
       dropdown_filter("Sex", "sudors-cooccurrence-sex-filter", options=opts_list(sex_opts), multi=True, placeholder="All"),
       dropdown_filter("Age Group", "sudors-cooccurrence-age-filter", options=opts_list(age_opts), multi=True, placeholder="All"),
       dropdown_filter("Calendar Year", "sudors-cooccurrence-year-filter", options=opts_list(year_opts), multi=True, placeholder="All"),
   ],
)

from section_texts import SECTION_TEXTS
sudors_cooccurrence_sidebar_text = SECTION_TEXTS.get("sudors-polysubstance", [])

def layout():
    """
    Build the discharges dashboard layout.
    """
    # Adjust plot heights for desktop
    bar_h = f"{compute_adaptive_horizontal_bar_height(len(substance_opts))}px"

# Left column: updated for nested md=4
    left_col = make_left_sidebar(
        kpi_card,
        reset_filters_button,
        filters_card,
        helper_text=sudors_cooccurrence_sidebar_text,
        last_updated_value=last_updated_value,
        xs=12,
        md=4, # CHANGED from 3 to 4
    )

    # Center column: updated for nested md=8
    center_col = dbc.Col(
        [
            graph_block("sudors-cooccurrence-bar", "Deaths by Co-occurring Substances"),
            html.P("Bar chart showing deaths by cooccurring substances.", className="visually-hidden"),

            # Sunburst Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Co-occurrence Sunburst", className="mb-0")
                        ]),
                        dbc.CardBody([
                            # ... (Keep your existing CardBody contents unchanged) ...
                            html.P([
                                "Sunburst chart showing how selected substances branch into co-occurring substance combinations.",
                                "Use the filter in the left panel to focus on one substance.",
                            ], className="text-muted mb-3"),
                            dcc.Loading(
                                html.Div(
                                    html.Div(
                                        dcc.Graph(
                                            id="sudors-alt-cooccurrence-sunburst",
                                            config={"displayModeBar": True, "displaylogo": False},
                                            style={"height": "500px"}
                                        ),
                                    ),
                                )
                            ),
                            html.P(
                                "Sunburst chart showing how selected substances branch into co-occurring substance combinations.",
                                className="visually-hidden",
                            ),
                        ])
                    ])
                ], md=12, className="mb-4")
            ])
        ],
        xs=12, md=8 # CHANGED from 6 to 8
    )

    # Center alt column: updated to take full width (md=12) of the nested wrapper
    center_alt_col = dbc.Col([
        # Cooccurrence Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Co-occurrence with selected substance", className="mb-0")
                    ]),
                    dbc.CardBody([
                        # ... (Keep your existing CardBody contents unchanged) ...
                        html.P([
                            "Grouped bar chart showing what percentage of cases with a given substance also contain each other substance. ",
                            "Use the filter in the left panel to focus on one substance.",
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            html.Div(
                                html.Div(
                                    dcc.Graph(
                                        id="sudors-alt-cooccurrence-bar-chart",
                                        config={"displayModeBar": True, "displaylogo": False},
                                        style={"height": bar_h}
                                    ),
                                ),
                            )
                        ),
                        html.P(
                            "Grouped bar chart showing the percentage of cases where the selected substance co-occurs with other substances.",
                            className="visually-hidden",
                        ),
                    ])
                ])
            ])
        ])
    ], xs=12, md=12, className="mb-4") # CHANGED from 9 to 12

    # Right column: Remains exactly the same (md=3)
    right_col = make_right_summary_tables_col(
        [
            ("Race/Ethnicity", "sudors-cooccurrence-table-race"),
            ("Sex at Birth", "sudors-cooccurrence-table-sex"),
            ("Homeless", "sudors-cooccurrence-table-homeless"),
            ("Calendar Year", "sudors-cooccurrence-table-year"),
            ("Age Group", "sudors-cooccurrence-table-age"),
        ],
        xs=12,
        md=3,
    )

    # RESTRUCTURED RETURN BLOCK
    return dbc.Container([
        skip_link,
        html.Div([
            dbc.Row([
                
                # 1. THE LEFT WRAPPER (Takes up 9 columns on the main grid)
                dbc.Col([
                    # Top inner row (Left and Center)
                    dbc.Row([left_col, center_col], className="g-3"),
                    
                    # Bottom inner row (Center Alt Chart)
                    dbc.Row([center_alt_col], className="g-3 mt-0")
                ], xs=12, md=9),

                # 2. THE RIGHT WRAPPER (Takes up 3 columns on the main grid)
                right_col
                
            ], className="g-3"),
        ], id="sudors-cooccurrence-section"),
    ], fluid=True, className="p-2")

# This is the default layout used when the app imports this file.
layout = layout()


# ----------------------------
# Callbacks
# ----------------------------

@callback(
   # filters
   Output("sudors-cooccurrence-substance-filter", "value"),
   Output("sudors-cooccurrence-homeless-filter", "value"),
   Output("sudors-cooccurrence-race-filter", "value"),
   Output("sudors-cooccurrence-sex-filter", "value"),
   Output("sudors-cooccurrence-age-filter", "value"),
   Output("sudors-cooccurrence-year-filter", "value"),
   Input("sudors-cooccurrence-reset-filters-btn", "n_clicks"),
   prevent_initial_call=True,
)

def reset_cooccurrence_filters(_n_clicks):
   # Reset all multi-select dropdowns to their default empty state.
   return None, None, None, None, None, None

@callback(
   # kpi card
   Output("sudors-cooccurrence-kpi-total", "children"),
   # graphs
   Output("sudors-cooccurrence-bar", "figure"),
    # tables
    Output("sudors-cooccurrence-table-race", "children"),
    Output("sudors-cooccurrence-table-sex", "children"),
    Output("sudors-cooccurrence-table-homeless", "children"),
    Output("sudors-cooccurrence-table-year", "children"),
    Output("sudors-cooccurrence-table-age", "children"),
   # filters
   Input("sudors-cooccurrence-substance-filter", "value"),
   Input("sudors-cooccurrence-homeless-filter", "value"),
   Input("sudors-cooccurrence-sex-filter", "value"),
   Input("sudors-cooccurrence-age-filter", "value"),
   Input("sudors-cooccurrence-race-filter", "value"),
   Input("sudors-cooccurrence-year-filter", "value"),
)

def update_dashboard(substance, homeless, sex, age, race, year):
   """
   This function runs every time the user changes a filter.
   It updates all the discharge visualizations and tables.
   """

   def apply_filter(frame, col, val):
       """
       Small helper so we don't repeat the same filter logic.

       If the user did not pick anything, we leave the data alone.
       If they picked one or more values, we only keep matching rows.
       """
       if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
           return frame
       if isinstance(val, (list, tuple)):
           return frame[frame[col].isin(val)]
       return frame[frame[col] == val]


   selected_values = (
       [v for v in substance if v]
       if isinstance(substance, (list, tuple, set))
       else ([substance] if substance else [])
   )

   # Start from the full dataset each time.
   dff_base = df_raw.copy()

   # Apply non-substance filters first.
   if "homeless" in dff_base.columns:       dff_base = apply_filter(dff_base, "homeless", homeless)
   if "sex" in dff_base.columns:            dff_base = apply_filter(dff_base, "sex", sex)
   if "age_cat" in dff_base.columns:        dff_base = apply_filter(dff_base, "age_cat", age)
   if "race_ethnicity" in dff_base.columns: dff_base = apply_filter(dff_base, "race_ethnicity", race)
   if "year" in dff_base.columns:           dff_base = apply_filter(dff_base, "year", year)

   dff = dff_base.copy()
   if selected_values and {"incident_id", "substance"}.issubset(dff_base.columns):
       dff = _records_matching_all_selected_substances(dff_base, selected_values)

   # Count unique discharges (each record_id represents one discharge).
   # Used to update the total on the KPI card when user selects the filter
   filter_total = dff["incident_id"].nunique()

   # Always use the full set of age categories from df_raw for summary tables
   age_table_order = []
   if "age_cat" in df_raw.columns:
       age_table_order = sort_opts(df_raw["age_cat"])

   # Build all summary tables once for reuse
   table_race = build_summary_count_table(
       dff,
       "race_ethnicity",
       id_col="incident_id",
       categories=race_opts if not race else None,
       include_all_ordered=not bool(race),
       count_label="Deaths",
   )
   table_sex = build_summary_count_table(
       dff,
       "sex",
       id_col="incident_id",
       categories=sex_opts if not sex else None,
       include_all_ordered=not bool(sex),
       count_label="Deaths",
   )
   table_homeless = build_summary_count_table(
       dff,
       "homeless",
       id_col="incident_id",
       categories=homeless_opts if not homeless else None,
       include_all_ordered=not bool(homeless),
       count_label="Deaths",
   )
   table_year = build_summary_count_table(
       dff,
       "year",
       id_col="incident_id",
       categories=year_opts if not year else None,
       include_all_ordered=not bool(year),
       count_label="Deaths",
   )
   table_age = build_summary_count_table(
       dff,
       "age_cat",
       id_col="incident_id",
       categories=age_table_order if not age else None,
       include_all_ordered=not bool(age),
       count_label="Deaths",
   )

   # ---------- Bar chart: Deaths by Substance ----------
   if {"substance"}.issubset(dff.columns):
       bar_source = dff.copy()
       if selected_values:
           selected_set = {str(v) for v in selected_values}
           bar_source = bar_source[~bar_source["substance"].astype(str).isin(selected_set)]

       by_sub = (
           bar_source.groupby("substance")["incident_id"].nunique()
           .reset_index(name="count")
           .sort_values("count", ascending=True)
       )

       if by_sub.empty:
           sud_bar = go.Figure().add_annotation(
               text="No additional co-substances found with selected substance(s)",
               showarrow=False,
           )
           return (
               format_count_display(filter_total),
               sud_bar,
               table_race,
               table_year,
               table_age,
               table_sex,
               table_homeless,
           )

       def ellipsize(text, max_len=25):
           if text is None:
               return text
           return text if len(text) <= max_len else text[:max_len] + "..."

       # Cuts off label length after 25 characters
       by_sub["substance_label"] = by_sub["substance"].apply(ellipsize)
       by_sub["display_count"] = by_sub["count"].apply(format_count_display)

       sud_bar = px.bar(
           by_sub,
          x="count",
           y="substance_label",
           barmode="stack",
           text="display_count",
          labels={"count": "Number of Deaths", "substance_label": "Cause of Death<br>(Not Mutually Exclusive)"},
       )

       apply_standard_single_series_bar_trace(sud_bar)
       sud_bar.update_traces(hovertemplate="%{y}: %{text}<extra></extra>")

       apply_standard_bar_layout(sud_bar, xaxis=dict(rangemode="tozero"))
   else:
       sud_bar = px.bar()

   # Return all the updated visuals and tables to Dash
   return (
       format_count_display(filter_total),
       sud_bar,
       table_race,
       table_sex,
       table_homeless,
       table_year,
       table_age,
   )

@callback(
    Output("sudors-alt-cooccurrence-bar-chart", "figure"),
    Output("sudors-alt-cooccurrence-sunburst", "figure"),
    # filters
    Input("sudors-cooccurrence-substance-filter", "value"),
    Input("sudors-cooccurrence-homeless-filter", "value"),
    Input("sudors-cooccurrence-sex-filter", "value"),
    Input("sudors-cooccurrence-age-filter", "value"),
    Input("sudors-cooccurrence-race-filter", "value"),
    Input("sudors-cooccurrence-year-filter", "value"),
)

def update_alternative_charts(substance, homeless, sex, age, race, year):

    def apply_filter(frame, col, val):
        """
        Small helper so we don't repeat the same filter logic.

        If the user did not pick anything, we leave the data alone.
        If they picked one or more values, we only keep matching rows.
        """
        if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
            return frame
        if isinstance(val, (list, tuple)):
            return frame[frame[col].isin(val)]
        return frame[frame[col] == val]

    selected_values = (
        [v for v in substance if v]
        if isinstance(substance, (list, tuple, set))
        else ([substance] if substance else [])
    )

    # Start from the full dataset each time.
    dff = df_raw.copy()

    # Apply non-substance filters first.
    if "homeless" in dff.columns:       dff = apply_filter(dff, "homeless", homeless)
    if "sex" in dff.columns:            dff = apply_filter(dff, "sex", sex)
    if "age_cat" in dff.columns:        dff = apply_filter(dff, "age_cat", age)
    if "race_ethnicity" in dff.columns: dff = apply_filter(dff, "race_ethnicity", race)
    if "year" in dff.columns:           dff = apply_filter(dff, "year", year)

    if selected_values and {"incident_id", "substance"}.issubset(dff.columns):
        dff = _records_matching_all_selected_substances(dff, selected_values)

    if dff.empty:
        empty_fig = go.Figure().add_annotation(text="No data matching filters", showarrow=False)
        # return both the bar and sunburst figures
        return empty_fig, empty_fig
    
    # --- Bar Chart ---
    if selected_values:
        selected_set = {str(v) for v in selected_values}
        total_records = dff["incident_id"].nunique()
        co_data = (
            dff.groupby("substance")["incident_id"]
            .nunique()
            .reset_index(name="Count")
        )
        co_data = co_data[~co_data["substance"].astype(str).isin(selected_set)]

        if co_data.empty:
            bar_fig = go.Figure().add_annotation(
                text="No additional co-substances found with selected substance(s)",
                showarrow=False,
            )
        else:
            co_data = co_data.rename(columns={"substance": "Also Found"})
            co_data["Total"] = total_records
            co_data["Percentage"] = (co_data["Count"] / total_records) * 100
            co_data = co_data.sort_values("Percentage", ascending=False)
            co_data["Count_formatted"] = co_data["Count"].apply(format_count_display)
            co_data["Total_formatted"] = co_data["Total"].apply(format_count_display)
            co_data["Plot_Percentage"], co_data["Percentage_display"], _ = build_suppressed_percentage_columns(
                co_data["Percentage"],
                count_display_values=co_data["Count_formatted"],
                decimals=1,
            )
            co_data["Cooccurrence_line"] = co_data["Percentage_display"].apply(
                lambda pct: (
                    f"Co-occurrence: {pct}"
                    if pd.notna(pct) and str(pct).strip()
                    else "Co-occurrence: Suppressed"
                )
            )
            co_data["label"] = co_data.apply(
                lambda row: (
                    f"{row['Percentage_display']} (n={row['Count_formatted']})"
                    if pd.notna(row["Percentage_display"]) and str(row["Percentage_display"]).strip()
                    else row["Count_formatted"]
                ),
                axis=1,
            )

            bar_fig = px.bar(
                co_data,
                x="Plot_Percentage",
                y="Also Found",
                orientation="h",
                labels={"Percentage": "Co-occurrence", "Also Found": "Other Substance"},
                text="label",
                custom_data=["Count_formatted", "Total_formatted", "Cooccurrence_line"],
            )
            apply_standard_single_series_bar_trace(
                bar_fig,
                cliponaxis=True,
                hovertemplate="<b>%{y}</b><br>"
                             "%{customdata[2]}<br>"
                             "Count: %{customdata[0]}<br>"
                             "Total: %{customdata[1]}<extra></extra>",
            )
            max_pct = float(co_data["Plot_Percentage"].max()) if not co_data.empty else 0.0
            bar_fig.update_xaxes(range=[0, max_pct * 1.15 if max_pct else 1])
            bar_fig.update_yaxes(
                categoryorder="array",
                categoryarray=co_data["Also Found"].tolist()[::-1],
            )
            apply_standard_bar_layout(bar_fig)

    else:
        co_data = build_cooccurrence_data(dff)
        if co_data.empty:
            bar_fig = go.Figure().add_annotation(text="No co-occurrence data", showarrow=False)
        else:
            co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
            co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)
            co_data['Plot_Percentage'], co_data['Percentage_display'], _ = build_suppressed_percentage_columns(
                co_data['Percentage'],
                count_display_values=co_data['Count_formatted'],
                decimals=1,
            )
            co_data['Cooccurrence_line'] = co_data['Percentage_display'].apply(
                lambda pct: (
                    f"Co-occurrence: {pct}"
                    if pd.notna(pct) and str(pct).strip()
                    else "Co-occurrence: Suppressed"
                )
            )

            bar_fig = px.bar(
                co_data,
                x='Primary',
                y='Plot_Percentage',
                color='Also Found',
                barmode='group',
                labels={'Percentage': 'Co-occurrence', 'Primary': 'Primary Substance'},
                text=co_data['Percentage_display'],
                custom_data=['Count_formatted', 'Total_formatted', 'Cooccurrence_line', 'Also Found']
            )
            bar_fig.update_traces(
                textposition='inside',
                hovertemplate='<b>%{customdata[3]}</b><br>' +
                            'Primary: %{x}<br>' +
                            '%{customdata[2]}<br>' +
                            'Count: %{customdata[0]}<br>' +
                            'Total: %{customdata[1]}<extra></extra>',
            )
            bar_fig.update_layout(legend=dict(orientation="v", x=1.02, y=1, xanchor="left", yanchor="top"))
            apply_standard_bar_layout(bar_fig)
        
    # --- Sunburst Chart ---
    if selected_values:
        selected_label = selected_values[0] if len(selected_values) == 1 else format_display_list(selected_values)
        selected_label_wrapped = wrap_axis_label(selected_label, max_len=28)
        selected_set = {str(v) for v in selected_values}

        cohort_records = dff.drop_duplicates(subset=["incident_id", "substance"])
        outer_counts = (
            cohort_records.groupby("substance")["incident_id"]
            .nunique()
            .sort_values(ascending=False)
        )
        outer_counts = outer_counts[~outer_counts.index.astype(str).isin(selected_set)]

        if outer_counts.empty:
            sun_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
        else:
            root_value = float(outer_counts.sum())
            ids = ["root"]
            labels = [selected_label_wrapped]
            parents = [""]
            values = [root_value]
            customdata = [[int(dff["incident_id"].nunique()), selected_label, selected_label]]

            min_label_share = 0.04

            def compact_label(value: str, max_chars: int = 12) -> str:
                text = str(value).strip()
                if len(text) <= max_chars:
                    return text
                return text[: max_chars - 3].rstrip() + "..."

            for sub_name, raw_count in outer_counts.items():
                ids.append(f"sub::{sub_name}")
                scaled_value = float(raw_count)
                show_label = (scaled_value / root_value) >= min_label_share if root_value else False
                label_text = sub_name if show_label else compact_label(sub_name)
                labels.append(wrap_axis_label(label_text, max_len=20))
                parents.append("root")
                values.append(scaled_value)
                customdata.append([int(raw_count), selected_label, str(sub_name)])

            sun_fig = go.Figure(go.Sunburst(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                customdata=customdata,
                branchvalues="total",
                insidetextorientation="horizontal",
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    "Raw Count: %{customdata[0]:,}<br>"
                    "Cohort: %{customdata[1]}<extra></extra>"
                ),
            ))
            apply_standard_non_axis_layout(sun_fig)
            sun_fig.update_layout(uniformtext_minsize=8, uniformtext_mode="show")
    else:
        sunburst_data = build_sunburst_cooccurrence_data(dff)
        if sunburst_data.empty:
            sun_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
        else:
            sunburst_counts = sunburst_data.value_counts().reset_index(name='Count')

            sun_fig = px.sunburst(
                sunburst_counts,
                path=["Primary", "Also Found"],
                values="Count",
            )
            apply_standard_non_axis_layout(sun_fig)
            sun_fig.update_layout(uniformtext_minsize=8, uniformtext_mode="show")

    return bar_fig, sun_fig
