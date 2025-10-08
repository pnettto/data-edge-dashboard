"""Markdown component."""

import streamlit as st


def render_markdown(config):
    if 'title' in config and config['title']:
        st.subheader(config['title'])
    st.markdown(config['content'])