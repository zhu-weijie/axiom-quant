import pandas as pd
import yfinance as yf


def fetch_market_data(tickers: list[str], period: str = "5y") -> pd.DataFrame | None:
    if not tickers:
        return None

    try:
        data = yf.download(tickers, period=period, auto_adjust=False, group_by="ticker")

        if data.empty:
            return None

        data = (
            data.stack(level=0, future_stack=True)
            .rename_axis(["Date", "Ticker"])
            .reset_index()
        )

        data.rename(
            columns={
                "Date": "trade_date",
                "Ticker": "ticker",
                "Open": "open_price",
                "High": "high_price",
                "Low": "low_price",
                "Close": "close_price",
                "Volume": "volume",
            },
            inplace=True,
        )

        final_columns = [
            "trade_date",
            "ticker",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        ]

        data.dropna(subset=final_columns, inplace=True)

        return data[final_columns]

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None
