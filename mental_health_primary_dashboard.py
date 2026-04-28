from db_utils import execute_query
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from theme import register_template

register_template()

# ----------------------------
# Data helpers
# ----------------------------
def load_sql_query(name, path="queries.sql"):
   """
   This helper looks inside the queries.sql file and pulls out
   the specific SQL block we want by name.

   Why: this keeps all the SQL in one file instead of hard-coding
   long queries directly in the Python file.
   """
   with open(path, "r", encoding="utf-8") as f:
       sql = f.read()
   # The SQL file is split into blocks marked with "-- name:"
   blocks = sql.split("-- name:")
   m = {}
   for b in blocks:
       # Skip any empty chunks
       if not b.strip():
           continue
       # First line after "-- name:" is the name, the rest is the SQL text
       lines = b.strip().split("\n")
       m[lines[0].strip()] = "\n".join(lines[1:]).strip()
   # If we typed the wrong query name, complain loudly
   if name not in m:
       raise KeyError(f"Named query '{name}' not found in {path}.")
   return m[name]

def load_diagnosis_dataframe_from_db():
   """
   This helper:
     1. Loads the main SQL query by name.
     2. Connects to the database and runs the query.
     3. Cleans up some columns so the rest of the app is easier to write.

   Why: having this in one place avoids repeating the same database
   logic in multiple callbacks.
  
   Note: Uses either SQLite or MSSQL automatically based on config.
   """
  
   sql = load_sql_query("load_discharge_data_view_diagnosis")
  
   # Execute query using db_utils (automatically uses correct database)
   df = execute_query(sql)
   print(f"load_discharge_data_view_diagnosis returned {len(df):,} rows")

   # If there is no data, we stop early instead of showing a broken page
   if df.empty:
       raise RuntimeError("Query returned 0 rows.")

   # Make the year column numeric when possible so graphs treat it as numbers
   if "year" in df.columns:
       df["year"] = pd.to_numeric(df["year"], errors="coerce")

   # For these columns, replace missing values with "Unknown"
   # so we don't get blank labels in filters and tables.
   for col in ["substance", "diagnosis_type", "is_primary", "county", "city", "zip", "hawaii_residency", "age_group", "sex", "race_ethnicity", "year"]:
       if col in df.columns:
           df[col] = df[col].fillna("Unknown")
   return df

# Load the full dataset once at startup.
# The callbacks will reuse this instead of hitting the database every time.
df_raw = load_diagnosis_dataframe_from_db()

# Total number of unique records, used for the big KPI card.
kpi_total = df_raw["record_id"].nunique() if "record_id" in df_raw.columns else 0

# ---------- filter options ----------
def sort_opts(series):
   """
   Turn a column into a sorted list of unique values.

   We also push "Unknown" to the end of the list so the filter menus
   look cleaner and more natural to read.
   """
   vals = pd.Series(series.unique()).astype(str)
   return sorted([v for v in vals if v != "Unknown"]) + (["Unknown"] if "Unknown" in vals.values else [])

# Build the lists of choices for each filter only if the column exists.
# Why: this makes the code more flexible if the data shape changes later.
su_opts     = sort_opts(df_raw.loc[df_raw["diagnosis_type"] == "su", "diagnosis"])      if "diagnosis"      in df_raw.columns else []
mh_opts     = sort_opts(df_raw.loc[df_raw["diagnosis_type"] == "mh", "diagnosis"])      if "diagnosis"      in df_raw.columns else []
age_opts    = sort_opts(df_raw["age_group"])                                            if "age_group"      in df_raw.columns else []
sex_opts    = sort_opts(df_raw["sex"])                                                  if "sex"            in df_raw.columns else []
county_opts = sort_opts(df_raw["county"])                                               if "county"         in df_raw.columns else []
year_opts   = sorted(df_raw["year"].dropna().unique().tolist())                         if "year"           in df_raw.columns else []

def opts_list(values):
   """
   Turn a simple list of values into the format Dash expects for
   drop-down choices (label + value).
   """
   return [{"label": v, "value": v} for v in values]


# ----------------------------
# Reusable graph block (Tools toggle + title + graph)
# ----------------------------
def graph_block(base_id: str, title_text: str, height_px: str):
   """
   Make a standard "card" that holds:
     - a hidden store that remembers if the tools are on/off
     - a small Tools button that the user clicks
     - a title for the plot
     - the actual graph area

   Why: we use this pattern for several plots, so this function keeps
   the layout consistent and avoids repeating the same code over and over.
   """
   return html.Div(
       [
           # Header row with the plot title.
           html.H5(title_text, id=f"{base_id}-title", className="plot-card-header mb-2"),


           # The actual graph. Modebar (tools) is always on now.
           dcc.Graph(
               id=base_id,
               style={"height": height_px, "width": "100%"},
               config={"displayModeBar": True, "displaylogo": False},
           ),
       ],
       className="mb-4",
       # This makes sure the tools bar is never cut off visually.
       style={"overflow": "visible"}
   )

# ----------------------------
# UI
# ----------------------------

# This link helps keyboard and screen reader users jump straight to the filters.
skip_link = html.A(
   "Skip to filters",
   href="#alt-filters",
   className="visually-hidden-focusable",
   tabIndex=0
)

# Big green card that shows the total number of discharges.
# Why: gives users a quick "at a glance" number when they open the page.
kpi_card = dbc.Card(
   dbc.CardBody([
       html.H4("Discharges related to co-occuring MH Disorder (primary) and SUD (secondary)", className="card-title text-white"),
       html.H2(id="mh-primary-kpi-total-deaths", className="text-white"),
   ]),
   className="bg-success text-center mb-4"
)

# Card holding all the filter controls down the left side.
# Each filter uses the options we built from the data above.
filters_card = dbc.Card(
   dbc.CardBody([
       html.H5("Filter Data", tabIndex=1),

       html.Label("Substance Type", htmlFor="mh-primary-su-filter", tabIndex=2, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-su-filter", options=opts_list(su_opts), multi=True,
           placeholder="Substance Type", className="mb-2",
           persistence=True, persistence_type="session"
       ),
       html.Label("Mental Health Diagnosis", htmlFor="mh-primary-mh-filter", tabIndex=2, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-mh-filter", options=opts_list(mh_opts), multi=True,
           placeholder="Mental Health Diagnosis", className="mb-2",
           persistence=True, persistence_type="session",
           optionHeight=125
       ),
       html.Label("Age Group", htmlFor="mh-primary-age-group-filter", tabIndex=6, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-age-group-filter", options=opts_list(age_opts), multi=True,
           placeholder="Age Group", className="mb-0",
           persistence=True, persistence_type="session"
       ),
       html.Label("Sex", htmlFor="mh-primary-sex-filter", tabIndex=5, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-sex-filter", options=opts_list(sex_opts), multi=True,
           placeholder="Sex", className="mb-2",
           persistence=True, persistence_type="session"
       ),
       html.Label("County", htmlFor="mh-primary-county-filter", tabIndex=5, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-county-filter", options=opts_list(county_opts), multi=True,
           placeholder="County", className="mb-2",
           persistence=True, persistence_type="session"
       ),
       html.Label("Calendar Year", htmlFor="mh-primary-year-filter", tabIndex=3, className="form-label"),
       dcc.Dropdown(
           id="mh-primary-year-filter", options=opts_list(year_opts), multi=True,
           placeholder="Calendar Year", className="mb-2",
           persistence=True, persistence_type="session"
       ),
   ]),
   id="alt-filters",
   className="mb-4"
)

def layout_for(
   is_mobile: bool = False,
   show_discharges: bool = True,
):
   """
   Build the full page layout, with slightly different heights if we
   are on a phone vs a larger screen.

   Why: on small screens we want taller plots so they are easier to read,
   but on desktops shorter plots look better side-by-side.
   """
   # Adjust plot heights depending on screen size.
   bar_h  = "55vh" if is_mobile else "360px"
   line_h = "60vh" if is_mobile else "400px"

   # Left column: KPI and filters.
   left_col = dbc.Col([kpi_card, filters_card], xs=12, md=3)

   # Center column: the main line and bar charts.
   center_col = dbc.Col(
       [
           dbc.Row([
               graph_block("mh-primary-bar-diagnosis", "Mental Health Diagnosis", bar_h),
               html.P("Bar chart of mental health diagnosis.", className="sr-only"),
           ]),
           dbc.Row([
               graph_block("mh-primary-line-discharges", "Discharges by Mental Health diagnosis and Year", line_h),
               html.P("Line chart of mental health diagnosis.", className="sr-only"),
           ]),
       ],
       xs=12, md=6
   )

   # Right column:
   # - Two small summary tables (by county and by age group)
   # - A pie chart for gender
   #
   # On phones, the two small tables sit side-by-side.
   # On bigger screens, they stack vertically.
   right_col = dbc.Col(
       [
           dbc.Row(
               [
                   dbc.Col(
                       [
                           html.Div(
                               id="mh-primary-age-group-table",
                               className="mobile-side-table",
                               style={"overflowX": "auto"}
                           ),
                       ],
                       xs=12, md=12, className="pe-1 mb-3",
                   ),
                   dbc.Col(
                       [
                           html.Div(
                               id="mh-primary-gender-table",
                               className="mobile-side-table",
                               style={"overflowX": "auto"}
                           ),
                       ],
                       xs=12, md=12, className="ps-1 mb-3",
                   ),
                   dbc.Col(
                       [
                           html.Div(
                               id="mh-primary-county-table",
                               className="mobile-side-table",
                               style={"overflowX": "auto"}
                           ),
                       ],
                       xs=12, md=12, className="ps-1 mb-3",
                   ),
               ],
               className="g-2"
           ),
       ],
       xs=12, md=3
   )
   # Wrap everything in a fluid container so it stretches with the screen.
   return dbc.Container([
       skip_link,
       html.Div(
           dbc.Row([left_col, center_col, right_col], className="g-3"),
           id="discharges-section",
           style={} if show_discharges else {"display": "none"}
       ),
       html.Hr(
           className="my-5",
           style={} if (show_discharges) else {"display": "none"}
       ),
   ], fluid=True, className="p-2")

# This is the default layout used when the app imports this file.
# We pass False here since desktop is the standard case.
layout = layout_for(is_mobile=False)

# ----------------------------
# Figures + tables (no plotly titles)
# ----------------------------

@callback(
   Output("mh-primary-kpi-total-deaths", "children"),
   Output("mh-primary-bar-diagnosis", "figure"),
   Output("mh-primary-line-discharges", "figure"),
   Output("mh-primary-age-group-table", "children"),
   Output("mh-primary-gender-table", "children"),
   Output("mh-primary-county-table", "children"),
   Input("mh-primary-su-filter", "value"),
   Input("mh-primary-mh-filter", "value"),
   Input("mh-primary-age-group-filter", "value"),
   Input("mh-primary-sex-filter", "value"),
   Input("mh-primary-county-filter", "value"),
   Input("mh-primary-year-filter", "value"),
)

def update_dashboard(su, mh, age, sex, county, year):
   """
   This function runs every time the user changes a filter.

   It:
     - Applies all the filters to the data,
     - Builds two graphs (line + stacked bar),
     - Builds two tables,
     - Builds the pie chart.
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
   if su:
       su_ids_filtered = set(dff.loc[(dff["diagnosis_type"] == "su") & (dff["diagnosis"].isin(su)), "record_id"])
       dff = dff[dff["record_id"].isin(su_ids_filtered)]
   if mh:
       mh_ids_filtered = set(dff.loc[(dff["diagnosis_type"] == "mh") & (dff["diagnosis"].isin(mh)), "record_id"])
       dff = dff[dff["record_id"].isin(mh_ids_filtered)]

   if "age_group" in dff.columns:      dff = apply_filter(dff, "age_group", age)
   if "sex" in dff.columns:            dff = apply_filter(dff, "sex", sex)
   if "county" in dff.columns:         dff = apply_filter(dff, "county", county)
   if "year" in dff.columns:           dff = apply_filter(dff, "year", year)

   all_su_ids = set(dff.loc[dff["diagnosis_type"] == "su", "record_id"])
   primary_mh_ids = set(dff.loc[(dff["diagnosis_type"] == "mh") & (dff["is_primary"] == 1), "record_id"])

   cooccuring_ids = all_su_ids.intersection(primary_mh_ids)

   dff = dff[dff["record_id"].isin(cooccuring_ids)]

   # Count unique discharges (each record_id represents one discharge).
   # Used to update the total on the KPI card when user selects the filter
   filter_total = dff["record_id"].nunique()

   # ---------- Bar chart: Discharges by Mental Health diagnosis ----------
   if {"record_id", "diagnosis", "diagnosis_type"}.issubset(dff.columns):
      
       mh_df = dff[dff["diagnosis_type"] == "mh"]


       by_mh = (
           mh_df.groupby("diagnosis")["record_id"]
           .nunique()
           .reset_index().rename(columns={"record_id": "count"})
           .sort_values("count", ascending=True)
       )

       def ellipsize(text, max_len=25):
           if text is None:
               return text
           return text if len(text) <= max_len else text[:max_len] + "..."

       # Cuts off label length after 25 characters
       by_mh["diagnosis"] = by_mh["diagnosis"].apply(ellipsize)

       mh_bar = px.bar(
           by_mh,
           x="count",
           y="diagnosis",
           barmode="stack",
           text="count",
           labels={
               "count": "Number of Discharges",
               "diagnosis": "Mental Health Diagnosis"
           },
       )

       mh_bar.update_traces(
           marker_color="#22767C",
           textposition="outside",
           hovertemplate="Number of Discharges: %{text}<extra></extra>",
       )

       mh_bar.update_layout(
           margin=dict(l=0, r=0, t=10, b=80),
           xaxis=dict(automargin=True),
       )

   else:
       mh_bar = px.bar()

   # ---------- Line chart: Discharges by County and Year ----------
   if {"record_id", "diagnosis", "diagnosis_type", "year"}.issubset(dff.columns):

       mh_df = dff[dff["diagnosis_type"] == "mh"]

       # Count unique discharges per year + county
       by_mh = (
           mh_df.groupby(["year", "diagnosis"])["record_id"].nunique()
           # .reset_index(name="count")
           .reset_index().rename(columns={"record_id": "count"})
       )

       # Order substances in a consistent way for the legend
       substance = sort_opts(dff["diagnosis"]) if "diagnosis" in dff.columns else []
       if substance:
           by_mh["diagnosis"] = pd.Categorical(by_mh["diagnosis"], categories=substance, ordered=True)

       # Build the line graph
       mh_line = px.line(
           by_mh,
           x="year",
           y="count",
           color="diagnosis",
           markers=True,
           labels={"year": "Year", "count": "Discharges", "diagnosis": "Mental Health Diagnosis"},
       )
       # Customize hover text and margins for a cleaner look
       mh_line.update_traces(
           hovertemplate="Year %{x}<br>%{y:,} discharges<extra></extra>"
       )
       mh_line.update_layout(
           margin=dict(l=0, r=20, t=10, b=0),
           xaxis=dict(dtick=1),
           legend=dict(
               y=-1.5
           )
       )
   else:
       # If we don't have the needed columns, return an empty figure
       mh_line = px.line()

   # ---------- Helper for the summary tables ----------
   def tbl(column, categories=None):
       """
       Build a small table that shows the count of unique discharges
       for each value in the chosen column.

       If we pass in a list of categories, we use that order in the table.
       """
       if column not in dff.columns:
           return dbc.Alert(
               f"Column '{column}' not found.",
               color="warning",
               className="mb-0"
           )

       # Count unique discharges per category
       g = dff.groupby(column)["record_id"].nunique().reset_index(name="count")

       # Use the given category order if provided
       if categories:
           g[column] = pd.Categorical(g[column], categories=categories, ordered=True)
           g = g.sort_values(column)

       # Make the counts look nicer with commas
       g["count"] = g["count"].map(lambda x: "<=10" if x <= 10 else f"{int(x):,}")

       # Use friendly display labels for table headers
       header_labels = {
           "age_group": "Age Group",
           "sex": "Sex",
           "county": "County",
       }
       display_column = header_labels.get(column, column)
       g = g.rename(columns={column: display_column, "count": "Discharges"})

       # Build a styled table for the dashboard
       return dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)

   # Return all the updated visuals and tables to Dash
   return (
       f"{filter_total:,}",
       mh_bar,
       mh_line,
       tbl("age_group"),
       tbl("sex"),
       tbl("county"),
   )
