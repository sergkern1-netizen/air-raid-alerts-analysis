import pytest
import numpy as np
import pandas as pd
from src.models.lstm import LSTMModel


def test_lstm_initialization():
    """Test LSTM model can be initialized"""
    model = LSTMModel(lookback=30, units=50, epochs=10)
    assert model.name == "LSTM"
    assert not model.is_fitted


def test_lstm_fit():
    """Test LSTM fitting with time series data"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    values = 100 + np.arange(200) * 0.5 + np.random.normal(0, 5, 200)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = LSTMModel(lookback=30, units=32, epochs=5, verbose=0)
    model.fit(df)

    assert model.is_fitted
    assert model.model is not None


def test_lstm_forecast():
    """Test LSTM forecasting"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    values = 100 + np.arange(200) * 0.5 + np.random.normal(0, 5, 200)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = LSTMModel(lookback=30, units=32, epochs=5, verbose=0)
    model.fit(df)
    forecast = model.forecast(steps=7)

    assert len(forecast) == 7
    assert all(np.isfinite(forecast))


def test_lstm_with_different_lookback():
    """Test LSTM with different lookback periods"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=300, freq="D")
    values = 100 + np.arange(300) * 0.3 + np.random.normal(0, 5, 300)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = LSTMModel(lookback=50, units=32, epochs=5, verbose=0)
    model.fit(df)
    forecast = model.forecast(steps=14)

    assert len(forecast) == 14
