"""
DB Utility fFnctions
"""

import re
import urllib
import logging
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from sqlmodel import SQLModel, Session, create_engine, delete

SHOW_SQL_IN_LOG = False


# Associate a table with its data to update in a DB
@dataclass
class TableData:
    table: SQLModel
    df: pd.DataFrame


def mask_pw(odbc_str: str) -> str:
    """
    Mask uid and pwd in ODBC connection string for logging
    """
    # Use regex to mask uid= and pwd= values
    masked_str = re.sub(r"(uid=|pwd=)[^;]*", r"\1****", odbc_str, flags=re.IGNORECASE)
    return masked_str


def get_db_connection(odbc_str: str):
    """
    Given an ODBC connection string, return a connection to the DB via SQLModel
    """
    # Split connection string into odbc prefix and parameters (ie everything after odbc_connect=)
    match = re.search(r"^(.*odbc_connect=)(.*)$", odbc_str)
    prefix = match.group(1) if match else ""
    params = match.group(2) if match else ""
    if prefix and params:
        # URL escape ODBC connection string
        conn_str = prefix + urllib.parse.quote_plus(params)
    else:
        # No odbc_connect= found, just original string
        conn_str = odbc_str

    # Use SQLModel to establish connection to DB
    try:
        engine = create_engine(conn_str, echo=SHOW_SQL_IN_LOG)
        return engine
    except Exception as e:
        logging.error(f"ERROR: failed to connect to DB")
        logging.error(e)
        return None


def write_tables_to_db(engine, tables_data: list[TableData]) -> None:
    """ """
    with Session(engine) as session:
        for table_data in tables_data:
            logging.info(f"Writing data to table: {table_data.table.__tablename__}")

            # Clear table and rewrite from dataframe
            session.exec(delete(table_data.table))
            table_data.df.to_sql(
                name=table_data.table.__tablename__,
                con=session.connection(),
                if_exists="append",
                index=False,
            )
        session.commit()


def write_meta(engine, meta_table):
    """
    Populate the meta table with updated time
    """
    logging.info("Writing metadata")
    with Session(engine) as session:
        # Clear and reset last ingest time
        session.exec(delete(meta_table))
        session.add(meta_table(modified=datetime.now()))
        session.commit()
