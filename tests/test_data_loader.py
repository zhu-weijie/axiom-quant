import pandas as pd

from axiomquant.pipelines.data_loader import fetch_market_data


def test_fetch_market_data_single_ticker():
    data = fetch_market_data(tickers=["AAPL"], period="1mo")
    assert data is not None
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert "ticker" in data.columns
    assert data["ticker"].iloc[0] == "AAPL"


def test_fetch_market_data_multiple_tickers():
    data = fetch_market_data(tickers=["MSFT", "GOOG"], period="1mo")
    assert data is not None
    assert isinstance(data, pd.DataFrame)
    assert len(data["ticker"].unique()) == 2


def test_fetch_market_data_invalid_ticker():
    data = fetch_market_data(tickers=["INVALIDTICKERXYZ"], period="1mo")
    assert data is None or data.empty
