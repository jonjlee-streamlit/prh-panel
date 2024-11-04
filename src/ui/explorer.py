import streamlit as st
import pandas as pd
import plotly.express as px
from . import ui
from ..model import source_data, data


def st_page(src_data: source_data.SourceData):
    """
    Show department specific Streamlit page
    """
    # Get sidebar settings
    user_settings = ui.show_settings(src_data)

    # Process the source data by filtering and generating the specifc metrics displayed in the UI
    app_data = data.process(user_settings, src_data)

    st.write("# Panel Explorer (2024)")

    st_patient_details(app_data.paneled_patients_df)

    st.write("## Patient List")
    selected_mrn = st_patient_table(app_data.paneled_patients_df)

    st.write("## Encounters")
    st_encounter_table(app_data.encounters_df, selected_mrn)


def st_patient_table(patients_df: pd.DataFrame):
    """
    Display patient table
    """
    patients_df = patients_df.copy()

    # Display a dataframe with selectable rows (one at a time) with only
    # columns MRN, sex, age_display, city, state, panel_location
    # Display column headers MRN, Sex, Age, City, State, Panel
    selected_columns = ["mrn", "sex", "age_display", "location", "panel_location"]
    display_columns = ["MRN", "Sex", "Age", "City", "Panel"]

    patients_df = patients_df[selected_columns]
    patients_df.columns = display_columns

    event = st.dataframe(
        patients_df.style.format(
            {
                "MRN": "{}",
            }
        ),
        hide_index=True,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
    )

    if event and event.selection and event.selection.rows:
        selected_row = event.selection.rows[0]
        selected_mrn = patients_df.iloc[selected_row]["MRN"]
        return selected_mrn

    return None


def st_patient_details(patients_df: pd.DataFrame):
    st.write(f"#### Number of patients: {len(patients_df)}")

    col1, col2 = st.columns(2)
    with col2:
        sex_counts = patients_df["sex"].value_counts()

        fig = px.pie(
            sex_counts,
            values=sex_counts.values,
            names=sex_counts.index,
            title="Sex",
            hole=0.3,
        )
        fig.update_layout(
            title={
                "text": "Sex",
                "x": 0.43,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 22, "weight": "normal"},
            }
        )
        st.plotly_chart(fig)

    with col1:
        age_bins = [0, 1, 18, 65, float("inf")]
        age_labels = ["<1y", "<18y", "18-65y", ">65y"]
        patients_df["age_group"] = pd.cut(
            patients_df["age"], bins=age_bins, labels=age_labels, right=False
        )

        age_group_counts = patients_df["age_group"].value_counts().sort_index()

        fig = px.pie(
            age_group_counts,
            values=age_group_counts.values,
            names=age_group_counts.index,
            title="Age Group",
            hole=0.3,
        )
        fig.update_layout(
            title={
                "text": "Age Group",
                "x": 0.4,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 22, "weight": "normal"},
            }
        )
        st.plotly_chart(fig)

    location_counts = patients_df["location"].value_counts()
    location_counts["Other"] = location_counts[location_counts < 20].sum()
    location_counts = pd.concat(
        [
            location_counts[location_counts >= 20],
            pd.Series({"Other": location_counts["Other"]}),
        ]
    )

    fig = px.bar(
        location_counts,
        x=location_counts.index,
        y=location_counts.values,
        title="Locations",
        labels={"y": "Count", "index": ""},
    )
    fig.update_layout(
        title={
            "text": "Locations",
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 22, "weight": "normal"},
        }
    )
    st.plotly_chart(fig)


def st_encounter_table(encounters_df: pd.DataFrame, selected_mrn):
    if selected_mrn is None:
        return st.write("Select a patient to view encounters")

    encounters_df = encounters_df.copy()
    encounters_df = encounters_df[encounters_df["mrn"] == selected_mrn]

    selected_columns = [
        "location",
        "encounter_date",
        "encounter_type",
        "service_provider",
        "with_pcp",
        "diagnoses",
        "level_of_service",
    ]
    display_columns = [
        "Location",
        "Date",
        "Type",
        "Provider",
        "With PCP",
        "Diagnoses",
        "LOS",
    ]
    encounters_df = encounters_df[selected_columns]
    encounters_df.columns = display_columns

    # Keep only
    st.dataframe(
        encounters_df.style.format(
            {
                "Date": "{:%Y-%m-%d}",
            },
        ),
        hide_index=True,
    )
