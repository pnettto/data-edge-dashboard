"""Image component."""

import streamlit as st


def render_image(config):
    border_radius = config.get('border_radius', '10px')
    
    st.markdown(
        f"""
        <style>
        .rounded-image img {{
            border-radius: {border_radius};
            width: 100%;
        }}
        </style>
        <div class="rounded-image">
        """,
        unsafe_allow_html=True
    )
    st.image(config['src'], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)