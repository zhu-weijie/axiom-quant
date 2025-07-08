from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from axiomquant.core.analytics import calculate_sharpe_ratio
from axiomquant.core.backtester import Backtester
from axiomquant.database.operations import get_db_engine

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
    run_id: int
    ticker: str
    sharpe_ratio: float
    trade_count: int
    final_portfolio_value: float


class ResultResponse(BaseModel):
    id: int
    ticker: str
    start_date: str
    end_date: str
    short_window: int
    long_window: int
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
    final_value = bt.portfolio["total"].iloc[-1]
    trade_count = len(bt.trades)

    engine = get_db_engine()
    insert_query = text(
        "INSERT INTO backtest_results ("
        "ticker, start_date, end_date, short_window, long_window, "
        "sharpe_ratio, trade_count, final_portfolio_value"
        ") VALUES ("
        ":ticker, :start_date, :end_date, :short_window, :long_window, "
        ":sharpe_ratio, :trade_count, :final_portfolio_value"
        ") RETURNING id;"
    )

    with engine.connect() as connection:
        result = connection.execute(
            insert_query,
            {
                "ticker": request.ticker,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "short_window": request.short_window,
                "long_window": request.long_window,
                "sharpe_ratio": sharpe,
                "trade_count": trade_count,
                "final_portfolio_value": final_value,
            },
        )
        connection.commit()
        new_id = result.scalar_one()

    return BacktestResponse(
        run_id=new_id,
        ticker=request.ticker,
        sharpe_ratio=sharpe,
        trade_count=trade_count,
        final_portfolio_value=final_value,
    )


@app.get("/results/{run_id}", response_model=ResultResponse)
def get_result(run_id: int):
    engine = get_db_engine()
    query = text(
        "SELECT id, ticker, start_date::text, end_date::text, short_window, "
        "long_window, sharpe_ratio, trade_count, final_portfolio_value "
        "FROM backtest_results WHERE id = :run_id"
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"run_id": run_id}).first()

    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return ResultResponse(
        id=result[0],
        ticker=result[1],
        start_date=result[2],
        end_date=result[3],
        short_window=result[4],
        long_window=result[5],
        sharpe_ratio=result[6],
        trade_count=result[7],
        final_portfolio_value=float(result[8]),
    )
