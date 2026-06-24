"""ARIMA time series model implementation."""

import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA as SM_ARIMA

from .base import TimeSeriesModel

# Suppress warnings
warnings.filterwarnings("ignore")


class ARIMAModel(TimeSeriesModel):
    """ARIMA (AutoRegressive Integrated Moving Average) time series model.

    Implements ARIMA forecasting using statsmodels.
    """

    def __init__(self, order: tuple = (1, 1, 1), name: str = "ARIMA"):
        """Initialize ARIMAModel.

        Parameters
        ----------
        order : tuple, optional
            ARIMA order (p, d, q) where:
            - p: number of autoregressive lags
            - d: degree of differencing
            - q: number of moving average lags
            Default: (1, 1, 1)
        name : str, optional
            Name of the model (default: "ARIMA")
        """
        super().__init__(name=name)
        self.order = order
        self.model = None
        self._fit_result = None
        self._data = None

    def fit(self, data):
        """Fit the ARIMA model to data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Training data. If DataFrame, must contain 'ds' and 'y' columns.
            If numpy array, will be treated as time series values.

        Raises
        ------
        ValueError
            If data format is invalid
        """
        # Convert to values array
        if isinstance(data, pd.DataFrame):
            if "y" not in data.columns:
                raise ValueError("DataFrame must contain 'y' column")
            y_values = data["y"].values
        elif isinstance(data, np.ndarray):
            y_values = data
        else:
            raise ValueError("Data must be pandas DataFrame or numpy array")

        # Store original data for reference
        self._data = y_values

        # Fit ARIMA model
        try:
            self.model = SM_ARIMA(y_values, order=self.order)
            self._fit_result = self.model.fit()
        except Exception as e:
            raise ValueError(f"Failed to fit ARIMA model: {str(e)}")

        self.is_fitted = True

    def forecast(self, steps: int) -> np.ndarray:
        """Generate forecasts for future steps.

        Parameters
        ----------
        steps : int
            Number of steps ahead to forecast

        Returns
        -------
        np.ndarray
            Array of forecast values with shape (steps,)

        Raises
        ------
        ValueError
            If model is not fitted yet
        """
        if not self.is_fitted or self._fit_result is None:
            raise ValueError("Model must be fitted before forecasting")

        # Get forecast from ARIMA
        try:
            forecast_result = self._fit_result.get_forecast(steps=steps)
            forecast_values = forecast_result.predicted_mean.values
        except Exception:
            # Fallback: use simple last value
            forecast_values = np.full(steps, self._data[-1])

        return forecast_values

    def get_diagnostics(self) -> dict:
        """Get model diagnostics information.

        Returns
        -------
        dict
            Dictionary with model configuration and statistics
        """
        diagnostics = super().get_diagnostics()
        diagnostics.update(
            {
                "order": self.order,
                "aic": self._fit_result.aic if self._fit_result else None,
                "bic": self._fit_result.bic if self._fit_result else None,
            }
        )
        return diagnostics
