"""Model ensemble for comparative analysis of time series forecasts."""

from typing import Dict, List, Union
import numpy as np
import pandas as pd

from .base import TimeSeriesModel

def calculate_mae(y_true, y_pred):
    """Calculate Mean Absolute Error."""
    import numpy as np
    return np.mean(np.abs(y_true - y_pred))

def calculate_rmse(y_true, y_pred):
    """Calculate Root Mean Squared Error."""
    import numpy as np
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error."""
    import numpy as np
    return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100


class ModelEnsemble:
    """Ensemble of time series models for comparative analysis.

    Allows combining multiple models and generating forecasts from all of them
    for comparison and ensemble averaging.
    """

    def __init__(self):
        """Initialize an empty model ensemble."""
        self.models: Dict[str, TimeSeriesModel] = {}
        self.fitted = False

    def add_model(self, name: str, model: TimeSeriesModel) -> None:
        """Add a model to the ensemble.

        Parameters
        ----------
        name : str
            Name/identifier for the model
        model : TimeSeriesModel
            Model instance (must inherit from TimeSeriesModel)

        Raises
        ------
        TypeError
            If model is not an instance of TimeSeriesModel
        """
        if not isinstance(model, TimeSeriesModel):
            raise TypeError("Model must be an instance of TimeSeriesModel")

        self.models[name] = model

    def fit(self, data: Union[pd.DataFrame, np.ndarray]) -> None:
        """Fit all models in the ensemble.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Training data. If DataFrame, must contain 'ds' and 'y' columns.

        Raises
        ------
        ValueError
            If ensemble is empty
        """
        if not self.models:
            raise ValueError("Ensemble is empty. Add models before fitting.")

        for name, model in self.models.items():
            model.fit(data)

        self.fitted = True

    def forecast(self, steps: int) -> Dict[str, np.ndarray]:
        """Generate forecasts from all models in the ensemble.

        Parameters
        ----------
        steps : int
            Number of steps ahead to forecast

        Returns
        -------
        dict
            Dictionary with model names as keys and forecast arrays as values

        Raises
        ------
        ValueError
            If ensemble is not fitted
        """
        if not self.fitted:
            raise ValueError("Ensemble must be fitted before forecasting")

        forecasts = {}
        for name, model in self.models.items():
            forecasts[name] = model.forecast(steps)

        return forecasts

    def ensemble_forecast(self, steps: int, method: str = "mean") -> np.ndarray:
        """Generate ensemble forecast by combining individual forecasts.

        Parameters
        ----------
        steps : int
            Number of steps ahead to forecast
        method : str, optional
            Method for combining forecasts: "mean", "median", "min", "max"
            Default: "mean"

        Returns
        -------
        np.ndarray
            Combined forecast array

        Raises
        ------
        ValueError
            If ensemble is not fitted or invalid method
        """
        if not self.fitted:
            raise ValueError("Ensemble must be fitted before forecasting")

        forecasts = self.forecast(steps)

        # Stack all forecasts
        forecast_array = np.array(list(forecasts.values()))

        # Combine using specified method
        if method == "mean":
            return np.mean(forecast_array, axis=0)
        elif method == "median":
            return np.median(forecast_array, axis=0)
        elif method == "min":
            return np.min(forecast_array, axis=0)
        elif method == "max":
            return np.max(forecast_array, axis=0)
        else:
            raise ValueError(
                f"Unknown method '{method}'. Use 'mean', 'median', 'min', or 'max'"
            )

    def get_summary(self) -> pd.DataFrame:
        """Get summary of models in the ensemble.

        Returns
        -------
        pd.DataFrame
            DataFrame with model names and diagnostics
        """
        summaries = []
        for name, model in self.models.items():
            diagnostics = model.get_diagnostics()
            diagnostics["Name"] = name
            summaries.append(diagnostics)

        return pd.DataFrame(summaries)


def compare_models(
    models_list: List[TimeSeriesModel],
    train_data: pd.DataFrame,
    test_data: pd.DataFrame,
    steps: int = 7,
) -> List[Dict]:
    """Compare multiple models on train and test data.

    Parameters
    ----------
    models_list : list of TimeSeriesModel
        List of model instances to compare
    train_data : pd.DataFrame
        Training dataset with 'ds' and 'y' columns
    test_data : pd.DataFrame
        Test dataset with 'ds' and 'y' columns
    steps : int, optional
        Number of steps to forecast (default: 7)

    Returns
    -------
    list of dict
        List of result dictionaries with keys:
        - "Model": model name
        - "MAE": Mean Absolute Error
        - "RMSE": Root Mean Squared Error
        - "MAPE": Mean Absolute Percentage Error
    """
    results = []

    for model in models_list:
        # Fit model on training data
        model.fit(train_data)

        # Generate forecasts for test period
        forecast = model.forecast(steps)

        # Get actual test values
        actual = test_data["y"].values[:steps]

        # Calculate metrics
        mae = calculate_mae(actual, forecast)
        rmse = calculate_rmse(actual, forecast)
        mape = calculate_mape(actual, forecast)

        # Store results
        results.append(
            {
                "Model": model.name,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape,
            }
        )

    return results
