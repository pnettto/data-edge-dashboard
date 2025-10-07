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
            area_df = df[df[config['category_field']].isin(highlight_cats)]
            area_df = area_df.pivot(
                index=config['x_field'], 
                columns=config['category_field'], 
                values=config['y_field']
            ).reset_index()

            area_chart = alt.Chart(area_df).mark_area(
                opacity=0.3,
                color='lightgray'
            ).encode(
                x=f"{config['x_field']}:T",
                y=f"{highlight_cats[0]}:Q",
                y2=f"{highlight_cats[1]}:Q"
            )
            return (area_chart + line_chart).properties(height=340)

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
            area_df = df[df[config['category_field']].isin(highlight_cats)]
            area_df = area_df.pivot_table(
                index=[config['x_field'], 'type'],
                columns=config['category_field'],
                values=config['y_field']
            ).reset_index()

            area_chart = alt.Chart(area_df).mark_area(
                opacity=0.3,
                color='lightgray'
            ).encode(
                x=f"{config['x_field']}:T",
                y=f"{highlight_cats[0]}:Q",
                y2=f"{highlight_cats[1]}:Q"
            )
            chart = area_chart + chart

    return chart.properties(height=340)