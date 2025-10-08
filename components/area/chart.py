"""Chart building logic for stacked area charts"""

import altair as alt
import pandas as pd


# Area chart styling
AREA_COLOR_SCHEME = "tableau20"
AREA_SINGLE_COLOR = "#0b7dcfff"
AREA_OPACITY = 0.7
AREA_INTERPOLATE = "monotone"  # Makes area edges smoother and more rounded


def build_chart(df: pd.DataFrame, config: dict) -> alt.Chart:
    """
    Build a stacked area chart using Altair.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        config (dict): Configuration dictionary with chart settings.

    Returns:
        alt.Chart: The configured Altair chart object.
    """
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config['category_field']
    
    x_label = config.get('x_label', x_field)
    y_label = config.get('y_label', y_field)
    category_label = config.get('category_label', category_field)

    # Base chart
    base = alt.Chart(df).encode(
        x=alt.X(f'{x_field}:T', title=x_label),
        y=alt.Y(f'{y_field}:Q', title=y_label),
        color=alt.Color(
            f'{category_field}:N',
            title=category_label,
            scale=alt.Scale(scheme='tableau20'),
            legend=alt.Legend(orient='bottom')
        )
    )

    # Stacked area chart
    area = base.mark_area(
        opacity=AREA_OPACITY,
        interpolate=AREA_INTERPOLATE
    )

    # Start with area chart
    chart = area

    # Add reference line if specified
    if 'reference_line' in config:
        axis, value, label = config['reference_line']
        
        if axis == 'y':
            ref_line = alt.Chart(pd.DataFrame({'y': [value]})).mark_rule(
                strokeDash=[5, 5],
                color='gray'
            ).encode(
                y='y:Q',
                tooltip=[alt.Tooltip('y:Q', title=label)]
            )
        else:  # axis == 'x'
            ref_line = alt.Chart(pd.DataFrame({'x': [value]})).mark_rule(
                strokeDash=[5, 5],
                color='gray'
            ).encode(
                x=alt.X('x:T', title=x_label),
                tooltip=[alt.Tooltip('x:T', title=label)]
            )
        
        chart = chart + ref_line

    return chart.properties(height=400)


def _build_single_area(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single area chart without forecast."""
    encoding = _get_base_encoding(config)
    
    area = alt.Chart(df).mark_area(
        color=AREA_SINGLE_COLOR,
        opacity=AREA_OPACITY,
        interpolate=AREA_INTERPOLATE
    ).encode(**encoding)
    
    return area.properties(height=CHART_HEIGHT)


def _build_multi_area(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-area (stacked) chart without forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    
    return alt.Chart(df).mark_area(
        opacity=AREA_OPACITY,
        interpolate=AREA_INTERPOLATE
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=AREA_COLOR_SCHEME),
            legend=alt.Legend(title=category_label)
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
        ]
    ).properties(height=CHART_HEIGHT)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single area chart with forecast."""
    base = alt.Chart(df)
    encoding = _get_base_encoding(config, include_type=True)
    
    # Actual area (solid)
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_area(
        color=AREA_SINGLE_COLOR,
        opacity=AREA_OPACITY,
        interpolate=AREA_INTERPOLATE
    ).encode(**encoding)
    
    # Forecast area (lighter)
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_area(
        color=AREA_SINGLE_COLOR,
        opacity=AREA_OPACITY * 0.5,
        interpolate=AREA_INTERPOLATE
    ).encode(**encoding)
    
    return (actual + forecast).properties(height=CHART_HEIGHT)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-area (stacked) chart with forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    base = alt.Chart(df)
    
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_area(
        opacity=AREA_OPACITY,
        interpolate=AREA_INTERPOLATE
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=AREA_COLOR_SCHEME),
            legend=alt.Legend(title=category_label)
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_area(
        opacity=AREA_OPACITY * 0.5,
        interpolate=AREA_INTERPOLATE
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=AREA_COLOR_SCHEME),
            legend=None
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    return (actual + forecast).properties(height=CHART_HEIGHT)
