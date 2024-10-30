import streamlit as st


def run():
    """Main streamlit app entry point"""
    pass


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
    page_title="PRH Dashboard", layout="wide", initial_sidebar_state="auto"
)
run()
