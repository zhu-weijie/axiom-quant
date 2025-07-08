CREATE TABLE historical_market_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price NUMERIC(10, 4) NOT NULL,
    high_price NUMERIC(10, 4) NOT NULL,
    low_price NUMERIC(10, 4) NOT NULL,
    close_price NUMERIC(10, 4) NOT NULL,
    volume BIGINT NOT NULL,
    UNIQUE(ticker, trade_date)
);
