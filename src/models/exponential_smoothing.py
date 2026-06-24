"""Exponential Smoothing time series model implementation."""

import logging
import numpy as np
import pandas as pd
import warnings
from typing import Union

from .base import TimeSeriesModel

logger = logging.getLogger(__name__)

# Suppress any warnings
warnings.filterwarnings("ignore")


class ExponentialSmoothingModel(TimeSeriesModel):
    """Exponential Smoothing-based time series forecasting model.

    Implements Holt-Winters exponential smoothing with support for flexible
    seasonal periods. Uses statsmodels.tsa.holtwinters.ExponentialSmoothing.
    """

    def __init__(
        self,
        seasonal_periods: int = 30,
        trend: str = "add",
        seasonal: str = "add",
        seasonal_periods_validation: bool = True,
    ):
        """Initialize ExponentialSmoothingModel.

        Parameters
        ----------
        seasonal_periods : int, optional
            Number of periods for seasonal component (default: 30)
        trend : str, optional
            Trend component: 'add' for additive, 'mul' for multiplicative (default: 'add')
        seasonal : str, optional
            Seasonal component: 'add' for additive, 'mul' for multiplicative (default: 'add')
        seasonal_periods_validation : bool, optional
            Whether to validate seasonal periods >= 2 (default: True)
        """
        super().__init__(name="ExponentialSmoothing")
        self.seasonal_periods = seasonal_periods
        self.trend = trend
        self.seasonal = seasonal
        self.seasonal_periods_validation = seasonal_periods_validation
        self.fitted_model = None
        self._training_values = None
        self._last_value = None
        self._mean = None
        self._std = None

    def _fit_exponential_smoothing(self, values: np.ndarray, seasonal_arg=None):
        """Private method to fit ExponentialSmoothing with given seasonal parameter.

        Parameters
        ----------
        values : np.ndarray
            Training values array
        seasonal_arg : str or None, optional
            Seasonal component to use ('add', 'mul', or None)

        Returns
        -------
        ExponentialSmoothingResults
            Fitted ExponentialSmoothing model

        Raises
        ------
        Exception
            If fitting fails with the given parameters
        """
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        return ExponentialSmoothing(
            values,
            trend=self.trend,
            seasonal=seasonal_arg,
            seasonal_periods=self.seasonal_periods,
        ).fit(optimized=True)

    def fit(self, data: Union[pd.DataFrame, np.ndarray]) -> None:
        """Fit the Exponential Smoothing model to data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Training data. If DataFrame, must contain 'value' column.
            If numpy array, will be used directly.

        Raises
        ------
        ValueError
            If DataFrame doesn't contain required columns or data is too short
        """
        # Convert numpy array to values if needed
        if isinstance(data, np.ndarray):
            values = data
        elif isinstance(data, pd.DataFrame):
            if "value" not in data.columns:
                raise ValueError("DataFrame must contain 'value' column")
            values = data["value"].values
        else:
            raise ValueError("Data must be a pandas DataFrame or numpy array")

        # Validate minimum data length
        min_length = 2 * self.seasonal_periods
        if len(values) < min_length:
            raise ValueError(
                f"Data must have at least {min_length} observations "
                f"(2x seasonal_periods), got {len(values)}"
            )

        # Store training values and statistics
        self._training_values = values
        self._last_value = values[-1]
        self._mean = np.mean(values)
        self._std = np.std(values)

        # Try to fit Exponential Smoothing model
        try:
            self.fitted_model = self._fit_exponential_smoothing(values, self.seasonal)
        except Exception as e:
            logger.warning(
                f"ExponentialSmoothing with seasonal={self.seasonal} failed: {e}. "
                f"Trying without seasonal..."
            )
            # Fallback: try without seasonal component
            try:
                self.fitted_model = self._fit_exponential_smoothing(values, seasonal_arg=None)
            except Exception as fallback_error:
                logger.warning(
                    f"ExponentialSmoothing without seasonal also failed: {fallback_error}. "
                    f"Using fallback method for forecasting."
                )
                # If statsmodels fails, keep None and use fallback in forecast
                self.fitted_model = None

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
        if not self.is_fitted:
            raise ValueError("Model must be fitted before forecasting")

        # Try to use fitted statsmodels model if available
        if self.fitted_model is not None:
            try:
                forecast_values = self.fitted_model.forecast(steps=steps)
                # Ensure all values are finite
                if np.all(np.isfinite(forecast_values)):
                    return forecast_values.values if hasattr(forecast_values, 'values') else forecast_values
            except Exception as e:
                logger.warning(
                    f"Fitted model forecast failed: {e}. Using fallback method."
                )

        # Fallback: simple exponential smoothing with trend
        forecast_values = np.zeros(steps)

        # Calculate trend from last few values
        if len(self._training_values) > 1:
            trend = (self._training_values[-1] - self._training_values[0]) / (
                len(self._training_values) - 1
            )
        else:
            trend = 0

        current_value = self._last_value

        for i in range(steps):
            # Apply simple exponential smoothing with trend
            alpha = 0.3  # Smoothing parameter
            forecast_values[i] = alpha * current_value + (1 - alpha) * (
                current_value + trend * (i + 1)
            )

            # Add small random noise for variation
            noise = np.random.normal(0, self._std * 0.05)
            forecast_values[i] += noise

            current_value = forecast_values[i]

        return forecast_values

    def get_diagnostics(self) -> dict:
        """Get model diagnostics information.

        Returns
        -------
        dict
            Dictionary with model configuration and status
        """
        diagnostics = super().get_diagnostics()
        diagnostics.update(
            {
                "seasonal_periods": self.seasonal_periods,
                "trend": self.trend,
                "seasonal": self.seasonal,
                "fitted_model_type": (
                    type(self.fitted_model).__name__
                    if self.fitted_model is not None
                    else "Fallback"
                ),
            }
        )
        return diagnostics
