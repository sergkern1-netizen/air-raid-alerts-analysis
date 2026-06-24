# src/analyzer.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple

class TimeSeriesAnalyzer:
    """Analyze air raid alerts time series"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp')

    def basic_statistics(self) -> Dict:
        """Calculate basic statistics"""
        daily = self.df.groupby(self.df['timestamp'].dt.date).size()

        return {
            'total_alerts': len(self.df),
            'date_range': (self.df['timestamp'].min(), self.df['timestamp'].max()),
            'daily_mean': daily.mean(),
            'daily_std': daily.std(),
            'daily_min': daily.min(),
            'daily_max': daily.max(),
            'days_with_alerts': (daily > 0).sum(),
            'total_days': len(daily),
        }

    def hourly_pattern(self) -> pd.Series:
        """Detect hourly patterns"""
        hourly = self.df.groupby(self.df['timestamp'].dt.hour).size()
        return hourly / len(self.df) * 100  # Percentage

    def weekly_pattern(self) -> pd.Series:
        """Detect weekly patterns (day of week)"""
        weekly = self.df.groupby(self.df['timestamp'].dt.dayofweek).size()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly.index = [days[i] for i in weekly.index]
        return weekly

    def monthly_trend(self) -> pd.Series:
        """Get monthly aggregation"""
        monthly = self.df.groupby(self.df['timestamp'].dt.to_period('M')).size()
        return monthly

    def regional_distribution(self) -> pd.Series:
        """Get alerts by region if available"""
        if 'region' in self.df.columns:
            return self.df['region'].value_counts()
        elif 'oblast' in self.df.columns:
            return self.df['oblast'].value_counts()
        return None

    def plot_daily_timeline(self, figsize: Tuple = (14, 6)) -> plt.Figure:
        """Plot daily alert counts"""
        daily = self.df.groupby(self.df['timestamp'].dt.date).size()

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(daily.index, daily.values, linewidth=1.5, color='darkred')
        ax.fill_between(daily.index, daily.values, alpha=0.3, color='red')
        ax.set_title('Daily Air Raid Alerts', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Alerts')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig

    def plot_hourly_pattern(self, figsize: Tuple = (12, 5)) -> plt.Figure:
        """Plot hourly distribution"""
        hourly = self.hourly_pattern()

        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(hourly.index, hourly.values, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_title('Alert Distribution by Hour of Day', fontsize=12, fontweight='bold')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Percentage of Alerts (%)')
        ax.set_xticks(range(0, 24, 2))
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        return fig

    def plot_monthly_trend(self, figsize: Tuple = (14, 5)) -> plt.Figure:
        """Plot monthly trend"""
        monthly = self.monthly_trend()

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(range(len(monthly)), monthly.values, marker='o', linewidth=2, markersize=6, color='green')
        ax.set_title('Monthly Alert Trend', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Alerts')
        ax.set_xticks(range(0, len(monthly), max(1, len(monthly)//10)))
        ax.set_xticklabels([str(m) for m in monthly.index[::max(1, len(monthly)//10)]], rotation=45)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig

    def arima_forecast(self, steps: int = 7, order: Tuple = (1, 1, 1)) -> Tuple[np.ndarray, Dict]:
        """Forecast with ARIMA model"""
        from statsmodels.tsa.arima.model import ARIMA

        daily = self.df.groupby(self.df['timestamp'].dt.date).size()

        try:
            model = ARIMA(daily.values, order=order)
            results = model.fit()

            forecast_result = results.get_forecast(steps=steps)
            # predicted_mean is already a numpy array
            forecast_values = np.asarray(forecast_result.predicted_mean)
            conf_int_df = forecast_result.conf_int()
            conf_int = np.asarray(conf_int_df)

            return forecast_values, {
                'model': results,
                'aic': results.aic,
                'bic': results.bic,
                'rmse': np.sqrt(np.mean(results.resid**2)),
                'conf_int': conf_int,
            }
        except Exception as e:
            print(f"ARIMA error: {e}")
            return None, None

    def plot_forecast(self, steps: int = 7, figsize: Tuple = (14, 6)) -> Tuple[plt.Figure, Dict]:
        """Plot ARIMA forecast"""
        daily = self.df.groupby(self.df['timestamp'].dt.date).size()
        forecast_values, model_info = self.arima_forecast(steps=steps)

        if forecast_values is None:
            return None, None

        last_date = self.df['timestamp'].max().date()
        future_dates = pd.date_range(start=last_date, periods=steps+1, freq='D')[1:]

        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(daily.index, daily.values, label='Observed', linewidth=2, color='darkblue')
        ax.plot(future_dates.date, forecast_values, label='Forecast', linewidth=2,
                color='red', linestyle='--', marker='o')

        conf_int = model_info['conf_int']
        ax.fill_between(future_dates.date,
                        conf_int[:, 0],
                        conf_int[:, 1],
                        alpha=0.2, color='red', label='95% Confidence')

        ax.set_title('ARIMA(1,1,1) Forecast - Next 7 Days', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Alerts')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig, model_info
