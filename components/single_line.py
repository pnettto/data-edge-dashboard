"""Single line chart component"""

import streamlit as st
import altair as alt
import pandas as pd

def render_single_line_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])

    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']

    chart = alt.Chart(df).mark_line(point=True, color="#1f77b4").encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
        ],
    ).properties(height=340)

    st.altair_chart(chart, use_container_width=True)