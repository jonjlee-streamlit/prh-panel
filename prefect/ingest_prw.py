import os
import logging
import argparse
import urllib
import re
import pandas as pd
from datetime import datetime
from sqlmodel import Session, create_engine, delete
from dotenv import load_dotenv
from dataclasses import dataclass
from sqlmodel import SQLModel
from prw_ingest import prw_model as prw


# -------------------------------------------------------
# Types
# -------------------------------------------------------
# Association of table with its data to update in a DB
@dataclass
class TableData:
    table: SQLModel
    df: pd.DataFrame


# -------------------------------------------------------
# Config
# -------------------------------------------------------
# Load environment from .env file, does not overwrite existing env variables
load_dotenv()

# Load security sensitive config from env vars. Default output to local SQLite DB.
PRW_DB_ODBC = os.environ.get("PRW_DB_ODBC", "sqlite:///prw.sqlite3")

# Input files
DEFAULT_DATA_DIR = "./"
ENCOUNTERS_FILENAME = "encounters.xlsx"

# Other internal configuration
SHOW_SQL_IN_LOG = False


# -------------------------------------------------------
# Extract from Source Files
# -------------------------------------------------------
def sanity_check_data_dir(base_path, encounters_file):
    """
    Executed once at the beginning of ingest to validate data directory and files
    meet basic requirements.
    """
    error = None
    if not os.path.isdir(base_path):
        error = f"ERROR: data directory path does not exist: {base_path}"
    if not os.path.isfile(encounters_file):
        error = f"ERROR: data file missing: {encounters_file}"

    if error is not None:
        print(error)

    return error is None


def read_encounters(filename):
    # Extract data from first sheet from excel worksheet
    # -------------------------------------------------------
    logging.info(f"Reading {filename}")
    df = pd.read_excel(filename, sheet_name=0, usecols="A:V", header=0)

    # Transform data into patients and encounters tables
    # -------------------------------------------------------
    # Rename columns to match the required column names
    df.rename(
        columns={
            "MRN": "mrn",
            "Patient": "name",
            "Sex": "sex",
            "DOB": "dob",
            "Address": "address",
            "City": "city",
            "State": "state",
            "ZIP": "zip",
            "Phone": "phone",
            "Pt. E-mail Address": "email",
            "PCP": "pcp",
            "Location": "location",
            "Dept": "dept",
            "Visit Date": "encounter_date",
            "Time": "encounter_time",
            "Encounter Type": "UNUSED",
            "Type": "encounter_type",
            "Provider/Resource": "service_provider",
            "With PCP?": "with_pcp",
            "Appt Status": "appt_status",
            "Encounter Diagnoses": "diagnoses",
            "Level of Service": "level_of_service",
        },
        inplace=True,
    )

    # Drop duplicate patients based on 'mrn' and keep the first occurrence
    patients_df = df.drop_duplicates(subset=["mrn"], keep="first").copy()
    patients_df = patients_df[
        [
            "mrn",
            "sex",
            "dob",
            "address",
            "city",
            "state",
            "zip",
            "phone",
            "email",
            "pcp",
        ]
    ]
    # Force dob to be date only, no time
    patients_df["dob"] = pd.to_datetime(patients_df["dob"]).dt.date

    # Select relevant columns for encounters
    encounters_df = df[
        [
            "mrn",
            "location",
            "dept",
            "encounter_date",
            "encounter_time",
            "encounter_type",
            "service_provider",
            "with_pcp",
            "appt_status",
            "diagnoses",
            "level_of_service",
        ]
    ].copy()
    # Force encounter_date to be date only, no time
    encounters_df["encounter_date"] = pd.to_datetime(
        encounters_df["encounter_date"]
    ).dt.date

    return patients_df, encounters_df


def write_meta(engine, modified):
    """
    Populate the meta and sources_meta tables with updated times
    """
    logging.info("Writing metadata")
    with Session(engine) as session:
        # Clear metadata tables
        session.exec(delete(prw.PrwMeta))
        session.exec(delete(prw.PrwSourcesMeta))

        # Set last ingest time and other metadata fields
        session.add(prw.PrwMeta(modified=datetime.now()))

        # Store last modified timestamps for ingested files
        for file, modified_time in modified.items():
            sources_meta = prw.PrwSourcesMeta(filename=file, modified=modified_time)
            session.add(sources_meta)

        session.commit()


# -------------------------------------------------------
# DB Utilities
# -------------------------------------------------------
def get_db_connection(odbc_str):
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


def write_tables_to_db(engine, tables_data):
    with Session(engine) as session:
        for table_data in tables_data:
            logging.info(f"Writing data to table: {table_data.table.__tablename__}")

            # Clear data in DB
            session.exec(delete(table_data.table))

            # Write data from dataframe
            table_data.df.to_sql(
                name=table_data.table.__tablename__,
                con=session.connection(),
                if_exists="append",
                index=False,
            )
        session.commit()


# -------------------------------------------------------
# Utilities
# -------------------------------------------------------
def mask_pw(odbc_str):
    """
    Mask uid and pwd in ODBC connection string for logging
    """
    # Use regex to mask uid= and pwd= values
    masked_str = re.sub(r"(uid=|pwd=)[^;]*", r"\1****", odbc_str, flags=re.IGNORECASE)
    return masked_str


# -------------------------------------------------------
# Main entry point
# -------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ingest raw data into PRH warehouse.")
    parser.add_argument(
        "-i",
        "--input_dir",
        help="Path to the source data directory",
        default=DEFAULT_DATA_DIR,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output DB connection string, including credentials if needed",
        default=PRW_DB_ODBC,
    )
    return parser.parse_args()


def main():
    # Logging configuration
    logging.basicConfig(level=logging.INFO)

    # Load config from cmd line
    args = parse_arguments()
    base_path = args.input_dir
    output_odbc = args.output
    logging.info(f"Data dir: {base_path}, output: {mask_pw(output_odbc)}")

    # Source file paths
    encounters_file = os.path.join(base_path, ENCOUNTERS_FILENAME)
    source_files = [encounters_file]
    logging.info(f"Source files: {source_files}")

    # Sanity check data directory expected location and files
    if not sanity_check_data_dir(base_path, encounters_file):
        logging.error("ERROR: data directory error (see above). Terminating.")
        exit(1)

    # Read source files into memory
    patients_df, encounters_df = read_encounters(encounters_file)

    # Get connection to output DB
    db_engine = get_db_connection(output_odbc)
    if db_engine is None:
        logging.error("ERROR: cannot open output DB (see above). Terminating.")
        exit(1)

    # Create tables if they do not exist
    prw.PrwModel.metadata.create_all(db_engine)

    # Write into DB
    write_tables_to_db(
        db_engine,
        [
            TableData(table=prw.PrwPatient, df=patients_df),
            TableData(table=prw.PrwEncounter, df=encounters_df),
        ],
    )

    # Update last ingest time and modified times for source data files
    modified = {
        file: datetime.fromtimestamp(os.path.getmtime(file)) for file in source_files
    }
    write_meta(db_engine, modified)

    # Cleanup
    db_engine.dispose()
    logging.info("Done")


if __name__ == "__main__":
    main()
