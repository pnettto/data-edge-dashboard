"""Table component."""

import streamlit as st


def render_table(config):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.dataframe(
        config['df'],
        use_container_width=True,
        height=400,
        hide_index=config.get('hide_index', True),
    )