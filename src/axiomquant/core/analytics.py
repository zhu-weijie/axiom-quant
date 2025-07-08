import numpy as np
import pandas as pd


def calculate_simple_moving_average(prices: pd.Series, window: int) -> pd.Series:
    if window <= 0:
        raise ValueError("Window size must be positive.")
    if prices.empty or len(prices) < window:
        return pd.Series(dtype=np.float64)
    return prices.rolling(window=window).mean()


def calculate_sharpe_ratio(
    daily_returns: pd.Series, risk_free_rate: float = 0.0
) -> float:
    if daily_returns.empty:
        return 0.0

    excess_returns = daily_returns - (risk_free_rate / 252)

    annualized_mean_return = excess_returns.mean() * 252

    annualized_volatility = excess_returns.std() * np.sqrt(252)

    if annualized_volatility == 0:
        return np.inf if annualized_mean_return > 0 else 0.0

    return annualized_mean_return / annualized_volatility
