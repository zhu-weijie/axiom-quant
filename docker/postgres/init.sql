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

CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    short_window INT NOT NULL,
    long_window INT NOT NULL,
    sharpe_ratio FLOAT NOT NULL,
    trade_count INT NOT NULL,
    final_portfolio_value NUMERIC(15, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);