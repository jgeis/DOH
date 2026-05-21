# dashboard_utils.py — Shared utilities for dashboards

import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from theme import register_template
import re


STATEWIDE_COUNTY = "Statewide"
COUNT_SUPPRESSION_THRESHOLD = 10
SUPPRESSED_COUNT_LABEL = "<10*"


# Global preferred order for sidebar filters.
# Unknown/new labels are intentionally placed after these.
FILTER_LABEL_ORDER = [
    "Substance",
    "Substance Type",
    "Primary Substance",
    "Substance Use Diagnosis",
    "Mental Health Diagnosis",
    "Calendar Year",
    "Year",
    "Month",
    "County of Death",
    "County",
    "City",
    "Age Group",
    "Sex",
    "Race/Ethnicity",
    "Hawaii Resident",
    "Homeless",
]


# Global preferred order for right-column summary tables.
RIGHT_TABLE_LABEL_ORDER = [
    "Calendar Year",
    "Year",
    "County",
    "Age Group",
    "Sex",
    "Sex at Birth",
    "Race/Ethnicity",
    "Hawaii Resident",
    "Homeless",
    "Is Homeless",
]


def _normalize_filter_label(label: str) -> str:
    """Normalize filter labels so ordering is resilient to punctuation/case variants."""
    text = re.sub(r"[^a-z0-9]+", " ", str(label).strip().lower())
    return " ".join(text.split())


_FILTER_LABEL_RANK = {
    _normalize_filter_label(label): idx
    for idx, label in enumerate(FILTER_LABEL_ORDER)
}

_RIGHT_TABLE_LABEL_RANK = {
    _normalize_filter_label(label): idx
    for idx, label in enumerate(RIGHT_TABLE_LABEL_ORDER)
}


def _ordered_filters(filters):
    """Return filters ordered by FILTER_LABEL_ORDER, preserving relative order for unknown labels."""
    indexed = list(enumerate(filters))

    def _sort_key(item):
        original_idx, (label_text, _control) = item
        rank = _FILTER_LABEL_RANK.get(_normalize_filter_label(label_text), len(_FILTER_LABEL_RANK))
        return rank, original_idx

    return [flt for _idx, flt in sorted(indexed, key=_sort_key)]


def make_right_summary_tables_col(table_specs, xs: int = 12, md: int = 3):
    """
    Build a right-column block of summary tables in a shared, site-wide order.

    Args:
        table_specs: list of tuples in the form (label, table_id) or
            (label, table_id, heading)
        xs, md: responsive widths for the right column
    """
    indexed = list(enumerate(table_specs))

    def _sort_key(item):
        original_idx, spec = item
        label = spec[0]
        norm = _normalize_filter_label(label)
        rank = _RIGHT_TABLE_LABEL_RANK.get(norm, len(_RIGHT_TABLE_LABEL_RANK))
        return rank, original_idx

    ordered_specs = [spec for _idx, spec in sorted(indexed, key=_sort_key)]

    table_cols = []
    for idx, spec in enumerate(ordered_specs):
        label = spec[0]
        table_id = spec[1]
        heading = spec[2] if len(spec) > 2 else None
        side_class = "pe-1 mb-3" if idx == 0 else "ps-1 mb-3"
        children = []
        if heading:
            children.append(html.H6(heading, className="mb-2"))
        children.append(
            html.Div(
                id=table_id,
                className="mobile-side-table",
                style={"overflowX": "auto"},
            )
        )

        table_cols.append(
            dbc.Col(
                children,
                xs=12,
                md=12,
                className=side_class,
            )
        )

    return dbc.Col([dbc.Row(table_cols, className="g-2")], xs=xs, md=md)

# This applies our custom Plotly theme (colors, fonts, etc.)
register_template()


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


def sort_opts(series):
    """
    Turn a column into a sorted list of unique values.

    We also make sure "Unknown" always shows up at the end of the list
    so the drop-down menus look cleaner.
    """
    def _normalize_age_group_label(text: str) -> str:
        """Normalize age labels like 'Under 15' to '<15' for consistent menu display."""
        s = str(text).strip()
        m = re.fullmatch(r"under\s+(\d+)", s, flags=re.IGNORECASE)
        if m:
            return f"<{m.group(1)}"
        return s

    normalized = pd.Series(series).dropna().astype(str).map(_normalize_age_group_label)
    vals = [str(v) for v in pd.Series(normalized.unique()).tolist()]

    def _lt_sort_key(text: str):
        """Sort '<' bucket values by numeric component when available."""
        m = re.search(r"\d+", text)
        return (int(m.group()) if m else float("inf"), text)

    less_than = sorted([v for v in vals if "<" in v], key=_lt_sort_key)
    has_unknown = "Unknown" in vals

    middle = sorted([v for v in vals if "<" not in v and v != "Unknown"])
    ordered = less_than + middle + (["Unknown"] if has_unknown else [])
    return ordered


def format_count_display(value, threshold: int = COUNT_SUPPRESSION_THRESHOLD, suppressed_label: str = SUPPRESSED_COUNT_LABEL) -> str:
    """
    Format a count for UI display with small-number suppression.

    Values where 0 < value < threshold are shown as '<10*' by default.
    """
    if value is None or pd.isna(value):
        return "0"

    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return str(value)

    if 0 < numeric < threshold:
        return suppressed_label
    return f"{numeric:,}"


def opts_list(values):
    """
    Turn a simple list of values into the format Dash expects for
    drop-down choices (label + value).
    """
    return [{"label": v, "value": v} for v in values]


def format_display_list(values) -> str:
    """
    Format a list of values for display using natural-language "and" rules.

    Examples:
    - [A] -> "A"
    - [A, B] -> "A and B"
    - [A, B, C] -> "A, B, and C" (Oxford comma)
    """
    items = [str(v).strip() for v in values if str(v).strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def with_statewide_county(values) -> list[str]:
    """
    Return county values with a synthetic "Statewide" option prepended.

    This does not modify database data; it only affects UI/filter choices.
    """
    cleaned = [str(v).strip() for v in values if str(v).strip()]
    non_statewide = [v for v in cleaned if v.lower() != STATEWIDE_COUNTY.lower()]
    return [STATEWIDE_COUNTY] + non_statewide


def statewide_first(values) -> list[str]:
    """
    Return values in the same order, but move "Statewide" to the front if present.

    Unlike `with_statewide_county`, this does not inject synthetic values.
    """
    cleaned = [str(v).strip() for v in values if str(v).strip()]
    unique = list(dict.fromkeys(cleaned))
    has_statewide = any(v.lower() == STATEWIDE_COUNTY.lower() for v in unique)
    if not has_statewide:
        return unique
    non_statewide = [v for v in unique if v.lower() != STATEWIDE_COUNTY.lower()]
    return [STATEWIDE_COUNTY] + non_statewide


def apply_county_filter(frame: pd.DataFrame, county_value, county_col: str = "county") -> pd.DataFrame:
    """
    Apply county filtering with support for synthetic "Statewide" semantics.

    Rules:
      - Empty selection => no county filtering
      - Selection includes "Statewide" => no county filtering
      - Otherwise => filter to selected county/countries
    """
    if county_col not in frame.columns:
        return frame

    if county_value is None or (isinstance(county_value, (list, tuple, set)) and len(county_value) == 0):
        return frame

    selected = county_value if isinstance(county_value, (list, tuple, set)) else [county_value]
    normalized = [str(v).strip().lower() for v in selected if str(v).strip()]

    if not normalized:
        return frame

    if STATEWIDE_COUNTY.lower() in normalized:
        return frame

    selected_set = set(normalized)
    mask = frame[county_col].astype(str).str.strip().str.lower().isin(selected_set)
    return frame[mask]


def county_output_should_include_statewide(county_value) -> bool:
    """
    Decide whether county-based outputs should include a synthetic "Statewide" row.

    Include it when:
      - no county filter is selected, or
      - county selection explicitly includes "Statewide".
    """
    if county_value is None:
        return True

    selected = county_value if isinstance(county_value, (list, tuple, set)) else [county_value]
    if len(selected) == 0:
        return True

    normalized = [str(v).strip().lower() for v in selected if str(v).strip()]
    if not normalized:
        return True

    return STATEWIDE_COUNTY.lower() in normalized


def append_statewide_aggregate_rows(
    grouped_df: pd.DataFrame,
    value_col: str,
    county_col: str = "county",
) -> pd.DataFrame:
    """
    Append synthetic statewide aggregate rows to a county-grouped DataFrame.

    The function preserves any non-county grouping columns (e.g., year),
    summing `value_col` across counties for each grouping combination.
    """
    if grouped_df.empty or county_col not in grouped_df.columns or value_col not in grouped_df.columns:
        return grouped_df

    base = grouped_df[
        grouped_df[county_col].astype(str).str.strip().str.lower() != STATEWIDE_COUNTY.lower()
    ].copy()

    if base.empty:
        return grouped_df

    non_county_group_cols = [c for c in base.columns if c not in {county_col, value_col}]

    if non_county_group_cols:
        statewide = base.groupby(non_county_group_cols, as_index=False)[value_col].sum()
    else:
        statewide = pd.DataFrame({value_col: [base[value_col].sum()]})

    statewide[county_col] = STATEWIDE_COUNTY
    statewide = statewide[base.columns.tolist()]
    return pd.concat([base, statewide], ignore_index=True)


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


# Shared chart spacing defaults to keep line/bar modebar overlap consistent site-wide.
STANDARD_CHART_SIDE_MARGINS = {"l": 0, "r": 12}
STANDARD_BAR_MARGIN = {**STANDARD_CHART_SIDE_MARGINS, "t": 30, "b": 80}
STANDARD_LINE_MARGIN = {**STANDARD_CHART_SIDE_MARGINS, "t": 30, "b": 80}
STANDARD_MAP_MARGIN = {"l": 0, "r": 0, "t": 30, "b": 0}
STANDARD_NON_AXIS_MARGIN = {**STANDARD_CHART_SIDE_MARGINS, "t": 30, "b": 0}


def apply_standard_bar_layout(
    fig,
    margin: dict | None = None,
    xaxis: dict | None = None,
    yaxis: dict | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for bar charts, with optional overrides."""
    merged_margin = STANDARD_BAR_MARGIN.copy()
    if margin:
        merged_margin.update(margin)

    merged_xaxis = {"automargin": True}
    if xaxis:
        merged_xaxis.update(xaxis)

    merged_yaxis = {"automargin": True}
    if yaxis:
        merged_yaxis.update(yaxis)

    fig.update_layout(
        margin=merged_margin,
        xaxis=merged_xaxis,
        yaxis=merged_yaxis,
        **layout_kwargs,
    )
    return fig


def apply_standard_line_layout(
    fig,
    margin: dict | None = None,
    xaxis: dict | None = None,
    yaxis: dict | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for line charts, with optional overrides."""
    merged_margin = STANDARD_LINE_MARGIN.copy()
    if margin:
        merged_margin.update(margin)

    merged_xaxis = {"automargin": True}
    if xaxis:
        merged_xaxis.update(xaxis)

    merged_yaxis = {"automargin": True}
    if yaxis:
        merged_yaxis.update(yaxis)

    fig.update_layout(
        margin=merged_margin,
        xaxis=merged_xaxis,
        yaxis=merged_yaxis,
        **layout_kwargs,
    )
    return fig


def apply_standard_map_layout(
    fig,
    margin: dict | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for map charts, with optional overrides."""
    merged_margin = STANDARD_MAP_MARGIN.copy()
    if margin:
        merged_margin.update(margin)

    fig.update_layout(
        margin=merged_margin,
        **layout_kwargs,
    )
    return fig


def apply_standard_non_axis_layout(
    fig,
    margin: dict | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for non-axis charts (pie/sunburst), with optional overrides."""
    merged_margin = STANDARD_NON_AXIS_MARGIN.copy()
    if margin:
        merged_margin.update(margin)

    fig.update_layout(
        margin=merged_margin,
        **layout_kwargs,
    )
    return fig


def make_kpi_card(label: str, count_id: str | None = None, count: int | None = None) -> dbc.Card:
    """
    Build the standard big green KPI card shown at the top-left of every page.

    Use `count_id` when the number is updated dynamically by a Dash callback
    (the callback should target that element ID). Use `count` for a pre-computed
    static total that never changes with filters.

    Args:
        label:    Descriptive text shown beneath the number (e.g. "Number of Discharges").
        count_id: HTML id for the <h2> element so a callback can update it at runtime.
        count:    Static integer to display directly in the card (formatted with commas).
    """
    if count_id is not None:
        value_el = html.H2(id=count_id, className="text-white")
    else:
        value_el = html.H2(format_count_display(count) if count is not None else "—", className="text-white")
    return dbc.Card(
        dbc.CardBody([
            value_el,
            html.Small(label, className="card-title text-white"),
        ]),
        className="bg-success text-center mb-4",
    )


def make_sidebar_helper_text(text: str | list[str] | tuple[str, ...]) -> html.Div:
    """
    Build the standardized helper text block shown under the filters card.

    Accepts either one string or multiple strings. Multiple strings are
    rendered as separate paragraphs with compact spacing.
    """
    lines = [text] if isinstance(text, str) else list(text)
    return html.Div(
        [
            html.P(line, className=("mb-0" if i == len(lines) - 1 else "mb-2"))
            for i, line in enumerate(lines)
        ],
        className="mt-3 text-muted small",
    )


def compute_last_updated_value(df: pd.DataFrame | None) -> str | None:
    """
    Compute a display value for the most recent date found in a dataframe.

    Prefers date-like columns; falls back to max year when only year data exists.
    """
    if df is None or df.empty:
        return None

    latest_ts = None
    year_max = None

    for col in df.columns:
        col_name = str(col).strip().lower()
        series = df[col]

        if col_name == "year":
            years = pd.to_numeric(series, errors="coerce").dropna()
            if not years.empty:
                candidate_year = int(years.max())
                year_max = candidate_year if year_max is None else max(year_max, candidate_year)
            continue

        if "date" in col_name or col_name in {"day", "month", "period"}:
            parsed = pd.to_datetime(series, errors="coerce")
            parsed = parsed.dropna()
            if parsed.empty:
                continue
            candidate_ts = parsed.max()
            if latest_ts is None or candidate_ts > latest_ts:
                latest_ts = candidate_ts

    if latest_ts is not None:
        return latest_ts.strftime("%Y-%m-%d")

    if year_max is not None:
        return str(year_max)

    return None


def make_last_updated_block(last_updated_value: str | None):
    """Render standardized Last Updated text for the left sidebar."""
    if not last_updated_value:
        return None

    return html.Div(
        [
            html.Small("Last Updated", className="fw-semibold text-muted d-block"),
            html.Div(last_updated_value),
        ],
        className="mt-3 small",
    )


def make_left_sidebar(
    kpi_card_component,
    reset_filters_button,
    filters_card,
    helper_text: str | list[str] | tuple[str, ...] | None = None,
    last_updated_value: str | None = None,
    xs: int = 12,
    md: int = 3,
) -> dbc.Col:
    """
    Build the standardized left sidebar column used by dashboards.

    Order is always:
      1) KPI card
      2) Reset button
      3) Filters card
      4) Optional Last Updated
      5) Optional helper text block
    """
    children = [kpi_card_component, reset_filters_button, filters_card]
    last_updated_block = make_last_updated_block(last_updated_value)
    if last_updated_block is not None:
        children.append(last_updated_block)
    if helper_text:
        if isinstance(helper_text, (str, list, tuple)):
            children.append(make_sidebar_helper_text(helper_text))
        else:
            children.append(helper_text)
    return dbc.Col(children, xs=xs, md=md)


def make_filters_card(
    card_id: str,
    filters,
    title: str = "Filter Data",
    start_tab_index: int = 1,
    class_name: str = "mb-4",
) -> dbc.Card:
    """
    Build a standardized filters card with consistent label formatting and tab order.

    Args:
        card_id: ID for the outer filters card.
        filters: Iterable of (label_text, dash_component) tuples in visual order.
        title: Heading shown at the top of the filters card.
        start_tab_index: Tab index used for the heading; labels start at +1 in order.
        class_name: CSS class name for the outer card.
    """
    def _normalize_spacing_class(existing_class: str | None, is_last: bool) -> str:
        """Replace any existing mb-* class with mb-2/mb-0 based on position."""
        desired = "mb-0" if is_last else "mb-2"
        tokens = (existing_class or "").split()
        tokens = [t for t in tokens if not re.fullmatch(r"mb-\d+", t)]
        tokens.append(desired)
        return " ".join(tokens).strip()

    def _with_enforced_spacing(control_component, is_last: bool):
        """Clone a Dash component with normalized className spacing."""
        props = control_component.to_plotly_json().get("props", {})
        props["className"] = _normalize_spacing_class(props.get("className"), is_last)
        return control_component.__class__(**props)

    ordered = _ordered_filters(filters)

    children: list = [html.H5(title, tabIndex=start_tab_index)]

    total = len(ordered)
    for idx, (label_text, control) in enumerate(ordered, start=1):
        is_last = idx == total
        normalized_control = _with_enforced_spacing(control, is_last)
        control_id = getattr(normalized_control, "id", None)
        children.append(
            html.Label(
                label_text,
                htmlFor=control_id,
                tabIndex=start_tab_index + idx,
                className="form-label",
            )
        )
        children.append(normalized_control)

    return dbc.Card(dbc.CardBody(children), id=card_id, className=class_name)


def dropdown_filter(label: str, control_id: str, **kwargs):
    """
    Convenience builder for dropdown filters used by make_filters_card.

    If persistence is not provided, defaults to the control id.
    """
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return label, dcc.Dropdown(id=control_id, **kwargs)


def checklist_filter(label: str, control_id: str, **kwargs):
    """Convenience builder for checklist filters used by make_filters_card."""
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return label, dcc.Checklist(id=control_id, **kwargs)


def radio_filter(label: str, control_id: str, **kwargs):
    """Convenience builder for radio-item filters used by make_filters_card."""
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return label, dcc.RadioItems(id=control_id, **kwargs)
