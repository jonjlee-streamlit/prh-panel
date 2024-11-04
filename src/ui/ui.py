import streamlit as st
from ..model import source_data


def show_settings(src_data: source_data.SourceData) -> dict:
    """
    Render the sidebar and return the dict with configuration options set by the user.
    """
    with st.sidebar:
        st_sidebar_prh_logo()
        st.write("## Clinic")
        clinic = st.selectbox(
            "",
            options=[
                "All",
                "Pullman Family Medicine",
                "Residency",
                "Palouse Pediatrics",
                "Palouse Medical",
            ],
            label_visibility="collapsed",
        )

    return {"clinic": clinic}


def st_sidebar_prh_logo():
    """
    Add PRH Logo to side bar - https://discuss.streamlit.io/t/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-multipage-app/28213/5
    """
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-image: url(https://www.pullmanregional.org/hubfs/PullmanRegionalHospital_December2019/Image/logo.svg);
                background-repeat: no-repeat;
                padding-top: 0px;
                background-position: 55px 20px;
            }
            .element-container iframe {
                min-height: 810px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
