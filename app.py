import streamlit as st
from src.model import source_data
from src.ui import explorer


def run():
    """Main streamlit app entry point"""
    # Fetch source data - do this before auth to ensure all requests to app cause data refresh
    # Read, parse, and cache (via @st.cache_data) source data
    with st.spinner("Initializing..."):
        src_data = source_data.from_s3()

    # Show the main page
    explorer.st_page(src_data)


def clear_cache():
    """
    Clear Streamlit cache so source_data module will reread DB from disk on next request
    """
    st.cache_data.clear()
    return st.markdown(
        'Cache cleared. <a href="/" target="_self">Return to dashboard.</a>',
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="PRH Panel Explorer", layout="wide", initial_sidebar_state="auto"
)
run()
