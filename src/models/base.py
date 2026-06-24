"""Base class for time series models."""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd


class TimeSeriesModel(ABC):
    """Abstract base class for time series forecasting models."""

    def __init__(self, name: str = None):
        """Initialize the base model.

        Parameters
        ----------
        name : str, optional
            Name of the model
        """
        self.name = name or self.__class__.__name__
        self.is_fitted = False
        self.model = None

    @abstractmethod
    def fit(self, data):
        """Fit the model to data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Training data
        """
        pass

    @abstractmethod
    def forecast(self, steps: int) -> np.ndarray:
        """Generate forecasts for future steps.

        Parameters
        ----------
        steps : int
            Number of steps ahead to forecast

        Returns
        -------
        np.ndarray
            Forecast values
        """
        pass

    def get_diagnostics(self) -> dict:
        """Get model diagnostics information.

        Returns
        -------
        dict
            Dictionary with model information
        """
        return {
            "name": self.name,
            "is_fitted": self.is_fitted,
        }
