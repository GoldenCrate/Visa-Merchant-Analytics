"""
One-time script: loads merchants.csv into Snowflake.
Run from project root after generate_data.py.

    python load_to_snowflake.py

Reads credentials from .env (copy from apple-project/.env and update DATABASE).
"""
import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

CREDS = {
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
}
DATABASE = os.environ.get("SNOWFLAKE_DATABASE", "MERCHANT_ANALYTICS")
SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")

CREATE_DB = f"CREATE DATABASE IF NOT EXISTS {DATABASE};"
USE_DB = f"USE DATABASE {DATABASE};"
USE_SCHEMA = f"USE SCHEMA {SCHEMA};"
DROP_TABLE = "DROP TABLE IF EXISTS MERCHANTS;"
CREATE_TABLE = """
CREATE TABLE MERCHANTS (
    merchant_id         INTEGER,
    merchant_name       VARCHAR,
    category            VARCHAR,
    region              VARCHAR,
    integration_type    VARCHAR,
    years_on_visa       FLOAT,
    avg_monthly_volume_k FLOAT,
    monthly_txn_count   INTEGER,
    avg_txn_size        FLOAT,
    dispute_rate_pct    FLOAT,
    support_tickets_monthly INTEGER,
    volume_trend_pct    FLOAT,
    churn_label         INTEGER
);
"""


def main():
    df = pd.read_csv("streamlit_app/data/merchants.csv")
    df.columns = [c.upper() for c in df.columns]

    conn = snowflake.connector.connect(**CREDS)
    cur = conn.cursor()
    try:
        cur.execute(CREATE_DB)
        cur.execute(USE_DB)
        cur.execute(USE_SCHEMA)
        cur.execute(DROP_TABLE)
        cur.execute(CREATE_TABLE)
        print("Table created.")

        success, nchunks, nrows, _ = write_pandas(conn, df, "MERCHANTS", database=DATABASE, schema=SCHEMA)
        print(f"Loaded {nrows:,} rows in {nchunks} chunk(s). Success={success}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
