"""Bar chart component"""

import streamlit as st
import altair as alt


def render_bar_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(
        alt.Chart(config['df'])
        .mark_bar()
        .encode(
            x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
            y=alt.Y(f"{config['y_field']}:Q",
                    title=config['y_label'], axis=alt.Axis(format=",")),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q",
                            title=config['y_label'], format=","),
            ],
        )
        .properties(height=340),
        use_container_width=True,
    )
