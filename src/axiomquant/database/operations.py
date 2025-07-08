import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine


def get_db_engine() -> Engine:
    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ.get("POSTGRES_USER", "admin"),
        password=os.environ.get("POSTGRES_PASSWORD", "password"),
        host=os.environ.get("POSTGRES_HOST", "db"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        database=os.environ.get("POSTGRES_DB", "axiom_quant_dev"),
    )
    return create_engine(db_url)


def write_dataframe_to_db(df: pd.DataFrame, table_name: str) -> None:
    if df.empty:
        print("DataFrame is empty. No data to write.")
        return

    try:
        engine = get_db_engine()
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Successfully wrote {len(df)} rows to table '{table_name}'.")
    except Exception as e:
        print(f"An error occurred while writing to the database: {e}")
        raise
