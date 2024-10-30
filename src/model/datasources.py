import os, logging
import sqlite3
import boto3
from . import encrypt
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Path to default app database: panel.sqlite3 next to ingest.py
DB_FILE = "panel.sqlite3"
LOCAL_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", DB_FILE
)

# Remote URL in Cloudflare R2
R2_URL = os.environ.get("PRH_PANEL_CLOUDFLARE_R2_URL")
R2_BUCKET = os.environ.get("PRH_PANEL_CLOUDFLARE_R2_BUCKET")
R2_KEY = DB_FILE


def connect_file(file=LOCAL_DB_PATH):
    """
    Reads the specified SQLite database file into memory and returns a connection object.
    Returns sqlite3.Connection as a connection object to the SQLite database in memory.
    """
    return sqlite3.connect(file)


def connect_s3(url=R2_URL, bucket=R2_BUCKET, key=R2_KEY, encrypted=True):
    """
    Fetches the SQLite database file from a remote S3-compatible storage, decrypts it,
    and loads it into an in-memory SQLite database.
    Returns sqlite3.Connection as a connection object to the SQLite database in memory.
    """
    try:
        # Initialize the S3 client
        logging.info("Fetch remote DB file")
        s3_client = boto3.client("s3", endpoint_url=url)

        # Fetch the encrypted database file from the remote storage
        response = s3_client.get_object(Bucket=bucket, Key=key)
        remote_db = response["Body"].read()

        # Decrypt the database file
        logging.info("Decrypting")
        decrypted_db = encrypt.decrypt(remote_db) if encrypted else remote_db

        # Write the decrypted database to an in-memory SQLite database
        logging.info("Reading DB to memory")
        conn = sqlite3.connect(":memory:")
        with conn:
            conn.executescript(decrypted_db.decode("utf-8"))

        return conn

    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Credentials error: %s", e)
        raise
    except Exception as e:
        logging.error("Failed to fetch and load remote database: %s", e)
        raise
