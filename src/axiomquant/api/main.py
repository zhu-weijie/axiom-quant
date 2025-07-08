from fastapi import FastAPI
from pydantic import BaseModel

from axiomquant.core.analytics import calculate_sharpe_ratio
from axiomquant.core.backtester import Backtester

app = FastAPI(
    title="AxiomQuant API",
    description="An API for running quantitative backtests.",
    version="0.1.0",
)


class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    short_window: int = 50
    long_window: int = 200


class BacktestResponse(BaseModel):
    ticker: str
    sharpe_ratio: float
    trade_count: int
    final_portfolio_value: float


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest):
    bt = Backtester(
        ticker=request.ticker,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    bt.run_sma_crossover_strategy(
        short_window=request.short_window, long_window=request.long_window
    )

    daily_returns = bt.portfolio["total"].pct_change().dropna()
    sharpe = calculate_sharpe_ratio(daily_returns)

    return BacktestResponse(
        ticker=request.ticker,
        sharpe_ratio=sharpe,
        trade_count=len(bt.trades),
        final_portfolio_value=bt.portfolio["total"].iloc[-1],
    )
