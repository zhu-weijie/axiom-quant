import numpy as np
import pandas as pd
import pytest

from axiomquant.core.analytics import (
    calculate_sharpe_ratio,
    calculate_simple_moving_average,
)


def test_calculate_sma_basic():
    prices = pd.Series([10, 12, 14, 16, 18])
    sma = calculate_simple_moving_average(prices, window=3)
    pd.testing.assert_series_equal(
        sma, pd.Series([np.nan, np.nan, 12.0, 14.0, 16.0]), check_names=False
    )


def test_calculate_sma_insufficient_data():
    prices = pd.Series([10, 12])
    sma = calculate_simple_moving_average(prices, window=3)
    assert sma.empty


def test_calculate_sma_invalid_window():
    prices = pd.Series([10, 12, 14])
    with pytest.raises(ValueError):
        calculate_simple_moving_average(prices, window=0)


def test_calculate_sharpe_ratio_basic():
    returns = pd.Series([0.01, 0.01, 0.01, -0.01, 0.01] * 50)
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
    assert sharpe > 1.0


def test_calculate_sharpe_ratio_no_volatility():
    returns = pd.Series([0.01] * 252)
    sharpe = calculate_sharpe_ratio(returns)
    assert sharpe == np.inf


def test_calculate_sharpe_ratio_empty_input():
    returns = pd.Series([], dtype=float)
    sharpe = calculate_sharpe_ratio(returns)
    assert sharpe == 0.0
