
# Mapping from code/column names to canonical filter display labels
FILTER_LABELS = {
    "Substance": "Substance Type",
    "Substance Type": "Substance Type",
    "primary_substance": "Primary Substance",
    "Mental Health Diagnosis": "Mental Health Diagnosis",
    "Year": "Calendar Year",
    "Calendar Year": "Calendar Year",
    "Month": "Month",
    "county_of_death": "County",
    "County": "County",
    "city": "City",
    "Age Group": "Age Group",
    "Sex": "Sex at Birth",
    "sex": "Sex at Birth",
    "Gender": "Sex at Birth",
    "sex_at_birth": "Sex at Birth",
    "Race/Ethnicity": "Race/Ethnicity",
    "Hawaii Resident": "Hawaii Resident",
    "Hawaii Residency": "Hawaii Resident",
    "Homeless Status": "Is Homeless",
    "Referral Destination": "Referral Destination",
    "Service Modality": "Service Modality",
    "Service Category": "Service Category",
    "Crisis Line": "Crisis Line",
    
}

def get_standard_filter_label(label: str) -> str:
    """
    Return the canonical display label for a filter, given a code/column name or variant.
    Falls back to the original label if not found.
    """
    key = str(label).strip().lower().replace(" ", "_")
    # Try direct match, then normalized key
    if label in FILTER_LABELS:
        return FILTER_LABELS[label]
    if key in FILTER_LABELS:
        return FILTER_LABELS[key]
    # Try title case and other common variants
    if label.title() in FILTER_LABELS:
        return FILTER_LABELS[label.title()]
    return label
# dashboard_utils.py — Shared utilities for dashboards

import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from theme import register_template
import re
import textwrap
import math


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
    "Calendar Years",
    "Year",
    "Month",
    "County of Death",
    "County",
    "City",
    "Age Group",
    "Sex",
    "Sex at Birth",
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
        if _normalize_filter_label(label_text) == _normalize_filter_label("Custom Date Range"):
            rank = len(_FILTER_LABEL_RANK) + 1
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
    vals = [str(v).strip() for v in pd.Series(series).dropna().astype(str).unique().tolist()]
    vals = [v for v in vals if v]

    def _age_like_sort_key(text: str):
        s = str(text).strip()
        low = s.lower()

        if low == "unknown":
            return (4, float("inf"), float("inf"), s)

        under_match = re.fullmatch(r"under\s+(\d+)", s, flags=re.IGNORECASE)
        if under_match:
            n = int(under_match.group(1))
            return (0, n, n, s)

        lt_match = re.fullmatch(r"<\s*(\d+)", s)
        if lt_match:
            n = int(lt_match.group(1))
            return (0, n, n, s)

        range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            return (1, start, end, s)

        plus_match = re.fullmatch(r"(\d+)\s*\+", s)
        if plus_match:
            n = int(plus_match.group(1))
            return (2, n, n, s)

        return (3, float("inf"), float("inf"), low)

    has_age_like = any(
        re.fullmatch(r"under\s+\d+|<\s*\d+|\d+\s*-\s*\d+|\d+\s*\+", str(v).strip(), flags=re.IGNORECASE)
        for v in vals
    )

    if has_age_like:
        return sorted(vals, key=_age_like_sort_key)

    non_unknown_vals = [v for v in vals if v.lower() != "unknown"]
    is_year_like = bool(non_unknown_vals) and all(re.fullmatch(r"\d{4}", v) for v in non_unknown_vals)
    if is_year_like:
        sorted_years = sorted(non_unknown_vals, key=lambda x: int(x), reverse=True)
        has_unknown = any(v.lower() == "unknown" for v in vals)
        return sorted_years + (["Unknown"] if has_unknown else [])

    has_unknown = any(v.lower() == "unknown" for v in vals)
    middle = sorted(non_unknown_vals)
    return middle + (["Unknown"] if has_unknown else [])


def format_count_display(value, threshold: int = COUNT_SUPPRESSION_THRESHOLD, suppressed_label: str = SUPPRESSED_COUNT_LABEL) -> str:
    """
    Format a count for UI display with small-number suppression.

    Values where 0 <= value < threshold are shown as '<10*' by default.
    """
    if value is None or pd.isna(value):
        return suppressed_label

    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return str(value)

    if 0 <= numeric < threshold:
        return suppressed_label
    return f"{numeric:,}"


def build_suppressed_bar_count_columns(
    values,
    threshold: int = COUNT_SUPPRESSION_THRESHOLD,
    suppressed_label: str = SUPPRESSED_COUNT_LABEL,
    suppress_zero: bool = False,
):
    """
    Return plot/display values for bar charts that use count suppression.

    `plot_values` are zeroed when suppressed so short bars do not leak counts.
    `display_values` show the suppression label for suppressed counts.
    """
    numeric = pd.to_numeric(pd.Series(values), errors="coerce").fillna(0)

    if suppress_zero:
        suppressed_mask = (numeric >= 0) & (numeric < threshold)
    else:
        suppressed_mask = (numeric > 0) & (numeric < threshold)

    plot_values = numeric.where(~suppressed_mask, 0)
    display_values = [
        suppressed_label if is_suppressed else format_count_display(v, threshold, suppressed_label)
        for v, is_suppressed in zip(numeric, suppressed_mask)
    ]
    return plot_values, pd.Series(display_values, index=numeric.index), suppressed_mask


def apply_suppressed_horizontal_bar_display(
    fig,
    suppress_zero: bool = False,
    threshold: int = COUNT_SUPPRESSION_THRESHOLD,
    suppressed_label: str = SUPPRESSED_COUNT_LABEL,
    require_integer_like: bool = True,
    override_hovertemplate: bool = True,
):
    """
    Apply suppression-safe display for horizontal bar traces in a figure.

    This zeroes suppressed bar lengths (to avoid revealing small counts),
    displays suppression labels as bar text, and uses text-only hover.
    """
    for trace in fig.select_traces(selector={"type": "bar"}):
        if getattr(trace, "orientation", None) != "h":
            continue

        x_values = getattr(trace, "x", None)
        if x_values is None:
            continue

        plot_values, display_values, suppressed_mask = build_suppressed_bar_count_columns(
            x_values,
            threshold=threshold,
            suppressed_label=suppressed_label,
            suppress_zero=suppress_zero,
        )

        if require_integer_like:
            non_na = pd.to_numeric(pd.Series(x_values), errors="coerce").dropna()
            if non_na.empty:
                continue
            if ((non_na - non_na.round()).abs() > 1e-9).any():
                # Skip percentage-like or non-count traces.
                continue

        trace.x = plot_values.tolist()
        trace.text = display_values.tolist()
        if suppressed_mask.any():
            trace.textposition = "outside"
            if override_hovertemplate:
                trace.hovertemplate = "%{y}: %{text}<extra></extra>"
        trace.cliponaxis = False

    return fig


def format_percentage_display(
    value,
    count_value=None,
    count_display: str | None = None,
    decimals: int = 1,
    suppressed_output: str = "",
) -> str:
    """
    Format a percentage value while hiding it when the related count is suppressed.

    If `count_display` (or `count_value`) resolves to SUPPRESSED_COUNT_LABEL, return
    `suppressed_output` instead of a numeric percentage.
    """
    resolved_count_display = (
        count_display
        if count_display is not None
        else format_count_display(count_value)
    )

    if resolved_count_display == SUPPRESSED_COUNT_LABEL:
        return suppressed_output

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return suppressed_output

    if math.isnan(numeric) or math.isinf(numeric):
        return suppressed_output

    return f"{numeric:.{decimals}f}%"


def build_suppressed_percentage_columns(
    percentage_values,
    count_values=None,
    count_display_values=None,
    decimals: int = 1,
    suppressed_output: str = "",
    suppressed_plot_value: float = 0.0,
):
    """
    Build plotted/display percentage series that hide percentages when counts are suppressed.

    Returns:
      - plot_percentage_values: numeric values with suppressed rows zeroed (or overridden)
      - percentage_display_values: formatted percentage strings (or suppressed_output)
      - suppressed_mask: True where count suppression is active
    """
    percentage_numeric = pd.to_numeric(pd.Series(percentage_values), errors="coerce").fillna(0.0)

    if count_display_values is None:
        count_display_series = pd.Series(count_values).apply(format_count_display)
    else:
        count_display_series = pd.Series(count_display_values).astype(str)

    suppressed_mask = count_display_series == SUPPRESSED_COUNT_LABEL

    percentage_display_values = [
        format_percentage_display(
            pct,
            count_display=count_display,
            decimals=decimals,
            suppressed_output=suppressed_output,
        )
        for pct, count_display in zip(percentage_numeric, count_display_series)
    ]

    plot_percentage_values = percentage_numeric.where(~suppressed_mask, suppressed_plot_value)
    return plot_percentage_values, pd.Series(percentage_display_values, index=percentage_numeric.index), suppressed_mask


def wrap_axis_label(label: str, max_len: int = 45) -> str:
    """Wrap long categorical axis labels using HTML line breaks for Plotly."""
    if label is None:
        return ""
    wrapped = textwrap.wrap(str(label), width=max_len)
    return "<br>".join(wrapped) if wrapped else ""


def compute_adaptive_horizontal_bar_height(
    category_count: int,
    min_height: int | None = None,
    max_height: int | None = None,
    pixels_per_bar: int = 30,
    base_padding: int = 80,
) -> int:
    """
    Compute a chart height that keeps horizontal bar thickness readable.

    The height scales with category count. Optional min/max bounds can be applied
    by passing min_height/max_height.
    """
    safe_count = max(0, int(category_count or 0))
    estimated = base_padding + (safe_count * pixels_per_bar)

    if min_height is not None:
        estimated = max(int(min_height), estimated)
    if max_height is not None:
        estimated = min(int(max_height), estimated)
    return estimated


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


def build_summary_count_table(
    frame: pd.DataFrame,
    group_col: str,
    id_col: str = "record_id",
    categories=None,
    include_all_ordered: bool = False,
    include_statewide_county: bool = False,
    county_col: str = "county",
    header_labels: dict | None = None,
    count_label: str = "Discharges",
):
    """
    Build a standardized summary table of distinct counts for a grouping column.

    This helper centralizes category completion, statewide county aggregation,
    suppression-safe count formatting, and table rendering.
    """
    if frame is None or frame.empty or group_col not in frame.columns or id_col not in frame.columns:
        return dbc.Alert(f"Column '{group_col}' not found.", color="warning", className="mb-0")

    grouped = frame.groupby(group_col)[id_col].nunique().reset_index(name="count")

    if group_col == county_col and include_statewide_county:
        grouped = append_statewide_aggregate_rows(grouped, value_col="count", county_col=county_col)

    if group_col == county_col and categories is not None:
        categories = statewide_first(categories)
        if include_statewide_county and STATEWIDE_COUNTY not in categories:
            categories = [STATEWIDE_COUNTY] + list(categories)

    if categories is not None and include_all_ordered:
        # Ensure both group_col and categories are the same type (string) for merging
        full = pd.DataFrame({group_col: categories})
        # If group_col is year or types differ, cast both to string
        if group_col == "year" or full[group_col].dtype != grouped[group_col].dtype:
            full[group_col] = full[group_col].astype(str)
            grouped[group_col] = grouped[group_col].astype(str)
        grouped = full.merge(grouped, on=group_col, how="left")
        grouped["count"] = grouped["count"].fillna(0).astype(int)

    if group_col == "year":
        grouped = grouped.sort_values(group_col, ascending=False)
    elif categories is not None:
        grouped[group_col] = pd.Categorical(grouped[group_col], categories=categories, ordered=True)
        grouped = grouped.sort_values(group_col)
    else:
        grouped = grouped.sort_values("count", ascending=False)

    grouped["count"] = grouped["count"].map(format_count_display)

    labels = {
        "year": "Calendar Year",
        "age_group": "Age Group",
        "county": "County",
        "sex": "Sex at Birth",
        "race_ethnicity": "Race/Ethnicity",
        "hawaii_residency": "Hawaii Resident",
        "homeless": "Is Homeless",
        "discharges": "Discharges",
    }
    if header_labels:
        labels.update(header_labels)

    grouped = grouped.rename(columns={group_col: labels.get(group_col, group_col), "count": count_label})

    return dbc.Table.from_dataframe(grouped, striped=True, bordered=True, hover=True)


def graph_block(base_id: str, title_text: str, height_px: str | None = None):
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
                style=({"height": height_px, "width": "100%"} if height_px else {"width": "100%"}),
                config={"displayModeBar": True, "displaylogo": False},
            ),
        ],
        className="mb-4",
        # This makes sure the tools bar is never cut off visually.
        style={"overflow": "visible"}
    )


# Shared chart spacing defaults to keep all bar/line/map charts consistent site-wide.
STANDARD_CHART_MARGIN = {"l": 12, "r": 12, "t": 30, "b": 50}
STANDARD_BAR_MARGIN = STANDARD_CHART_MARGIN.copy()
STANDARD_LINE_MARGIN = STANDARD_CHART_MARGIN.copy()
STANDARD_MAP_MARGIN = STANDARD_CHART_MARGIN.copy()
STANDARD_NON_AXIS_MARGIN = {
    **STANDARD_CHART_MARGIN,
    "t": STANDARD_CHART_MARGIN["t"] + 20,
}


def apply_standard_bar_layout(
    fig,
    margin: dict | None = None,
    xaxis: dict | None = None,
    yaxis: dict | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for bar charts, with optional overrides."""
    explicit_height = layout_kwargs.get("height")
    if explicit_height is None:
        horizontal_bar_units = 0
        for trace in getattr(fig, "data", []):
            if getattr(trace, "type", None) != "bar" or getattr(trace, "orientation", None) != "h":
                continue
            trace_y = getattr(trace, "y", None)
            if trace_y is None:
                continue
            label_units = sum(str(label).count("<br>") + 1 for label in trace_y)
            horizontal_bar_units = max(horizontal_bar_units, label_units)

        if horizontal_bar_units:
            layout_kwargs["height"] = compute_adaptive_horizontal_bar_height(
                horizontal_bar_units,
            )

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

    # Use "auto" so labels move outside when bars are too short to show text inside.
    fig.update_traces(
        textposition="auto",
        cliponaxis=False,
        selector={"type": "bar"},
    )

    # Re-apply suppression display after layout-level textposition updates.
    apply_suppressed_horizontal_bar_display(
        fig,
        suppress_zero=True,
        require_integer_like=True,
        override_hovertemplate=False,
    )

    # Keep suppression labels visible when a chart intentionally zeroes suppressed bars.
    # We only force outside placement for labels that contain the suppression token.
    for trace in fig.select_traces(selector={"type": "bar"}):
        text_values = getattr(trace, "text", None)
        if text_values is None or isinstance(text_values, str):
            continue

        text_list = ["" if v is None else str(v) for v in text_values]
        if not any(SUPPRESSED_COUNT_LABEL in value for value in text_list):
            continue

        trace.textposition = [
            "outside" if SUPPRESSED_COUNT_LABEL in value else "auto"
            for value in text_list
        ]
        trace.cliponaxis = False

    return fig

def apply_standard_single_series_bar_trace(
    fig,
    hovertemplate: str = "%{y}: %{x:,}<extra></extra>",
    marker_color: str = "#22767C",
    texttemplate: str = "%{text}",
    textposition: str = "auto",
    textangle: int = 0,
    cliponaxis: bool = False,
    apply_count_suppression: bool = True,
    suppress_zero_counts: bool = True,
    **trace_kwargs,
):
    """Apply standard trace styling for single-series bar charts."""
    if texttemplate == "%{text}":
        # Centralize numeric label formatting so dashboards don't need per-chart comma logic.
        for trace in fig.select_traces(selector={"type": "bar"}):
            text_values = getattr(trace, "text", None)
            if text_values is None or isinstance(text_values, str):
                continue

            text_series = pd.Series(list(text_values))
            if text_series.empty:
                continue

            numeric_series = pd.to_numeric(text_series, errors="coerce")
            if numeric_series.isna().any():
                # Keep preformatted or categorical labels (e.g., '<10*') unchanged.
                continue

            formatted_text = [
                (f"{int(v):,}" if float(v).is_integer() else f"{float(v):,.2f}".rstrip("0").rstrip("."))
                for v in numeric_series
            ]
            trace.text = formatted_text

    fig.update_traces(
        marker_color=marker_color,
        texttemplate=texttemplate,
        textposition=textposition,
        textangle=textangle,
        cliponaxis=cliponaxis,
        hovertemplate=hovertemplate,
        selector={"type": "bar"},
        **trace_kwargs,
    )

    if apply_count_suppression:
        apply_suppressed_horizontal_bar_display(
            fig,
            suppress_zero=suppress_zero_counts,
            require_integer_like=True,
            # Keep custom hovers for charts that intentionally define richer tooltips.
            override_hovertemplate=(hovertemplate == "%{y}: %{x:,}<extra></extra>"),
        )
    return fig


def add_stacked_bar_total_labels(
    fig,
    totals_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    formatter=format_count_display,
):
    """Add readable top-of-stack labels for stacked bars, thinning when categories are dense."""
    if fig is None or totals_df is None or totals_df.empty:
        return fig

    required = {x_col, y_col}
    if not required.issubset(totals_df.columns):
        return fig

    totals = totals_df[[x_col, y_col]].copy()
    totals[y_col] = pd.to_numeric(totals[y_col], errors="coerce").fillna(0)
    totals = totals[totals[y_col] >= 0].copy()
    if totals.empty:
        return fig

    totals = totals.reset_index(drop=True)
    n_labels = len(totals)

    # Keep labels legible on dense category axes by showing every Nth total.
    if n_labels <= 12:
        step = 1
    elif n_labels <= 24:
        step = 2
    else:
        step = max(3, math.ceil(n_labels / 12))

    font_size = 12 if step == 1 else 11 if step == 2 else 10
    for idx, row in totals.iterrows():
        if idx % step != 0:
            continue

        fig.add_annotation(
            x=row[x_col],
            y=row[y_col],
            text=formatter(row[y_col]) if formatter else str(row[y_col]),
            showarrow=False,
            yshift=10 + (6 if (step > 1 and idx % 2) else 0),
            xshift=((8 if idx % 2 == 0 else -8) if step > 1 else 0),
            font=dict(size=font_size),
            bgcolor="rgba(255,255,255,0.80)",
            borderpad=1,
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
    layout_kwargs.setdefault("title", None)
    layout_kwargs.setdefault("legend_title_text", None)

    merged_margin = STANDARD_LINE_MARGIN.copy()
    if margin:
        merged_margin.update(margin)

    merged_xaxis = {"automargin": True, "dtick": 1}
    if xaxis:
        merged_xaxis.update(xaxis)

    merged_yaxis = {"automargin": True, "rangemode": "tozero"}
    if yaxis:
        merged_yaxis.update(yaxis)

    explicit_legend = layout_kwargs.pop("legend", None)
    merged_legend = {
        "orientation": "h",
        "yanchor": "top",      # Flipped from "bottom" so it builds downward
        "y": -0.15,            # Moved much closer to the 0 line
        "xanchor": "left",
        "x": 0,
        "bgcolor": "rgba(0,0,0,0)",
    }

    # Keep semantic legend settings (e.g., title) but enforce shared position/background.
    if explicit_legend:
        for key in ("title", "title_text", "font", "itemsizing", "itemwidth", "traceorder"):
            if key in explicit_legend:
                merged_legend[key] = explicit_legend[key]

    fig.update_layout(
        margin=merged_margin,
        xaxis=merged_xaxis,
        yaxis=merged_yaxis,
        legend=merged_legend,
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


def apply_standard_heatmap_layout(
    fig,
    **layout_kwargs,
):
    """Apply standardized layout defaults for heatmaps."""
    return apply_standard_non_axis_layout(fig, **layout_kwargs)


def apply_standard_network_layout(
    fig,
    node_count: int | None = None,
    **layout_kwargs,
):
    """Apply standardized layout defaults for network charts with adaptive height/margins."""
    # Keep backward compatibility with older callsites that don't pass node_count.
    safe_node_count = int(node_count) if node_count is not None else 6
    # Keep enough room for labels while avoiding excessive empty space below the plot.
    network_height = min(820, max(620, 520 + safe_node_count * 16))
    return apply_standard_non_axis_layout(
        fig,
        margin={"b": 20},
        height=network_height,
        **layout_kwargs,
    )


def apply_standard_sankey_layout(
    fig,
    node_count: int,
    **layout_kwargs,
):
    """Apply standardized layout defaults for Sankey charts with adaptive height/margins."""
    sankey_height = max(860, 680 + int(node_count) * 40)
    # Sankey labels and lower links need extra room beyond standard chart spacing.
    sankey_bottom_margin = max(140, int(sankey_height * 0.15))
    return apply_standard_non_axis_layout(
        fig,
        margin={"b": sankey_bottom_margin},
        height=sankey_height,
        **layout_kwargs,
    )


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

    Automatically applies get_standard_filter_label to the label argument.
    If persistence is not provided, defaults to the control id.
    """
    from dashboard_utils import get_standard_filter_label
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return get_standard_filter_label(label), dcc.Dropdown(id=control_id, **kwargs)


def checklist_filter(label: str, control_id: str, **kwargs):
    """Convenience builder for checklist filters used by make_filters_card. Automatically applies get_standard_filter_label to the label argument."""
    from dashboard_utils import get_standard_filter_label
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return get_standard_filter_label(label), dcc.Checklist(id=control_id, **kwargs)


def radio_filter(label: str, control_id: str, **kwargs):
    """Convenience builder for radio-item filters used by make_filters_card. Automatically applies get_standard_filter_label to the label argument."""
    from dashboard_utils import get_standard_filter_label
    kwargs.setdefault("persistence", control_id)
    kwargs.setdefault("persistence_type", "session")
    return get_standard_filter_label(label), dcc.RadioItems(id=control_id, **kwargs)
