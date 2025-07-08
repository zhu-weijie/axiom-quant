import numpy as np
import pandas as pd

from ..database.operations import get_db_engine
from .analytics import calculate_simple_moving_average


def load_data_for_ticker(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    engine = get_db_engine()
    query = f"""
    SELECT trade_date, close_price
    FROM historical_market_data
    WHERE ticker = '{ticker}'
    AND trade_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY trade_date ASC;
    """
    with engine.connect() as connection:
        df = pd.read_sql(
            query, connection, index_col="trade_date", parse_dates=["trade_date"]
        )
    return df


class Backtester:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = load_data_for_ticker(ticker, start_date, end_date)
        self.trades = pd.DataFrame()
        self.portfolio = pd.DataFrame()

    def run_sma_crossover_strategy(self, short_window: int, long_window: int):
        if self.data.empty:
            print("No data available for backtesting.")
            return

        signals = pd.DataFrame(index=self.data.index)
        signals["price"] = self.data["close_price"]
        signals["short_mavg"] = calculate_simple_moving_average(
            signals["price"], short_window
        )
        signals["long_mavg"] = calculate_simple_moving_average(
            signals["price"], long_window
        )
        signals.dropna(inplace=True)

        signals["signal"] = 0.0
        signals.loc[signals.index[short_window:], "signal"] = np.where(
            signals["short_mavg"][short_window:] > signals["long_mavg"][short_window:],
            1.0,
            0.0,
        )
        signals["positions"] = signals["signal"].diff()

        trades = signals[signals["positions"] != 0].copy()
        trades["action"] = np.where(trades["positions"] == 1, "BUY", "SELL")
        self.trades = trades[["price", "action"]]

        initial_capital = 100000.0
        portfolio = pd.DataFrame(index=signals.index)
        portfolio["positions"] = signals["signal"]
        portfolio["price"] = signals["price"]
        portfolio["holdings"] = portfolio["positions"] * portfolio["price"]
        portfolio["cash"] = initial_capital - (
            portfolio["positions"].diff() * portfolio["price"]
        ).cumsum().fillna(0)
        portfolio["total"] = portfolio["cash"] + portfolio["holdings"]
        self.portfolio = portfolio
