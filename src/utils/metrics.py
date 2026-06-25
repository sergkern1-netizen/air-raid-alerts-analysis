"""Metrics for evaluating time series forecasts."""

import numpy as np
from typing import Union


def calculate_mae(actual: Union[np.ndarray, list], predicted: Union[np.ndarray, list]) -> float:
    """Calculate Mean Absolute Error.

    Parameters
    ----------
    actual : np.ndarray or list
        Actual values
    predicted : np.ndarray or list
        Predicted values

    Returns
    -------
    float
        Mean Absolute Error
    """
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    return np.mean(np.abs(actual - predicted))


def calculate_rmse(actual: Union[np.ndarray, list], predicted: Union[np.ndarray, list]) -> float:
    """Calculate Root Mean Squared Error.

    Parameters
    ----------
    actual : np.ndarray or list
        Actual values
    predicted : np.ndarray or list
        Predicted values

    Returns
    -------
    float
        Root Mean Squared Error
    """
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    return np.sqrt(np.mean((actual - predicted) ** 2))


def calculate_mape(actual: Union[np.ndarray, list], predicted: Union[np.ndarray, list]) -> float:
    """Calculate Mean Absolute Percentage Error.

    Parameters
    ----------
    actual : np.ndarray or list
        Actual values
    predicted : np.ndarray or list
        Predicted values

    Returns
    -------
    float
        Mean Absolute Percentage Error (as percentage)

    Notes
    -----
    If any actual value is 0, it will be replaced with 1e-10 to avoid division by zero.
    """
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    # Avoid division by zero
    actual = np.where(actual == 0, 1e-10, actual)

    return np.mean(np.abs((actual - predicted) / actual)) * 100


def calculate_metrics(actual: Union[np.ndarray, list], predicted: Union[np.ndarray, list]) -> dict:
    """Calculate all metrics at once.

    Parameters
    ----------
    actual : np.ndarray or list
        Actual values
    predicted : np.ndarray or list
        Predicted values

    Returns
    -------
    dict
        Dictionary with MAE, RMSE, and MAPE
    """
    return {
        'MAE': calculate_mae(actual, predicted),
        'RMSE': calculate_rmse(actual, predicted),
        'MAPE': calculate_mape(actual, predicted)
    }
