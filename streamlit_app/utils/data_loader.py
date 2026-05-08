"""
Data loader — tries Snowflake first, falls back to local CSV.
Snowflake credentials come from st.secrets (Streamlit Cloud) or .env (local).
"""
from __future__ import annotations
import os
import pandas as pd
import streamlit as st


def _get_sf_creds() -> dict | None:
    try:
        return {
            "account": st.secrets["SNOWFLAKE_ACCOUNT"],
            "user": st.secrets["SNOWFLAKE_USER"],
            "password": st.secrets["SNOWFLAKE_PASSWORD"],
            "database": st.secrets["SNOWFLAKE_DATABASE"],
            "schema": st.secrets["SNOWFLAKE_SCHEMA"],
            "warehouse": st.secrets["SNOWFLAKE_WAREHOUSE"],
        }
    except Exception:
        pass

    creds = {
        "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
        "user": os.environ.get("SNOWFLAKE_USER"),
        "password": os.environ.get("SNOWFLAKE_PASSWORD"),
        "database": os.environ.get("SNOWFLAKE_DATABASE", "MERCHANT_ANALYTICS"),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
    }
    if all(creds.get(k) for k in ("account", "user", "password", "warehouse")):
        return creds
    return None


def _load_from_snowflake(creds: dict) -> pd.DataFrame:
    import snowflake.connector
    conn = snowflake.connector.connect(**creds)
    try:
        df = pd.read_sql("SELECT * FROM MERCHANTS", conn)
        df.columns = [c.lower() for c in df.columns]
        return df
    finally:
        conn.close()


def _csv_path() -> str:
    here = os.path.dirname(__file__)
    return os.path.join(here, "..", "data", "merchants.csv")


@st.cache_data(ttl=300, show_spinner=False)
def load_merchants() -> pd.DataFrame:
    creds = _get_sf_creds()
    if creds:
        try:
            return _load_from_snowflake(creds)
        except Exception:
            pass
    return pd.read_csv(_csv_path())
