"""Chart building logic for stacked area charts"""

import altair as alt
import pandas as pd


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
        ),
        opacity=alt.condition(
            alt.datum.type == 'Forecast',
            alt.value(0.5),
            alt.value(1.0)
        )
    )

    # Stacked area chart
    area = base.mark_area().encode(
        strokeDash=alt.condition(
            alt.datum.type == 'Connector',
            alt.value([5, 5]),
            alt.value([0])
        )
    )

    # Combine layers
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

    return chart.properties(height=400).interactive()
