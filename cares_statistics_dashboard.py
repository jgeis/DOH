# cares_statistics_dashboard.py — Hawai'i CARES 988 Statistics page

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px

from config import USE_MSSQL
from db_utils import execute_query
from dashboard_utils import (
    load_sql_query,
    make_last_updated_block,
    compute_adaptive_horizontal_bar_height,
    apply_standard_bar_layout,
    apply_standard_single_series_bar_trace,
    apply_standard_line_layout,
    make_sidebar_helper_text,
    create_styled_table,
)
from theme import register_template

register_template()


def _query_name(base_name):
    """Return DB-specific named query key for MSSQL/SQLite compatibility."""
    return base_name if USE_MSSQL else f"{base_name}_sqlite"


def _compact_tick_label(value):
    """Format numeric ticks as compact labels like 6K, 1.5M."""
    v = float(value)
    if v >= 1_000_000:
        m = v / 1_000_000
        return f"{int(m)}M" if m.is_integer() else f"{m:.1f}M"
    if v >= 1_000:
        k = v / 1_000
        return f"{int(k)}K" if k.is_integer() else f"{k:.1f}K"
    return f"{int(v)}"


# ---------------------------------------------------------
# NEW: Data Loader for KPI Cards
# ---------------------------------------------------------
def _load_top_box_data():
    sql = load_sql_query("load_cares_statistics_top_box")
    df = execute_query(sql)
    
    if df.empty:
        return {}
    
    # Convert the first row into a case-insensitive dictionary
    # so we don't have to worry about SQL casing quirks
    row_dict = df.iloc[0].to_dict()
    return {k.lower(): v for k, v in row_dict.items()}


# ---------------------------------------------------------
# KPI Card UI Helper
# ---------------------------------------------------------
def _make_kpi_card(title, value, bg_color):
    return dbc.Card(
        dbc.CardBody(
            [
                # Changed text colors to white/light-gray to contrast with the dark backgrounds
                html.H6(title, className="card-title text-center mb-1", style={"fontSize": "0.85rem", "color": "#f8f9fa"}),
                html.H4(str(value), className="card-text text-center fw-bold mb-0", style={"color": "white"}),
            ]
        ),
        className="shadow-sm h-100",
        style={"backgroundColor": bg_color, "border": "none"}
    )

# ---------------------------------------------------------
# NEW: Vertical Banner UI Helper
# ---------------------------------------------------------
def _make_vertical_banner(text):
    return html.Div(
        # 1. The inner text element (Rotated, but isolated so it can't stretch)
        html.Span(
            text,
            style={
                "writingMode": "vertical-rl",
                "transform": "rotate(180deg)",
                "letterSpacing": "0.1rem",
                "textTransform": "uppercase",
                "whiteSpace": "nowrap", # Forces text to stay on one line
            }
        ),
        # 2. The outer background box (Behaves normally, fills the column height)
        className="d-flex align-items-center justify-content-center fw-bold text-muted h-100",
        style={
            "backgroundColor": "#e9ecef",
            "borderRadius": "0.25rem",
            "padding": "15px", # Slightly wider padding to give the text breathing room
            "minWidth": "50px", # Prevents the column from squishing too much
        }
    )


def _load_top_10_reasons_table():
    sql = load_sql_query(_query_name("load_cares_calls_by_nature_top_10"))
    df = execute_query(sql)

    col_lookup = {c.lower(): c for c in df.columns}
    if "nature_of_call" in col_lookup and col_lookup["nature_of_call"] != "Nature_of_Call":
        df = df.rename(columns={col_lookup["nature_of_call"]: "Nature_of_Call"})
    if "percentage_of_total" in col_lookup and col_lookup["percentage_of_total"] != "percentage_of_total":
        df = df.rename(columns={col_lookup["percentage_of_total"]: "percentage_of_total"})

    if "Nature_of_Call" in df.columns:
        df = df.rename(columns={"Nature_of_Call": "Category"})
    if "percentage_of_total" in df.columns:
        df = df.rename(columns={"percentage_of_total": "Percent"})

    if "Percent" in df.columns:
        df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce").fillna(0)
        df["Percent"] = df["Percent"].map(lambda v: f"{v:.2f}%")

    keep_cols = [col for col in ["Category", "Percent"] if col in df.columns]
    return df[keep_cols]


def _load_last_updated_value():
    sql = load_sql_query(_query_name("load_cares_calls_last_updated"))
    df = execute_query(sql)
    if df.empty or "last_updated" not in df.columns:
        return None

    parsed = pd.to_datetime(df.iloc[0]["last_updated"], errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _load_calls_line_chart():
    sql = load_sql_query("load_cares_calls_by_line_6_months")
    df = execute_query(sql)

    col_lookup = {c.lower(): c for c in df.columns}
    if "line" in col_lookup and col_lookup["line"] != "Line":
        df = df.rename(columns={col_lookup["line"]: "Line"})
    if "date" in col_lookup and col_lookup["date"] != "Date":
        df = df.rename(columns={col_lookup["date"]: "Date"})
    if "num_calls" in col_lookup and col_lookup["num_calls"] != "num_calls":
        df = df.rename(columns={col_lookup["num_calls"]: "num_calls"})

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[df["Date"].notna()].copy()
    df = df.sort_values("Date")
    df["Month"] = df["Date"].dt.strftime("%b")

    df["Line"] = df["Line"].replace({"All_Phones": "Phone Calls"})

    fig = px.line(
        df,
        x="Month",
        y="num_calls",
        color="Line",
        markers=True,
        labels={
            "Month": "Month",
            "num_calls": "# of calls/chats/texts",
            "Line": "Contact Type",
        },
    )
    
    fig.update_xaxes(categoryorder="array", categoryarray=df["Month"])

    apply_standard_line_layout(
        fig,
        yaxis=dict(rangemode="tozero", title="# of calls/chats/texts"),
        xaxis=dict(title="Month"),
        title=None,
        legend_title_text=None,
    )

    max_calls = int(pd.to_numeric(df["num_calls"], errors="coerce").fillna(0).max()) if not df.empty else 0
    if max_calls > 0:
        if max_calls <= 10_000:
            step = 1_000
        elif max_calls <= 50_000:
            step = 5_000
        else:
            step = 10_000

        upper = ((max_calls + step - 1) // step) * step
        tickvals = list(range(0, upper + step, step))
        ticktext = [_compact_tick_label(v) for v in tickvals]
        fig.update_yaxes(tickmode="array", tickvals=tickvals, ticktext=ticktext)

    fig.update_traces(hovertemplate="%{fullData.name}: %{y:,}<extra></extra>")
    fig.update_layout(hovermode="x unified", hoversort="value descending")

    return fig


def _load_cmo_bar_chart():
    sql = load_sql_query("load_crisis_mobile_outreach_6_months")
    df = execute_query(sql)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[df["Date"].notna()].copy()
    df = df.sort_values("Date")
    df["Month"] = df["Date"].dt.strftime("%b")

    fig = px.bar(
        df,
        x="Month",
        y="num_calls",
        labels={
            "Month": "Month",
            "num_calls": "# of CMOs",
        },
        text="num_calls",
    )
    apply_standard_bar_layout(
        fig,
        yaxis=dict(title="# of CMOs"),
        xaxis=dict(title="Month"),
    )
    apply_standard_single_series_bar_trace(
        fig, 
        hovertemplate="%{x}: %{y:,}<extra></extra>"
    )
    return fig


from section_texts import SECTION_TEXTS
cares_statistics_sidebar_text = make_sidebar_helper_text(SECTION_TEXTS.get("cares-statistics", []))

def layout():
    try:
        top_box_data = _load_top_box_data()
        top_10_df = _load_top_10_reasons_table()
        last_updated_value = _load_last_updated_value()
        calls_line_fig = _load_calls_line_chart()
        cmo_bar_fig = _load_cmo_bar_chart()
    except Exception as exc:
        return dbc.Container(
            dbc.Alert(
                f"Unable to load CARES statistics data in the current database mode. Details: {exc}",
                color="warning",
                className="mt-2",
            ),
            fluid=True,
        )

    def get_val(key):
        return top_box_data.get(key.lower(), "N/A")

    # Define our row colors
    color_calls = "rgb(42, 97, 53)"
    color_chats = "rgb(101, 63, 17)"
    color_texts = "rgb(60, 116, 123)"

    kpi_cards = [
        # Top Row (Calls)
        _make_kpi_card("Call Volume", get_val("CallVolume"), color_calls),
        _make_kpi_card("Call Answer Rate", get_val("CallAnswer"), color_calls),
        _make_kpi_card("Call Answer Speed (secs)", get_val("CallSpeed"), color_calls),
        _make_kpi_card("Call Stabilization Rate", get_val("CallStab"), color_calls),
        
        # Middle Row (Chats)
        _make_kpi_card("Chat Volume", get_val("ChatVol"), color_chats),
        _make_kpi_card("Chat Answer Rate", get_val("ChatAnswer"), color_chats),
        _make_kpi_card("Chat Answer Speed (secs)", get_val("ChatSpeed"), color_chats),
        _make_kpi_card("Chat Stabilization Rate", get_val("ChatStab"), color_chats),
        
        # Bottom Row (Texts)
        _make_kpi_card("Text Volume", get_val("TextVol"), color_texts),
        _make_kpi_card("Text Answer Rate", get_val("TextAnswer"), color_texts),
        _make_kpi_card("Text Answer Speed (secs)", get_val("TextSpeed"), color_texts),
        _make_kpi_card("Text Stabilization Rate", get_val("TextStab"), color_texts),
    ]

    kpi_grid_cols = [dbc.Col(card, xs=6, sm=4, md=3) for card in kpi_cards]

    table_component = create_styled_table(top_10_df)

    return dbc.Container(
        [
            # ROW 1: KPI Grid with Banner
            dbc.Row(
                [
                    dbc.Col(_make_vertical_banner("Past Month"), width="auto"),
                    dbc.Col(dbc.Row(kpi_grid_cols, className="g-3"), width=True)
                ],
                className="g-3 mb-4 align-items-stretch" 
            ),
            
            html.Hr(className="mb-4"),
            
            # ROW 2: Charts & Tables with Banner
            dbc.Row(
                [
                    dbc.Col(_make_vertical_banner("Past 6 Months"), width="auto"),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H5("Top 10 reasons for contacting Hawai'i CARES 988", className="plot-card-header mb-2"),
                                        html.Div(table_component, style={"overflowX": "auto"}),
                                        cares_statistics_sidebar_text,
                                        html.Div(make_last_updated_block(last_updated_value), className="mt-2"),
                                    ],
                                    xs=12, md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H5("Phone Call, Chat, & Text Volumes", className="plot-card-header mb-2"),
                                        dcc.Graph(
                                            id="cares-statistics-calls-line-chart",
                                            figure=calls_line_fig,
                                            config={"displayModeBar": True, "displaylogo": False},
                                            style={"width": "100%", "height": "450px"},
                                        ),
                                    ],
                                    xs=12, md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H5("Crisis Mobile Outreach (CMO)", className="plot-card-header mb-2"),
                                        dcc.Graph(
                                            id="cares-statistics-cmo-bar-chart",
                                            figure=cmo_bar_fig,
                                            config={"displayModeBar": True, "displaylogo": False},
                                            style={"width": "100%", "height": "450px"},
                                        ),
                                    ],
                                    xs=12, md=4,
                                ),
                            ],
                            className="g-3",
                        ),
                        width=True
                    )
                ],
                className="g-3 align-items-stretch"
            )
        ],
        fluid=True,
    )