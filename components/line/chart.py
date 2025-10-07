"""Chart building for line charts"""

import pandas as pd
import altair as alt


def build_chart(plot_df: pd.DataFrame, config: dict) -> alt.Chart:
    """Build Altair chart based on configuration."""
    has_forecast = config.get('forecast', False) and "type" in plot_df.columns
    has_categories = config.get('category_field') is not None
    
    if has_forecast and has_categories:
        return _build_multi_forecast(plot_df, config)
    elif has_forecast:
        return _build_single_forecast(plot_df, config)
    elif has_categories:
        return _build_multi_line(plot_df, config)
    else:
        return _build_single_line(plot_df, config)


def _get_base_encoding(config: dict, include_type: bool = False, include_category: bool = False) -> dict:
    """Get common encoding configuration."""
    category_label = config.get('category_label') or config.get('category_field', '')
    
    tooltip = [
        alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
        alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
    ]
    
    if include_category and config.get('category_field'):
        tooltip.append(alt.Tooltip(f"{config['category_field']}:N", title=category_label))
    
    if include_type:
        tooltip.append(alt.Tooltip("type:N", title="Type"))
    
    encoding = {
        'x': alt.X(f"{config['x_field']}:T", title=config['x_label']),
        'y': alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        'tooltip': tooltip,
    }
    
    if include_category and config.get('category_field'):
        encoding['color'] = alt.Color(
            f"{config['category_field']}:N", 
            legend=alt.Legend(title=category_label)
        )
    
    return encoding


def _build_single_line(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single line chart without forecast."""
    encoding = _get_base_encoding(config)
    
    return alt.Chart(df).mark_line(
        point=True, 
        color="#0b7dcfff"
    ).encode(**encoding).properties(height=340)


def _build_multi_line(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-line chart without forecast."""
    encoding = _get_base_encoding(config, include_category=True)
    
    line_chart = alt.Chart(df).mark_line(
        point=True
    ).encode(**encoding)

    if 'category_area_highlight' in config:
        highlight_cats = config['category_area_highlight']
        if len(highlight_cats) == 2:
            area_chart = _build_diff_area(df, config, highlight_cats, forecast=False)
            if area_chart is not None:
                # Independent color scales: area uses diff sign, lines use categories
                return (area_chart + line_chart).resolve_scale(color='independent').properties(height=340)

    return line_chart.properties(height=340)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single line chart with forecast."""
    base = alt.Chart(df)
    encoding = _get_base_encoding(config, include_type=True)
    
    # Actual line (solid)
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=True, color="#0b7dcfff").encode(**encoding)
    
    # Forecast line (dashed)
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=True, color="#0b7dcfff", strokeDash=[5, 5]).encode(**encoding)
    
    # Connector line (dashed, no points, minimal encoding)
    connector = base.transform_filter(
        alt.datum.type == "Connector"
    ).mark_line(point=False, color="#0b7dcfff", strokeDash=[5, 5]).encode(
        x=alt.X(f"{config['x_field']}:T"),
        y=alt.Y(f"{config['y_field']}:Q"),
    )
    
    return (actual + forecast + connector).properties(height=340)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-line chart with forecast."""
    base = alt.Chart(df)
    encoding = _get_base_encoding(config, include_type=True, include_category=True)
    
    # Actual lines (solid, color-coded)
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=True).encode(**encoding)
    
    # Forecast lines (dashed, color-coded)
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=True, strokeDash=[5, 5]).encode(**encoding)
    
    # Connector lines (dashed, color-coded, no points, minimal encoding)
    category_label = config.get('category_label') or config['category_field']
    connector = base.transform_filter(
        alt.datum.type == "Connector"
    ).mark_line(point=False, strokeDash=[5, 5]).encode(
        x=alt.X(f"{config['x_field']}:T"),
        y=alt.Y(f"{config['y_field']}:Q"),
        color=alt.Color(
            f"{config['category_field']}:N", 
            legend=alt.Legend(title=category_label)
        ),
    )
    
    chart = (actual + forecast + connector)

    if 'category_area_highlight' in config:
        highlight_cats = config['category_area_highlight']
        if len(highlight_cats) == 2:
            # Differential area only over Actual segment for clarity
            area_chart = _build_diff_area(df, config, highlight_cats, forecast=True)
            if area_chart is not None:
                chart = (area_chart + chart).resolve_scale(color='independent')

    return chart.properties(height=340)


def _build_diff_area(df: pd.DataFrame, config: dict, highlight_cats, forecast: bool = False) -> alt.Chart:
    """
    Build a differential area (green when first > second, red otherwise) between two categories.
    The first category in highlight_cats is treated as the baseline.
    """
    category_field = config['category_field']
    x_field = config['x_field']
    y_field = config['y_field']
    baseline, other = highlight_cats

    base_df = df.copy()
    if forecast and "type" in base_df.columns:
        # Shade only the actual (historical) segment to avoid duplicated forecast overlays
        base_df = base_df[base_df['type'] == "Actual"]

    # Keep only the two categories we care about
    base_df = base_df[base_df[category_field].isin(highlight_cats)]

    # Pivot so each category is a column; require both present (dropna)
    pivot_df = (
        base_df
        .pivot(index=x_field, columns=category_field, values=y_field)
        .dropna()
        .reset_index()
    )
    if pivot_df.empty:
        return None  # Nothing to shade

    # Compute difference and segment groups where sign changes
    pivot_df['diff'] = pivot_df[baseline] - pivot_df[other]
    pivot_df['is_positive'] = pivot_df['diff'] >= 0
    pivot_df['group_id'] = (pivot_df['is_positive'] != pivot_df['is_positive'].shift()).cumsum()

    # Upper / lower bounds for the filled area
    pivot_df['upper'] = pivot_df[[baseline, other]].max(axis=1)
    pivot_df['lower'] = pivot_df[[baseline, other]].min(axis=1)

    # Build area chart with segmented groups (detail) and color by sign
    area = alt.Chart(pivot_df).mark_area().encode(
        x=f"{x_field}:T",
        y="upper:Q",
        y2="lower:Q",
        detail="group_id:N",
        color=alt.Color(
            "is_positive:N",
            scale=alt.Scale(domain=[True, False], range=["#2e7d3280", "#c6282880"]),
            legend=None
        ),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{baseline}:Q", title=baseline, format=","),
            alt.Tooltip(f"{other}:Q", title=other, format=","),
            alt.Tooltip("is_positive:N", title=f"{baseline} above {other}?")
        ]
    )
    return area