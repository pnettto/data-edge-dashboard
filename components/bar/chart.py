"""Chart building for bar charts"""

import pandas as pd
import altair as alt

# Bar chart styling
BAR_COLOR_SCHEME = "tableau20"
BAR_SINGLE_COLOR = "#0b7dcfff"
BAR_FORECAST_OPACITY = 0.5
BAR_CORNER_RADIUS = 4  # Rounded corners for smoother appearance

# Trendline styling
TRENDLINE_COLOR = "#ffd600ff"
TRENDLINE_DASH = [5, 5]
TRENDLINE_WIDTH = 3
TRENDLINE_OPACITY = 0.8

# Reference line styling
REFERENCE_LINE_COLOR = "#FF6B6B"
REFERENCE_LINE_DASH = [8, 4]
REFERENCE_LINE_WIDTH = 2

# Chart dimensions
CHART_HEIGHT = 400

# Tooltip formatting
TOOLTIP_NUMBER_FORMAT = ","
TOOLTIP_AXIS_FORMAT = ",.0f"

# Add: axis label truncation control (0 disables truncation)
AXIS_LABEL_LIMIT = 0  # Disable truncation by default (overridable via config['axis_label_limit'])


def _build_axis(fmt=None, limit=AXIS_LABEL_LIMIT, rotate=False, axis_type='x'):
    """Helper to build Altair Axis.
    For x-axis:
        rotate=False -> vertical labels (angle -90)
        rotate=True  -> horizontal labels (angle 0)
    Y-axis labels are left unchanged (no angle set).
    """
    args = {}
    if fmt is not None:
        args['format'] = fmt
    if limit is not None:
        args['labelLimit'] = limit
    if axis_type == 'x':
        args['labelAngle'] = 0 if rotate else -90
    return alt.Axis(**args)


def _get_x_encoding_type(df: pd.DataFrame, x_field: str) -> str:
    """Determine the appropriate Altair encoding type for x-axis."""
    if pd.api.types.is_datetime64_any_dtype(df[x_field]):
        return "T"  # Temporal
    elif pd.api.types.is_numeric_dtype(df[x_field]):
        return "Q"  # Quantitative
    else:
        return "N"  # Nominal


def _is_time_or_sequential(df: pd.DataFrame, x_field: str) -> bool:
    """Check if x-axis data should be treated as time-series or sequential (not categorical)."""
    # Check if it's datetime
    if pd.api.types.is_datetime64_any_dtype(df[x_field]):
        return True
    
    # Check if it's numeric
    if pd.api.types.is_numeric_dtype(df[x_field]):
        return True
    
    # Check if string values look like dates
    if df[x_field].dtype == object:
        sample = df[x_field].dropna().astype(str).head(5)
        for val in sample:
            # Check for common date patterns
            if any(pattern in val for pattern in ['-', '/', 'Q', '20', '19']):
                # Try to parse as date
                try:
                    pd.to_datetime(val)
                    return True
                except:
                    pass
    
    return False


def build_chart(plot_df: pd.DataFrame, config: dict) -> alt.Chart:
    """Build Altair bar chart based on configuration."""
    has_forecast = config.get('forecast', False) and "type" in plot_df.columns
    has_categories = config.get('category_field') is not None
    
    if has_forecast and has_categories:
        chart = _build_multi_forecast(plot_df, config)
    elif has_forecast:
        chart = _build_single_forecast(plot_df, config)
    elif has_categories:
        chart = _build_multi_bar(plot_df, config)
    else:
        chart = _build_single_bar(plot_df, config)
    
    # Add reference line if configured
    if config.get('reference_line'):
        ref_line = _build_reference_line(plot_df, config)
        if ref_line:
            chart = chart + ref_line
    
    return chart


def _build_single_bar(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single bar chart without forecast."""
    x_type = _get_x_encoding_type(df, config['x_field'])
    orientation = config.get('orientation', 'vertical')
    
    # Use color scheme only for truly categorical data (not time-series or sequential)
    is_categorical_only = not _is_time_or_sequential(df, config['x_field'])
    
    color_encoding = alt.Color(
        f"{config['x_field']}:N",
        scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
        legend=None
    ) if is_categorical_only else None
    
    label_limit = config.get('axis_label_limit', AXIS_LABEL_LIMIT)
    rotate = config.get('rotate_labels', False)
    
    if orientation == 'horizontal':
        encoding = {
            'x': alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            'y': alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            'tooltip': [
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            ]
        }
        if color_encoding:
            encoding['color'] = color_encoding
            bars = alt.Chart(df).mark_bar(cornerRadiusEnd=BAR_CORNER_RADIUS).encode(**encoding)
        else:
            bars = alt.Chart(df).mark_bar(color=BAR_SINGLE_COLOR, cornerRadiusEnd=BAR_CORNER_RADIUS).encode(**encoding)
    else:
        encoding = {
            'x': alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            'y': alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            'tooltip': [
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            ]
        }
        if color_encoding:
            encoding['color'] = color_encoding
            bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS).encode(**encoding)
        else:
            bars = alt.Chart(df).mark_bar(color=BAR_SINGLE_COLOR, cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS).encode(**encoding)
    
    chart = bars
    
    # Add trendline if requested (only for vertical orientation)
    if config.get('trendline', False) and orientation == 'vertical':
        trendline = _create_trendline(df, config, x_type)
        chart = bars + trendline
    
    return chart.properties(height=CHART_HEIGHT)


def _create_trendline(df: pd.DataFrame, config: dict, x_type: str) -> alt.Chart:
    """Create a trendline layer using linear regression."""
    import numpy as np
    
    # Prepare data for regression
    df_sorted = df.sort_values(by=config['x_field']).reset_index(drop=True)
    x_numeric = np.arange(len(df_sorted))
    y_values = df_sorted[config['y_field']].values
    
    # Calculate linear regression
    coefficients = np.polyfit(x_numeric, y_values, 1)
    slope, intercept = coefficients[0], coefficients[1]
    
    # Create trendline points at start and end
    trendline_data = pd.DataFrame({
        config['x_field']: [df_sorted[config['x_field']].iloc[0], df_sorted[config['x_field']].iloc[-1]],
        config['y_field']: [intercept, slope * (len(df_sorted) - 1) + intercept]
    })
    
    return alt.Chart(trendline_data).mark_line(
        color=TRENDLINE_COLOR,
        strokeDash=TRENDLINE_DASH,
        size=TRENDLINE_WIDTH,
        opacity=TRENDLINE_OPACITY
    ).encode(
        x=alt.X(f"{config['x_field']}:{x_type}"),
        y=alt.Y(f"{config['y_field']}:Q")
    )


def _build_multi_bar(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart without forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    orientation = config.get('orientation', 'vertical')
    
    label_limit = config.get('axis_label_limit', AXIS_LABEL_LIMIT)
    rotate = config.get('rotate_labels', False)
    
    if orientation == 'horizontal':
        return alt.Chart(df).mark_bar(cornerRadiusEnd=BAR_CORNER_RADIUS).encode(
            x=alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=alt.Legend(title=category_label)
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            ]
        ).properties(height=CHART_HEIGHT)
    else:
        return alt.Chart(df).mark_bar(cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS).encode(
            x=alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=alt.Legend(title=category_label)
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            ]
        ).properties(height=CHART_HEIGHT)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single bar chart with forecast."""
    x_type = _get_x_encoding_type(df, config['x_field'])
    orientation = config.get('orientation', 'vertical')
    base = alt.Chart(df)
    
    label_limit = config.get('axis_label_limit', AXIS_LABEL_LIMIT)
    rotate = config.get('rotate_labels', False)
    
    if orientation == 'horizontal':
        actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(
            color=BAR_SINGLE_COLOR, cornerRadiusEnd=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
        
        forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(
            color=BAR_SINGLE_COLOR, opacity=BAR_FORECAST_OPACITY, cornerRadiusEnd=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
    else:
        actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(
            color=BAR_SINGLE_COLOR, cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
        
        forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(
            color=BAR_SINGLE_COLOR, opacity=BAR_FORECAST_OPACITY, cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
    
    return (actual + forecast).properties(height=CHART_HEIGHT)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart with forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    orientation = config.get('orientation', 'vertical')
    base = alt.Chart(df)
    
    label_limit = config.get('axis_label_limit', AXIS_LABEL_LIMIT)
    rotate = config.get('rotate_labels', False)
    
    if orientation == 'horizontal':
        actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(
            cornerRadiusEnd=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=alt.Legend(title=category_label)
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
        
        forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(
            opacity=BAR_FORECAST_OPACITY, cornerRadiusEnd=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=None
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
    else:
        actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(
            cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=alt.Legend(title=category_label)
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
        
        forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(
            opacity=BAR_FORECAST_OPACITY, cornerRadiusTopLeft=BAR_CORNER_RADIUS, cornerRadiusTopRight=BAR_CORNER_RADIUS
        ).encode(
            x=alt.X(
                f"{config['x_field']}:{x_type}",
                title=config['x_label'],
                axis=_build_axis(limit=label_limit, rotate=rotate, axis_type='x')
            ),
            y=alt.Y(
                f"{config['y_field']}:Q",
                title=config['y_label'],
                axis=_build_axis(fmt=TOOLTIP_AXIS_FORMAT, limit=label_limit, rotate=False, axis_type='y')
            ),
            color=alt.Color(
                f"{config['category_field']}:N",
                scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
                legend=None
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
                alt.Tooltip(f"{config['category_field']}:N", title=category_label),
                alt.Tooltip("type:N", title="Type"),
            ]
        )
    
    return (actual + forecast).properties(height=CHART_HEIGHT)


def _build_reference_line(df: pd.DataFrame, config: dict) -> alt.Chart:
    """
    Build a reference line (horizontal or vertical dashed line).
    
    Args:
        df: DataFrame (used for domain inference)
        config: Chart configuration with 'reference_line' as tuple (axis, value, label?)
               where axis is 'x' or 'y', value is the reference value, and label is optional
    
    Returns:
        Altair Chart with reference line or None if invalid configuration
    """
    reference_line = config.get('reference_line')
    if not reference_line or len(reference_line) < 2:
        return None
    
    axis = reference_line[0]
    value = reference_line[1]
    label = reference_line[2] if len(reference_line) > 2 else "Target"
    orientation = config.get('orientation', 'vertical')
    
    if axis.lower() == 'y':
        # Horizontal reference line
        ref_df = pd.DataFrame({config['y_field']: [value]})
        return alt.Chart(ref_df).mark_rule(
            strokeDash=REFERENCE_LINE_DASH,
            color=REFERENCE_LINE_COLOR,
            strokeWidth=REFERENCE_LINE_WIDTH
        ).encode(
            y=alt.Y(f"{config['y_field']}:Q"),
            tooltip=[alt.Tooltip(f"{config['y_field']}:Q", title=label, format=TOOLTIP_NUMBER_FORMAT)]
        )
    
    elif axis.lower() == 'x':
        # Vertical reference line
        x_field = config['x_field']
        x_type = _get_x_encoding_type(df, x_field)
        
        # Handle datetime conversion if needed
        x_value = value
        if pd.api.types.is_datetime64_any_dtype(df[x_field]):
            if not isinstance(value, pd.Timestamp):
                x_value = pd.to_datetime(value)
            ref_df = pd.DataFrame({x_field: [x_value]})
            return alt.Chart(ref_df).mark_rule(
                strokeDash=REFERENCE_LINE_DASH,
                color=REFERENCE_LINE_COLOR,
                strokeWidth=REFERENCE_LINE_WIDTH
            ).encode(
                x=alt.X(f"{x_field}:T"),
                tooltip=[alt.Tooltip(f"{x_field}:T", title=label)]
            )
        else:
            ref_df = pd.DataFrame({x_field: [x_value]})
            return alt.Chart(ref_df).mark_rule(
                strokeDash=REFERENCE_LINE_DASH,
                color=REFERENCE_LINE_COLOR,
                strokeWidth=REFERENCE_LINE_WIDTH
            ).encode(
                x=alt.X(f"{x_field}:{x_type}"),
                tooltip=[alt.Tooltip(f"{x_field}:{x_type}", title=label)]
            )
    
    return None
