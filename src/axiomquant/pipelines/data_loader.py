import pandas as pd
import yfinance as yf


def fetch_market_data(tickers: list[str], period: str = "5y") -> pd.DataFrame | None:
    try:
        data = yf.download(tickers, period=period, group_by="ticker")
        if data.empty:
            print("No data downloaded. Check ticker symbols and period.")
            return None

        if len(tickers) == 1:
            data["Ticker"] = tickers[0]
        else:
            data = data.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index()

        data.rename(
            columns={
                "Open": "open_price",
                "High": "high_price",
                "Low": "low_price",
                "Close": "close_price",
                "Volume": "volume",
                "Date": "trade_date",
            },
            inplace=True,
        )

        return data[
            [
                "trade_date",
                "Ticker",
                "open_price",
                "high_price",
                "low_price",
                "close_price",
                "volume",
            ]
        ]

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None
