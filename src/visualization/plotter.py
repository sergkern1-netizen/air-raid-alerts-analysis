import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional


class TimeSeriesPlotter:
    """Utility class for time series visualization and model comparison."""

    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """Initialize plotter with style."""
        self.style = style
        sns.set_style("darkgrid")

    def plot_series(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
        value_col: str = "value",
        title: str = "Time Series",
        figsize: tuple = (14, 5),
    ) -> plt.Figure:
        """Plot basic time series.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with timestamp and value columns
        timestamp_col : str
            Column name for timestamps
        value_col : str
            Column name for values
        title : str
            Plot title
        figsize : tuple
            Figure size (width, height)

        Returns
        -------
        plt.Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(df[timestamp_col], df[value_col], linewidth=1.5, label="Observed")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        return fig

    def plot_model_comparison(
        self,
        df: pd.DataFrame,
        forecasts: Dict[str, np.ndarray],
        timestamp_col: str = "ds",
        value_col: str = "y",
        title: str = "Model Forecast Comparison",
        figsize: tuple = (16, 8),
    ) -> plt.Figure:
        """Plot actual values and forecasts from multiple models.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with actual data
        forecasts : dict
            Dictionary mapping model names to forecast arrays
        timestamp_col : str
            Column name for timestamps
        value_col : str
            Column name for values
        title : str
            Plot title
        figsize : tuple
            Figure size

        Returns
        -------
        plt.Figure
            Matplotlib figure with actual and forecast lines
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Plot actual values
        ax.plot(
            df[timestamp_col],
            df[value_col],
            label="Actual",
            linewidth=2.5,
            color="black",
            marker="o",
            markersize=4,
        )

        # Plot forecasts from each model
        colors = ["red", "blue", "green", "orange", "purple", "brown"]
        last_date = df[timestamp_col].iloc[-1]
        freq = pd.infer_freq(df[timestamp_col])

        for i, (model_name, forecast) in enumerate(forecasts.items()):
            forecast_dates = pd.date_range(
                start=last_date, periods=len(forecast) + 1, freq=freq
            )[1:]
            color = colors[i % len(colors)]
            ax.plot(
                forecast_dates,
                forecast,
                label=f"{model_name} Forecast",
                linestyle="--",
                linewidth=2,
                color=color,
                marker="s",
                markersize=6,
            )

        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10, loc="best")
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        return fig

    def plot_metrics_comparison(
        self,
        results: list,
        title: str = "Model Performance Comparison",
        figsize: tuple = (12, 6),
    ) -> plt.Figure:
        """Plot comparison of model metrics (MAE, RMSE, MAPE).

        Parameters
        ----------
        results : list
            List of result dicts from compare_models function
        title : str
            Plot title
        figsize : tuple
            Figure size

        Returns
        -------
        plt.Figure
            Matplotlib figure with 3 metric subplots
        """
        # Extract data
        models = [r["Model"] for r in results]
        mae_values = [r.get("MAE", 0) for r in results]
        rmse_values = [r.get("RMSE", 0) for r in results]
        mape_values = [r.get("MAPE", 0) for r in results]

        # Filter out None values
        valid_indices = [i for i, m in enumerate(mae_values) if m is not None]

        if not valid_indices:
            print("No valid metrics to plot")
            return None

        models = [models[i] for i in valid_indices]
        mae_values = [mae_values[i] for i in valid_indices]
        rmse_values = [rmse_values[i] for i in valid_indices]
        mape_values = [mape_values[i] for i in valid_indices]

        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=figsize)

        # MAE comparison
        axes[0].bar(models, mae_values, color="skyblue", edgecolor="navy", alpha=0.7)
        axes[0].set_ylabel("MAE", fontsize=11)
        axes[0].set_title("Mean Absolute Error", fontsize=12, fontweight="bold")
        axes[0].grid(axis="y", alpha=0.3)

        # RMSE comparison
        axes[1].bar(
            models, rmse_values, color="lightcoral", edgecolor="darkred", alpha=0.7
        )
        axes[1].set_ylabel("RMSE", fontsize=11)
        axes[1].set_title("Root Mean Squared Error", fontsize=12, fontweight="bold")
        axes[1].grid(axis="y", alpha=0.3)

        # MAPE comparison
        axes[2].bar(
            models, mape_values, color="lightgreen", edgecolor="darkgreen", alpha=0.7
        )
        axes[2].set_ylabel("MAPE (%)", fontsize=11)
        axes[2].set_title(
            "Mean Absolute Percentage Error", fontsize=12, fontweight="bold"
        )
        axes[2].grid(axis="y", alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight="bold")
        fig.tight_layout()
        return fig
