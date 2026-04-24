# sudors_polysubstance_dashboard.py — Alternative visualizations for substance co-occurrence patterns

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

from theme import register_template
from db_utils import execute_query

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
    
    sql = load_sql_query("load_sudors_data_view_diag_su$")
    
    # Execute query using db_utils (automatically uses correct database)
    df = execute_query(sql)
    print(f"load_sudors_data_view_diag_su$ returned {len(df):,} rows")

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


# ---------- Helper functions ----------
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


# ---------- Layout ----------
def layout_for(is_mobile: bool = False):
    """Build the full page layout with co-occurrence visualizations."""
    
    return dbc.Container([
        # Store mobile state for callbacks
        dcc.Store(id="sudors-cooccurrence-is-mobile", data=is_mobile),
        
        html.H2(
            "Polysubstance Co-occurrence Analysis — Alternative Views",
            className="text-white bg-dark p-3 text-center mb-4"
        ),
        
        # Explanation section
        dbc.Alert([
            html.H5("About These Visualizations", className="alert-heading"),
            html.P([
                "These charts show relationships between different substances found in polysubstance cases. ",
                "Each visualization offers a different perspective on how substances co-occur."
            ]),
        ], color="info", className="mb-4"),
        
        # Visualization 1: Grouped Bar Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Co-occurrence by Primary Substance", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "When a primary substance is present, this shows what percentage of those cases ",
                            "also contain each other substance. Use the filter below to focus on one substance.",
                            html.Br() if is_mobile else "",
                            html.Small("(Scroll horizontally to see all substances)", className="text-muted") if is_mobile else ""
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            html.Div(
                                html.Div(
                                    dcc.Graph(
                                        id="sudors-cooccurrence-bar-chart",
                                        config={"displayModeBar": True, "displaylogo": False},
                                        style={"height": "650px" if is_mobile else "500px"}
                                    ),
                                    className="graph-inner" if is_mobile else ""
                                ),
                                className="hscroll-graph" if is_mobile else ""
                            )
                        ),
                        html.Hr(className="my-3"),
                        html.Label("Filter by Primary Substance:", className="form-label fw-bold"),
                        dcc.Dropdown(
                            id="sudors-cooccurrence-primary-substance",
                            options=[{"label": "All substances (no filter)", "value": ""}] + 
                                    [{"label": s, "value": s} for s in sorted(df_raw['substance'].unique())],
                            value="",
                            clearable=False,
                            className="mb-2"
                        ),
                        html.Small("Select a specific substance to see what co-occurs with it, or choose 'All substances' to see the full overview.", 
                                   className="text-muted")
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

        # Visualization 2: Sunburst Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Co-occurrence Sunburst", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "This shows a pie chart-like view of cases that also contain another substance.",
                            html.Br() if is_mobile else "",
                            html.Small("(Scroll horizontally to see all substances)", className="text-muted") if is_mobile else ""
                        ], className="text-muted mb-3"),
                        dcc.Loading(
                            html.Div(
                                html.Div(
                                    dcc.Graph(
                                        id="sudors-cooccurrence-sunburst",
                                        config={"displayModeBar": True, "displaylogo": False},
                                        style={"height": "650px" if is_mobile else "500px"}
                                    ),
                                    className="graph-inner" if is_mobile else ""
                                ),
                                className="hscroll-graph" if is_mobile else ""
                            )
                        ),
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

    ], fluid=True)

layout = layout_for(is_mobile=False)


# ---------- Callbacks ----------

@callback(
    Output("sudors-cooccurrence-bar-chart", "figure"),
    Input("sudors-cooccurrence-primary-substance", "value"),
    Input("sudors-cooccurrence-is-mobile", "data"),
)
def update_bar_chart(primary_substance, is_mobile):
    """Create grouped bar chart showing co-occurrence percentages."""
    
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Build co-occurrence data
    co_data = build_cooccurrence_data(df_raw)
    
    if co_data.empty:
        return go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
    
    # Mobile-specific adjustments
    if is_mobile:
        text_size = 8
        height = 650
        width = 900  # Fixed width for scrolling
        title_size = 13
        margin_left = 140
        margin_right = 40
        margin_top = 70
        margin_bottom = 100
    else:
        text_size = 10
        height = 500
        width = None  # Auto width
        title_size = 16
        margin_left = 150
        margin_right = 50  # Can reduce now that legend is on top
        margin_top = 120  # More room for horizontal legend
        margin_bottom = 120  # More room for x-axis labels
    
    # Filter by primary substance if selected (and not empty string)
    if primary_substance and primary_substance != "":
        co_data = co_data[co_data['Primary'] == primary_substance]
        if co_data.empty:
            return go.Figure().add_annotation(
                text=f"No co-occurrence data for {primary_substance}",
                showarrow=False
            )
        
        # Sort by percentage descending (highest to lowest) for both mobile and desktop
        co_data = co_data.sort_values('Percentage', ascending=False)
        
        # Create custom text with percentage and count
        co_data['label'] = co_data.apply(
            lambda row: f"{row['Percentage']:.1f}% (n={int(row['Count']):,})", 
            axis=1
        )
        
        # Create formatted hover text
        co_data['Count_formatted'] = co_data['Count'].apply(lambda x: f"{int(x):,}")
        co_data['Total_formatted'] = co_data['Total'].apply(lambda x: f"{int(x):,}")
        
        # Mobile: vertical bars (x=substance, y=percentage), Desktop: horizontal bars (x=percentage, y=substance)
        if is_mobile:
            fig = px.bar(
                co_data,
                x='Also Found',
                y='Percentage',
                orientation='v',
                title=f"When {primary_substance} is present, % with other substances",
                labels={'Percentage': 'Co-occurrence %', 'Also Found': 'Other Substance'},
                text='label',
                hover_data={
                    'Count': False, 
                    'Total': False, 
                    'label': False,
                    'Count_formatted': ':.0f',
                    'Total_formatted': ':.0f'
                },
                custom_data=['Count_formatted', 'Total_formatted']
            )
            
            fig.update_traces(
                textposition='outside',
                textangle=0,
                hovertemplate='<b>%{x}</b><br>' +
                             'Co-occurrence: %{y:.1f}%<br>' +
                             'Count: %{customdata[0]}<br>' +
                             'Total: %{customdata[1]}<extra></extra>',
                textfont=dict(size=text_size)
            )
        else:
            fig = px.bar(
                co_data,
                x='Percentage',
                y='Also Found',
                orientation='h',
                title=f"When {primary_substance} is present, % with other substances",
                labels={'Percentage': 'Co-occurrence %', 'Also Found': 'Other Substance'},
                text='label',
                hover_data={
                    'Count': False, 
                    'Total': False, 
                    'label': False,
                    'Count_formatted': ':.0f',
                    'Total_formatted': ':.0f'
                },
                custom_data=['Count_formatted', 'Total_formatted']
            )
            
            fig.update_traces(
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>' +
                             'Co-occurrence: %{x:.1f}%<br>' +
                             'Count: %{customdata[0]}<br>' +
                             'Total: %{customdata[1]}<extra></extra>',
                textfont=dict(size=text_size)
            )
        
    else:
        # Show all primary substances
        # Add custom text label with percentage and count
        co_data['label'] = co_data.apply(
            lambda row: f"{row['Percentage']:.1f}% (n={int(row['Count']):,})" if not is_mobile else f"{row['Percentage']:.0f}%", 
            axis=1
        )
        
        # Create formatted hover text
        co_data['Count_formatted'] = co_data['Count'].apply(lambda x: f"{int(x):,}")
        co_data['Total_formatted'] = co_data['Total'].apply(lambda x: f"{int(x):,}")
        
        fig = px.bar(
            co_data,
            x='Primary',
            y='Percentage',
            color='Also Found',
            barmode='group',
            title='Co-occurrence patterns: When [Primary] is present, % with other substances',
            labels={'Percentage': 'Co-occurrence %', 'Primary': 'Primary Substance'},
            text='label',
            hover_data={
                'Count': False, 
                'Total': False, 
                'label': False,
                'Count_formatted': ':.0f',
                'Total_formatted': ':.0f'
            },
            custom_data=['Count_formatted', 'Total_formatted', 'Also Found']
        )
        
        fig.update_traces(
            textposition='outside',
            textangle=0,
            hovertemplate='<b>%{customdata[2]}</b><br>' +
                         'Primary: %{x}<br>' +
                         'Co-occurrence: %{y:.1f}%<br>' +
                         'Count: %{customdata[0]}<br>' +
                         'Total: %{customdata[1]}<extra></extra>',
            textfont=dict(size=text_size)
        )
    
    # Apply mobile-responsive layout
    # X-axis angle: 45° for grouped view (substance names), 45° for mobile filtered (substance names), 0° for desktop filtered (percentages)
    x_angle = 45 if (not primary_substance or primary_substance == "") else (45 if is_mobile else 0)
    
    fig.update_layout(
        height=height,
        width=width,
        title=dict(font=dict(size=title_size)),
        xaxis=dict(
            tickangle=x_angle,
            tickfont=dict(size=text_size)
        ),
        yaxis=dict(tickfont=dict(size=text_size)),
        margin=dict(
            l=margin_left if primary_substance and primary_substance != "" else (margin_left - 10), 
            r=margin_right, 
            t=margin_top, 
            b=margin_bottom
        ),
        legend=dict(
            font=dict(size=text_size),
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above plot area
            xanchor="center",
            x=0.5  # Center horizontally
        ) if not primary_substance or primary_substance == "" else dict(font=dict(size=text_size)),
        autosize=False if is_mobile else True
    )
    
    return fig


@callback(
    Output("sudors-cooccurrence-sunburst", "figure"),
    Input("sudors-cooccurrence-primary-substance", "value"),
)

def update_sunburst(primary_substance):
    """Create grouped bar chart showing co-occurrence percentages."""
    
    if df_raw.empty or 'substance' not in df_raw.columns:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    

    sunburst_df = build_sunburst_cooccurrence_data(df_raw)
    
    # Count occurrences of each pair
    sunburst_df = (
        sunburst_df
        .value_counts()
        .reset_index(name='Count')
    )

    if primary_substance:
        sunburst_df = sunburst_df[sunburst_df['Primary'] == primary_substance]

    if sunburst_df.empty:
        return go.Figure().add_annotation(text="No co-occurrence data available", showarrow=False)
    
    fig = px.sunburst(
        sunburst_df,
        path=["Primary", "Also Found"],
        values="Count",
    )

    return fig