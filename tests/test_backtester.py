from unittest.mock import patch

import pandas as pd

from axiomquant.core.backtester import Backtester


@patch("axiomquant.core.backtester.load_data_for_ticker")
def test_sma_crossover_strategy(mock_load_data):
    dates = pd.to_datetime(pd.date_range(start="2025-01-01", periods=20))
    price_data = [
        10,
        11,
        12,
        13,
        14,
        15,
        14,
        13,
        12,
        11,
        10,
        9,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
    ]
    mock_df = pd.DataFrame({"close_price": price_data}, index=dates)
    mock_load_data.return_value = mock_df

    backtester = Backtester(
        ticker="TEST", start_date="2025-01-01", end_date="2025-01-20"
    )
    backtester.run_sma_crossover_strategy(short_window=5, long_window=10)

    assert not backtester.trades.empty
    assert backtester.trades.iloc[0]["action"] == "SELL"
    assert backtester.trades.iloc[1]["action"] == "BUY"

    assert not backtester.portfolio.empty
    assert "total" in backtester.portfolio.columns
    assert backtester.portfolio["total"].iloc[-1] != 100000.0


@patch("axiomquant.core.backtester.load_data_for_ticker")
def test_backtester_no_data(mock_load_data):
    mock_load_data.return_value = pd.DataFrame()

    backtester = Backtester(
        ticker="NODATA", start_date="2025-01-01", end_date="2025-01-20"
    )
    backtester.run_sma_crossover_strategy(short_window=5, long_window=10)

    assert backtester.trades.empty
    assert backtester.portfolio.empty
