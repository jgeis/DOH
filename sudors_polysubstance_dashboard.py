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
   make_filters_card,
   dropdown_filter,
   format_count_display,
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

   # Make the year column numeric when possible so graphs treat it as numbers
   if "year" in df.columns:
       df["year"] = pd.to_numeric(df["year"], errors="coerce")

   # For these columns, replace missing values with "Unknown"
   # so we don't get blank labels in filters and tables.
   for col in ["substance", "homeless", "sex", "age_cat", "race_ethnicity", "year"]:
       if col in df.columns:
           df[col] = df[col].fillna("Unknown")
   return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_sudors_dataframe_from_db()

# Total unique incidents for the static KPI card.
total_unique = df_raw["incident_id"].nunique() if "incident_id" in df_raw.columns else 0

# Build the lists of choices for each filter only if the column exists.
substance_opts  = sort_opts(df_raw["substance"])                     if "substance"         in df_raw.columns else []
homeless_opts   = sort_opts(df_raw["homeless"])                      if "homeless"          in df_raw.columns else []
sex_opts        = sort_opts(df_raw["sex"])                           if "sex"               in df_raw.columns else []
age_opts        = sort_opts(df_raw["age_cat"])                       if "age_cat"           in df_raw.columns else []
race_opts       = sort_opts(df_raw["race_ethnicity"])                if "race_ethnicity"    in df_raw.columns else []
year_opts       = sorted(df_raw["year"].dropna().unique().tolist())  if "year"              in df_raw.columns else []


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
sudors_cooccurrence_sidebar_text = SECTION_TEXTS.get("sudors_polysubstance", [])

def layout():
   """
   Build the discharges dashboard layout.
   """
   # Adjust plot heights for desktop
   bar_h  = "360px"

   # Left column: KPI, reset button, and filters.
   left_col = make_left_sidebar(
       kpi_card,
       reset_filters_button,
       filters_card,
       helper_text=sudors_cooccurrence_sidebar_text,
       xs=12,
       md=3,
   )

   # Center column: the main line, bar, and pie charts.
   center_col = dbc.Col(
       [
           graph_block("sudors-cooccurrence-bar", "Deaths by Co-occurring Substances", bar_h),
           html.P("Bar chart showing deaths by cooccurring substances.", className="visually-hidden"),

           # Sunburst Chart
           dbc.Row([
               dbc.Col([
                   dbc.Card([
                       dbc.CardHeader([
                           html.H5("Co-occurrence Sunburst", className="mb-0")
                       ]),
                       dbc.CardBody([
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
       xs=12, md=6
   )

   # Center alt column: the main line and bar charts.
   center_alt_col = dbc.Col([
       # Cooccurrence Chart
       dbc.Row([
           dbc.Col([
               dbc.Card([
                   dbc.CardHeader([
                       html.H5("Co-occurrence by Primary Substance", className="mb-0")
                   ]),
                   dbc.CardBody([
                       html.P([
                           "Grouped bar chart showing what percentage of cases with a given primary substance also contain each other substance. ",
                           "Use the filter in the left panel to focus on one substance.",
                       ], className="text-muted mb-3"),
                       dcc.Loading(
                           html.Div(
                               html.Div(
                                   dcc.Graph(
                                       id="sudors-alt-cooccurrence-bar-chart",
                                       config={"displayModeBar": True, "displaylogo": False},
                                       style={"height": "500px"}
                                   ),
                               ),
                           )
                       ),
                       html.P(
                           "Grouped bar chart showing the percentage of cases where each primary substance co-occurs with other substances.",
                           className="visually-hidden",
                       ),
                   ])
               ])
           ])
       ]),
   ], xs=12, md=12, className="mb-4")

   # Right column: summary tables
   right_col = dbc.Col([
       dbc.Row([
           dbc.Col([
               html.Div(
                   id="sudors-cooccurrence-table-race",
                   className="mobile-side-table",
                   style={"overflowX": "auto"}
               )], xs=12, md=12, className="pe-1 mb-3"),
           dbc.Col([
               html.Div(
                   id="sudors-cooccurrence-table-year",
                   className="mobile-side-table",
                   style={"overflowX": "auto"}
               )], xs=12, md=12, className="ps-1 mb-3"),
           dbc.Col([
               html.Div(
                   id="sudors-cooccurrence-table-age",
                   className="mobile-side-table",
                   style={"overflowX": "auto"}
               )], xs=12, md=12, className="ps-1 mb-3"),
       ], className="g-2"),
   ], xs=12, md=3)

   return dbc.Container([
       skip_link,
       html.Div(
           dbc.Row([left_col, center_col, right_col], className="g-3"),
           id="sudors-cooccurrence-section",
       ),
       html.Div(
           dbc.Row([center_alt_col], className="g-3"),
           id="sudors-alt-cooccurrence-section",
       ),
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

   # Start from the full dataset each time.
   dff = df_raw.copy()

   # Only apply filters for columns that actually exist.
   if "substance" in dff.columns:      dff = apply_filter(dff, "substance", substance)
   if "homeless" in dff.columns:       dff = apply_filter(dff, "homeless", homeless)
   if "sex" in dff.columns:            dff = apply_filter(dff, "sex", sex)
   if "age_cat" in dff.columns:        dff = apply_filter(dff, "age_cat", age)
   if "race_ethnicity" in dff.columns: dff = apply_filter(dff, "race_ethnicity", race)
   if "year" in dff.columns:           dff = apply_filter(dff, "year", year)

   # Count unique discharges (each record_id represents one discharge).
   # Used to update the total on the KPI card when user selects the filter
   filter_total = dff["incident_id"].nunique()


   # ---------- Bar chart: Deaths by Substance ----------
   if {"substance"}.issubset(dff.columns):
       by_sub = (
           dff.groupby("substance")["incident_id"].nunique()
           .reset_index(name="count")
           .sort_values("count", ascending=True)
       )

       # Show all rows, but suppress low-count bars by plotting zero width.
       by_sub["plot_count"] = by_sub["count"].apply(lambda x: 0 if x < 10 else x)

       def ellipsize(text, max_len=25):
           if text is None:
               return text
           return text if len(text) <= max_len else text[:max_len] + "..."

       # Cuts off label length after 25 characters
       by_sub["substance_label"] = by_sub["substance"].apply(ellipsize)
       by_sub["display_count"] = by_sub["count"].apply(format_count_display)

       sud_bar = px.bar(
           by_sub,
           x="plot_count",
           y="substance_label",
           barmode="stack",
           text="display_count",
           labels={"plot_count": "Number of Deaths", "substance_label": "Cause of Death<br>(Not Mutually Exclusive)"},
       )

       sud_bar.update_traces(
           marker_color="#22767C",
           textposition="outside",
           cliponaxis=False,
           hovertemplate="Cause of Death: %{customdata}<br>Number of Deaths: %{text}<extra></extra>",
           customdata=by_sub["substance"],
       )

       sud_bar.update_layout(
           margin=dict(l=0, r=0, t=10, b=80),
           xaxis=dict(automargin=True, rangemode="tozero"),
       )
   else:
       sud_bar = px.bar()


   # ---------- Helper for the summary tables ----------
   def tbl(column, categories=None):
       """Build a small table for the summary."""
       if column not in dff.columns:
           return dbc.Alert(
               f"Column '{column}' not found.",
               color="warning",
               className="mb-0"
           )

       # Count unique discharges per category
       g = dff.groupby(column)["incident_id"].nunique().reset_index(name="count")

       # Use the given category order if provided
       if categories:
           g[column] = pd.Categorical(g[column], categories=categories, ordered=True)
           g = g.sort_values(column)
       elif column == "race_ethnicity":
           g = g.sort_values("count", ascending=False)
       elif column == "homeless":
           g = g.sort_values("count", ascending=False)

       # Make the counts look nicer with commas
       g["count"] = g["count"].map(format_count_display)

       # Use friendly display labels for table headers
       header_labels = {
           "race_ethnicity": "Race/Ethnicity",
           "homeless": "Is Homeless",
           "year": "Calendar Year",
           "age_cat": "Age Group",
       }
       display_column = header_labels.get(column, column)
       g = g.rename(columns={column: display_column, "count": "Deaths"})

       # Build a styled table for the dashboard
       return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)

   # pin "under 15" at the top and "unknown" at the bottom, with the rest in numeric order in between
   def age_sort_key(label):
       text = str(label).strip()
       lower = text.lower()

       if lower == "under 15":
           return (0, -1, text)
       if lower == "unknown":
           return (2, float("inf"), text)

       match = re.search(r"\d+", text)
       if match:
           return (1, int(match.group()), text)

       return (1, float("inf"), text)

   age_table_order = []
   if "age_cat" in dff.columns:
       age_table_order = sorted(
           [v for v in dff["age_cat"].dropna().astype(str).unique()],
           key=age_sort_key,
       )

   # Return all the updated visuals and tables to Dash
   return (
       format_count_display(filter_total),
       sud_bar,
       tbl("race_ethnicity"),
       tbl("year"),
       tbl("age_cat", age_table_order),
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

    # Start from the full dataset each time.
    dff = df_raw.copy()

    # Only apply filters for columns that actually exist.
    if "substance" in dff.columns:      dff = apply_filter(dff, "substance", substance)
    if "homeless" in dff.columns:       dff = apply_filter(dff, "homeless", homeless)
    if "sex" in dff.columns:            dff = apply_filter(dff, "sex", sex)
    if "age_cat" in dff.columns:        dff = apply_filter(dff, "age_cat", age)
    if "race_ethnicity" in dff.columns: dff = apply_filter(dff, "race_ethnicity", race)
    if "year" in dff.columns:           dff = apply_filter(dff, "year", year)

    if dff.empty:
        empty_fig = go.Figure().add_annotation(text="No data matching filters", showarrow=False)
        # return both the bar and sunburst figures
        return empty_fig, empty_fig
    
    co_data = build_cooccurrence_data(dff)

    # --- Bar Chart ---
    if co_data.empty:
        bar_fig = go.Figure().add_annotation(text="No co-occurrence data", showarrow=False)
    else:
        co_data['Count_formatted'] = co_data['Count'].apply(format_count_display)
        co_data['Total_formatted'] = co_data['Total'].apply(format_count_display)

        bar_fig = px.bar(
            co_data,
            x='Primary',
            y='Percentage',
            color='Also Found',
            barmode='group',
            title='Co-occurrence patterns: When [Primary] is present, % with other substances',
            labels={'Percentage': 'Co-occurrence', 'Primary': 'Primary Substance'},
            text=co_data['Percentage'].apply(lambda x: f'{x:.1f}%'),
            custom_data=['Count_formatted', 'Total_formatted', 'Also Found']
        )
        bar_fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{customdata[2]}</b><br>' +
                        'Primary: %{x}<br>' +
                        'Co-occurrence: %{y:.1f}%<br>' +
                        'Count: %{customdata[0]}<br>' +
                        'Total: %{customdata[1]}<extra></extra>',
        )
        
    sunburst_data = build_sunburst_cooccurrence_data(dff)

    # --- Sunburst Chart ---
    if sunburst_data.empty:
        sun_fig = go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
    else:
        sunburst_counts = sunburst_data.value_counts().reset_index(name='Count')

        sun_fig = px.sunburst(
            sunburst_counts,
            path=["Primary", "Also Found"],
            values="Count",
        )

    return bar_fig, sun_fig
