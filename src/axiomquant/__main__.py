import argparse

from .database.operations import write_dataframe_to_db
from .pipelines.data_loader import fetch_market_data


def main():
    parser = argparse.ArgumentParser(description="AxiomQuant Data Ingestion Pipeline")
    parser.add_argument(
        "--tickers",
        nargs="+",
        required=True,
        help="A list of stock ticker symbols to process.",
    )
    parser.add_argument(
        "--period",
        type=str,
        default="5y",
        help="The period for which to download data (e.g., '1y', '5y', 'max').",
    )
    args = parser.parse_args()

    print(
        f"Starting data ingestion for tickers:{args.tickers} over period:{args.period}"
    )

    market_data_df = fetch_market_data(tickers=args.tickers, period=args.period)

    if market_data_df is not None and not market_data_df.empty:
        print(f"Fetched {len(market_data_df)} rows of data. Writing to database...")
        try:
            write_dataframe_to_db(market_data_df, "historical_market_data")
        except Exception as e:
            print(f"Pipeline failed during database write operation: {e}")
    else:
        print("No data fetched. Pipeline finished.")


if __name__ == "__main__":
    main()
