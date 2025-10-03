"""Multi-line line chart component"""

import streamlit as st
import altair as alt


def render_multi_line_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(
        alt.Chart(config['df'])
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
            y=alt.Y(f"{config['y_field']}:Q",
                    title=config['y_label'], axis=alt.Axis(format=",.0f")),
            color=alt.Color(f"{config['category_field']}:N", title="series"),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
                alt.Tooltip(f"{config['category_field']}:N", title="series"),
                alt.Tooltip(f"{config['y_field']}:Q",
                            title=config['y_label'], format=","),
            ],
        )
        .properties(height=340),
        use_container_width=True,
    )
