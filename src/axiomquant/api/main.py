from fastapi import BackgroundTasks, FastAPI, HTTPException
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


class BacktestCreateResponse(BaseModel):
    message: str
    run_id: int


class ResultResponse(BaseModel):
    id: int
    ticker: str
    start_date: str
    end_date: str
    short_window: int
    long_window: int
    status: str
    sharpe_ratio: float | None
    trade_count: int | None
    final_portfolio_value: float | None


@app.get("/health")
def read_health():
    return {"status": "ok"}


def run_backtest_in_background(run_id: int, request: BacktestRequest):
    engine = get_db_engine()
    update_query = text(
        "UPDATE backtest_results SET status = :status, sharpe_ratio = :sharpe, "
        "trade_count = :trades, final_portfolio_value = :value "
        "WHERE id = :run_id"
    )

    try:
        bt = Backtester(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        bt.run_sma_crossover_strategy(
            short_window=request.short_window, long_window=request.long_window
        )

        if bt.portfolio.empty or bt.portfolio["total"].iloc[-1] is None:
            params = {
                "status": "COMPLETED",
                "sharpe": 0.0,
                "trades": 0,
                "value": 100000.0,
                "run_id": run_id,
            }
        else:
            daily_returns = bt.portfolio["total"].pct_change().dropna()
            params = {
                "status": "COMPLETED",
                "sharpe": float(calculate_sharpe_ratio(daily_returns)),
                "trades": int(len(bt.trades)),
                "value": float(bt.portfolio["total"].iloc[-1]),
                "run_id": run_id,
            }

    except Exception as e:
        print(f"Backtest run {run_id} failed: {e}")
        params = {
            "status": "FAILED",
            "sharpe": None,
            "trades": None,
            "value": None,
            "run_id": run_id,
        }

    with engine.connect() as connection:
        connection.execute(update_query, params)
        connection.commit()


@app.post("/backtest", response_model=BacktestCreateResponse, status_code=202)
def create_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    engine = get_db_engine()
    insert_query = text(
        "INSERT INTO backtest_results ("
        "ticker, start_date, end_date, short_window, long_window, status) "
        "VALUES ("
        ":ticker, :start_date, :end_date, :short_window, :long_window, 'PENDING') "
        "RETURNING id;"
    )
    with engine.connect() as connection:
        result = connection.execute(insert_query, request.dict())
        connection.commit()
        new_id = result.scalar_one()

    background_tasks.add_task(run_backtest_in_background, new_id, request)

    return BacktestCreateResponse(message="Backtest run started", run_id=new_id)


@app.get("/results/{run_id}", response_model=ResultResponse)
def get_result(run_id: int):
    engine = get_db_engine()
    query = text(
        "SELECT id, ticker, start_date::text, end_date::text, short_window, "
        "long_window, status, sharpe_ratio, trade_count, final_portfolio_value "
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
        status=result[6],
        sharpe_ratio=result[7],
        trade_count=result[8],
        final_portfolio_value=float(result[9]) if result[9] is not None else None,
    )
