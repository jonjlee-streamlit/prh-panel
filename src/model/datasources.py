import os, logging
import sqlite3
import boto3
import streamlit as st
from . import encrypt
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import pandas as pd
from sqlalchemy import create_engine

# Path to default app database: panel.sqlite3 next to ingest.py
DB_FILE = "panel.sqlite3"
LOCAL_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", DB_FILE
)

# Remote URL in Cloudflare R2
R2_ACCT_ID = st.secrets.get("PRH_PANEL_R2_ACCT_ID")
R2_ACCT_KEY = st.secrets.get("PRH_PANEL_R2_ACCT_KEY")
R2_URL = st.secrets.get("PRH_PANEL_R2_URL")
R2_BUCKET = st.secrets.get("PRH_PANEL_R2_BUCKET")
R2_OBJECT = DB_FILE + ".enc"

# Encryption key for remote database
DATA_KEY = st.secrets.get("PRH_PANEL_DATA_KEY")


def connect_file(file=LOCAL_DB_PATH):
    """
    Reads the specified SQLite database file into memory and returns a connection object.
    Returns sqlite3.Connection as a connection object to the SQLite database in memory.
    """
    conn = sqlite3.connect(file)
    return engine_from_conn(conn)


def connect_s3(
    acct_id=R2_ACCT_ID,
    acct_key=R2_ACCT_KEY,
    url=R2_URL,
    bucket=R2_BUCKET,
    obj=R2_OBJECT,
    data_key=DATA_KEY,
):
    """
    Fetches the SQLite database file from a remote S3-compatible storage, decrypts it,
    and loads it into an in-memory SQLite database.
    Returns a SQLAlchemy engine to the SQLite database in memory.
    """
    try:
        # Initialize the S3 client
        logging.info("Fetch remote DB file")
        s3_client = boto3.client(
            "s3",
            endpoint_url=url,
            region_name="auto",
            aws_access_key_id=acct_id,
            aws_secret_access_key=acct_key,
        )

        # Fetch the encrypted database file from the remote storage
        response = s3_client.get_object(Bucket=bucket, Key=obj)
        remote_db = response["Body"].read()

        # Decrypt the database file
        logging.info("Decrypting")
        decrypted_db = (
            encrypt.decrypt(remote_db, data_key) if DATA_KEY is not None else remote_db
        )

        # Write the decrypted database to an in-memory SQLite database
        logging.info("Reading DB to memory")
        conn = sqlite3.connect(":memory:")
        conn.deserialize(decrypted_db)

        return engine_from_conn(conn)

    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", e)
        raise
    except Exception as e:
        logging.error("Failed to fetch and load remote database: %s", e)
        raise


def engine_from_conn(conn):
    """
    Returns a SQLAlchemy engine object from a sqlite3 connection object.
    Returns sqlalchemy.engine.base.Connection as a connection object from the given the SQLite database connection
    """
    return create_engine(f"sqlite://", creator=lambda: conn)
