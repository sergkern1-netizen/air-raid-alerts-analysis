import pytest
import numpy as np
import pandas as pd
from src.models.prophet import ProphetModel

def test_prophet_initialization():
    """Test Prophet model can be initialized"""
    model = ProphetModel(interval_width=0.95)
    assert model.name == "Prophet"
    assert not model.is_fitted

def test_prophet_fit():
    """Test Prophet fitting with data"""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    values = 50 + 10 * np.sin(np.arange(100) * 2 * np.pi / 30) + np.random.normal(0, 5, 100)

    df = pd.DataFrame({"ds": dates, "y": values})

    model = ProphetModel()
    model.fit(df)

    assert model.is_fitted
    assert model.model is not None

def test_prophet_forecast():
    """Test Prophet forecasting"""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    values = 50 + 10 * np.sin(np.arange(100) * 2 * np.pi / 30) + np.random.normal(0, 5, 100)

    df = pd.DataFrame({"ds": dates, "y": values})

    model = ProphetModel()
    model.fit(df)
    forecast = model.forecast(steps=7)

    assert len(forecast) == 7
    assert all(np.isfinite(forecast))

def test_prophet_with_seasonality():
    """Test Prophet with explicit seasonality settings"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    values = 100 + 30 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 5, 365)

    df = pd.DataFrame({"ds": dates, "y": values})

    model = ProphetModel(yearly_seasonality=True, daily_seasonality=False)
    model.fit(df)
    forecast = model.forecast(steps=30)

    assert len(forecast) == 30
