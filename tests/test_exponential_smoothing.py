import pytest
import numpy as np
import pandas as pd
from src.models.exponential_smoothing import ExponentialSmoothingModel


def test_exponential_smoothing_initialization():
    """Test ExponentialSmoothing model can be initialized"""
    model = ExponentialSmoothingModel(seasonal_periods=30)
    assert model.name == "ExponentialSmoothing"
    assert not model.is_fitted


def test_exponential_smoothing_fit():
    """Test ExponentialSmoothing fitting with data"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    trend = np.linspace(50, 70, 365)
    seasonal = 10 * np.sin(np.arange(365) * 2 * np.pi / 30)
    values = trend + seasonal + np.random.normal(0, 3, 365)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(df)

    assert model.is_fitted
    assert model.fitted_model is not None


def test_exponential_smoothing_forecast():
    """Test ExponentialSmoothing forecasting"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    trend = np.linspace(50, 70, 365)
    seasonal = 10 * np.sin(np.arange(365) * 2 * np.pi / 30)
    values = trend + seasonal + np.random.normal(0, 3, 365)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(df)
    forecast = model.forecast(steps=30)

    assert len(forecast) == 30
    assert all(np.isfinite(forecast))


def test_exponential_smoothing_different_seasonal_periods():
    """Test with different seasonal periods"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    values = 100 + np.random.normal(0, 5, 365)

    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = ExponentialSmoothingModel(seasonal_periods=7)
    model.fit(df)
    forecast = model.forecast(steps=14)

    assert len(forecast) == 14


def test_exponential_smoothing_forecast_without_fit():
    """Test that forecast raises error if fit not called"""
    model = ExponentialSmoothingModel()
    with pytest.raises(ValueError, match="must be fitted"):
        model.forecast(steps=7)


def test_exponential_smoothing_fit_with_numpy_array():
    """Test fitting with numpy array instead of DataFrame"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    values = 100 + np.random.normal(0, 5, 365)

    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(values)  # Pass numpy array directly

    assert model.is_fitted
    forecast = model.forecast(steps=7)
    assert len(forecast) == 7


def test_exponential_smoothing_get_diagnostics():
    """Test get_diagnostics returns model information"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    values = 100 + np.random.normal(0, 5, 365)
    df = pd.DataFrame({"timestamp": dates, "value": values})

    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(df)

    diagnostics = model.get_diagnostics()

    assert "name" in diagnostics
    assert diagnostics["seasonal_periods"] == 30
    assert diagnostics["name"] == "ExponentialSmoothing"
