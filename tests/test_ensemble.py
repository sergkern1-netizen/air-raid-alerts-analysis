import pytest
import numpy as np
import pandas as pd
from src.models.ensemble import ModelEnsemble, compare_models
from src.models.arima import ARIMAModel
from src.models.prophet import ProphetModel


def test_ensemble_initialization():
    """Test ensemble can be initialized"""
    ensemble = ModelEnsemble()
    assert ensemble.models == {}
    assert not ensemble.fitted


def test_ensemble_add_model():
    """Test adding models to ensemble"""
    ensemble = ModelEnsemble()
    arima_model = ARIMAModel(order=(1, 1, 1))

    ensemble.add_model("ARIMA", arima_model)
    assert "ARIMA" in ensemble.models


def test_ensemble_fit_all_models():
    """Test fitting all models in ensemble"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    values = 100 + np.arange(150) * 0.3 + np.random.normal(0, 5, 150)

    df = pd.DataFrame({"ds": dates, "y": values})

    ensemble = ModelEnsemble()
    ensemble.add_model("ARIMA", ARIMAModel(order=(1, 1, 1)))
    ensemble.add_model("Prophet", ProphetModel())

    ensemble.fit(df)

    assert ensemble.fitted
    assert ensemble.models["ARIMA"].is_fitted
    assert ensemble.models["Prophet"].is_fitted


def test_ensemble_forecast_comparison():
    """Test comparing forecasts from all models"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    values = 100 + np.arange(150) * 0.3 + np.random.normal(0, 5, 150)

    df = pd.DataFrame({"ds": dates, "y": values})

    ensemble = ModelEnsemble()
    ensemble.add_model("ARIMA", ARIMAModel(order=(1, 1, 1)))
    ensemble.add_model("Prophet", ProphetModel())

    ensemble.fit(df)
    forecasts = ensemble.forecast(steps=7)

    assert len(forecasts) == 2
    assert "ARIMA" in forecasts
    assert "Prophet" in forecasts
    assert len(forecasts["ARIMA"]) == 7
    assert len(forecasts["Prophet"]) == 7


def test_compare_models_function():
    """Test model comparison function"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    values = 100 + np.arange(200) * 0.3 + np.random.normal(0, 5, 200)
    df_train = pd.DataFrame({"ds": dates[:150], "y": values[:150]})
    df_test = pd.DataFrame({"ds": dates[150:], "y": values[150:]})

    results = compare_models([ARIMAModel(order=(1, 1, 1))], df_train, df_test)

    assert len(results) > 0
    assert "ARIMA" in results[0]["Model"]
