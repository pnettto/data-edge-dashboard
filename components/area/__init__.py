"""Stacked area chart component"""

import streamlit as st
import pandas as pd

from .chart import build_chart


def render_area_chart(config: dict) -> None:
    """
    Main entry point for rendering a stacked area chart.

    Args:
        config (dict): Dictionary containing chart configuration with the following keys:
            - title (str): Title of the chart.
            - description (str): Description or caption for the chart.
            - df (pd.DataFrame): DataFrame containing the data to plot.
            - x_field (str): Name of the column to use for the x-axis (should be datetime or convertible).
            - y_field (str): Name of the column to use for the y-axis.
            - category_field (str): Name of the column for categorical grouping (required for stacking).
            - category_label (str, optional): Title of the column for categorical grouping.
    """
    st.subheader(config['title'])
    st.caption(config['description'])

    actual_df = config['df'].copy()
    x_field = config['x_field']
    category_field = config.get('category_field')

    if not category_field:
        st.error("Stacked area chart requires a category_field for grouping")
        return

    # Convert x-axis to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(actual_df[x_field]):
        try:
            actual_df[x_field] = pd.to_datetime(actual_df[x_field])
        except (ValueError, TypeError):
            pass

    # Build and display chart
    chart = build_chart(actual_df, config)
    st.altair_chart(chart, use_container_width=True)


__all__ = ['render_area_chart']
