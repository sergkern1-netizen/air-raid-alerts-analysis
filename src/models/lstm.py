"""LSTM Deep Learning time series model implementation."""

import warnings
import numpy as np
import pandas as pd
from typing import Union, Tuple
from sklearn.preprocessing import MinMaxScaler

from .base import TimeSeriesModel

# Suppress warnings
warnings.filterwarnings("ignore")


class LSTMModel(TimeSeriesModel):
    """LSTM (Long Short-Term Memory) neural network for time series forecasting.

    Implements LSTM-based forecasting using TensorFlow/Keras.
    """

    def __init__(
        self,
        lookback: int = 30,
        units: int = 50,
        layers: int = 1,
        dropout: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.1,
        verbose: int = 1,
        name: str = "LSTM",
    ):
        """Initialize LSTMModel.

        Parameters
        ----------
        lookback : int, optional
            Number of past time steps to use as input (default: 30)
        units : int, optional
            Number of LSTM units (default: 50)
        layers : int, optional
            Number of LSTM layers (default: 1)
        dropout : float, optional
            Dropout rate for regularization (default: 0.2)
        epochs : int, optional
            Number of training epochs (default: 50)
        batch_size : int, optional
            Batch size for training (default: 32)
        validation_split : float, optional
            Fraction of data to use for validation (default: 0.1)
        verbose : int, optional
            Verbosity level (0=silent, 1=progress bar, 2=one line per epoch)
        name : str, optional
            Name of the model (default: "LSTM")
        """
        super().__init__(name=name)
        self.lookback = lookback
        self.units = units
        self.layers = layers
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.verbose = verbose

        # Will be set during fit
        self._scaler = None
        self._last_sequence = None
        self._training_values = None

    def _normalize_data(self, data: np.ndarray) -> Tuple[np.ndarray, MinMaxScaler]:
        """Normalize data using MinMaxScaler.

        Parameters
        ----------
        data : np.ndarray
            Raw data array

        Returns
        -------
        Tuple[np.ndarray, MinMaxScaler]
            Normalized data and the scaler object
        """
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Reshape data for scaler (needs 2D input)
        data_reshaped = data.reshape(-1, 1)
        normalized = scaler.fit_transform(data_reshaped).flatten()
        return normalized, scaler

    def _create_sequences(self, data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training.

        Parameters
        ----------
        data : np.ndarray
            Normalized time series data
        lookback : int
            Number of past time steps to use as input

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            X (input sequences) of shape (n_sequences, lookback)
            y (target values) of shape (n_sequences,)
        """
        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i:i + lookback])
            y.append(data[i + lookback])
        return np.array(X), np.array(y)

    def fit(self, data: Union[pd.DataFrame, np.ndarray]) -> None:
        """Fit the LSTM model to data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Training data. If DataFrame, must contain 'value' column.
            If numpy array, will be used directly.

        Raises
        ------
        ValueError
            If DataFrame doesn't contain required columns
        ImportError
            If TensorFlow is not installed
        """
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
        except ImportError:
            raise ImportError("TensorFlow is required for LSTM model. Install with: pip install tensorflow")

        # Convert to values array
        if isinstance(data, pd.DataFrame):
            if "value" not in data.columns:
                raise ValueError("DataFrame must contain 'value' column")
            values = data["value"].values
        elif isinstance(data, np.ndarray):
            values = data
        else:
            raise ValueError("Data must be pandas DataFrame or numpy array")

        # Store original training values
        self._training_values = values.copy()

        # Normalize data
        normalized_data, scaler = self._normalize_data(values)
        self._scaler = scaler

        # Create sequences
        X, y = self._create_sequences(normalized_data, self.lookback)

        # Reshape X for LSTM input (samples, timesteps, features)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        # Build LSTM model
        model = Sequential()

        # Add LSTM layers
        for i in range(self.layers):
            return_sequences = i < self.layers - 1  # Return sequences except for last layer
            model.add(LSTM(
                self.units,
                activation='relu',
                return_sequences=return_sequences,
                input_shape=(self.lookback, 1) if i == 0 else None
            ))
            if self.dropout > 0:
                model.add(Dropout(self.dropout))

        # Add output layer
        model.add(Dense(1))

        # Compile model
        model.compile(optimizer='adam', loss='mse')

        # Train model
        model.fit(
            X, y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            verbose=self.verbose
        )

        # Store model and last sequence for forecasting
        self.model = model
        self._last_sequence = normalized_data[-self.lookback:].copy()
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
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted before forecasting")

        forecast_values = []
        current_sequence = self._last_sequence.copy()

        # Iteratively predict next steps
        for _ in range(steps):
            # Reshape for model input (1 sample, lookback timesteps, 1 feature)
            current_sequence_reshaped = current_sequence.reshape(1, self.lookback, 1)

            # Predict next value
            next_value = self.model.predict(current_sequence_reshaped, verbose=0)[0, 0]
            forecast_values.append(next_value)

            # Update sequence for next iteration
            current_sequence = np.append(current_sequence[1:], next_value)

        # Convert normalized forecast to original scale
        forecast_array = np.array(forecast_values).reshape(-1, 1)
        forecast_denormalized = self._scaler.inverse_transform(forecast_array).flatten()

        return forecast_denormalized

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
                "lookback": self.lookback,
                "units": self.units,
                "layers": self.layers,
                "dropout": self.dropout,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "scaler_fitted": self._scaler is not None,
            }
        )
        return diagnostics
