"""Markdown component."""

import streamlit as st


def render_markdown(config):
    st.subheader(config['title'])
    st.markdown(config['content'])