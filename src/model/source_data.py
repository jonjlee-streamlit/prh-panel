"""
Source data as in-memory copy of all DB tables as dataframes
"""

import logging
import pandas as pd
import streamlit as st
from dataclasses import dataclass
from datetime import datetime
from sqlmodel import Session, text
from . import datasources


@dataclass(eq=True, frozen=True)
class SourceData:
    """In-memory copy of DB tables"""

    patients_df: pd.DataFrame = None
    encounters_df: pd.DataFrame = None

    # Metadata
    modified: datetime = None


@st.cache_data
def from_file() -> SourceData:
    engine = datasources.connect_file()
    src_data = from_db(engine)
    engine.dispose()
    return src_data


@st.cache_data
def from_s3() -> SourceData:
    engine = datasources.connect_s3()
    src_data = from_db(engine)
    engine.dispose()
    return src_data


def from_db(db_engine) -> SourceData:
    """
    Read all data from specified DB connection into memory and return as dataframes
    """
    logging.info("Reading DB tables")

    # Read the largest last_updated value from Meta
    with Session(db_engine) as session:
        modified = session.exec(text("select max(modified) from meta")).fetchone()[0]

    # Read dashboard data into dataframes
    dfs = {
        "patients_df": pd.read_sql_table("patients", db_engine),
        "encounters_df": pd.read_sql_table("encounters", db_engine),
    }

    return SourceData(modified=modified, **dfs)
