import os

import httpx
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

API_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def db_engine() -> Engine:
    db_url = (
        f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER', 'admin')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'password')}@"
        f"localhost:"
        f"{os.environ.get('POSTGRES_PORT', 5432)}/"
        f"{os.environ.get('POSTGRES_DB', 'axiom_quant_dev')}"
    )
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def setup_test_database(db_engine: Engine):
    sql_file_path = os.path.join(
        os.path.dirname(__file__), "..", "docker", "postgres", "init.sql"
    )
    with open(sql_file_path, "r") as f:
        sql_commands = f.read()

    with db_engine.connect() as connection:
        print("Resetting database schema...")
        connection.execute(text("DROP TABLE IF EXISTS backtest_results;"))
        connection.execute(text("DROP TABLE IF EXISTS historical_market_data;"))

        connection.execute(text(sql_commands))
        connection.commit()

    print("Setting up test database...")
    test_data = {
        "trade_date": pd.to_datetime(pd.date_range(start="2023-01-01", periods=200)),
        "ticker": "TEST",
        "open_price": 100,
        "high_price": 105,
        "low_price": 95,
        "close_price": 100,
        "volume": 1000,
    }
    df = pd.DataFrame(test_data)
    df["close_price"] = df["close_price"] + df["trade_date"].dt.day

    df.to_sql("historical_market_data", db_engine, if_exists="append", index=False)

    yield

    print("Tearing down test database...")
    with db_engine.connect() as connection:
        connection.execute(text("DELETE FROM backtest_results;"))
        connection.execute(text("DELETE FROM historical_market_data;"))
        connection.commit()


def test_health_check():
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_backtest_endpoint_and_get_results():
    backtest_payload = {
        "ticker": "TEST",
        "start_date": "2023-01-01",
        "end_date": "2023-07-01",
        "short_window": 10,
        "long_window": 20,
    }

    with httpx.Client() as client:
        response = client.post(f"{API_URL}/backtest", json=backtest_payload, timeout=30)

    assert response.status_code == 200
    response_data = response.json()
    assert "run_id" in response_data
    run_id = response_data["run_id"]

    with httpx.Client() as client:
        get_response = client.get(f"{API_URL}/results/{run_id}")

    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == run_id
    assert get_data["ticker"] == "TEST"
    assert get_data["trade_count"] > 0
