#!/usr/bin/env python
"""Create forecast visualization for all models on real data"""

import sys
import warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
from src.models.prophet import ProphetModel
from src.models.lstm import LSTMModel
from src.models.exponential_smoothing import ExponentialSmoothingModel
from src.models.ensemble import ModelEnsemble

# Load real data
df = pd.read_csv('data/processed/01_daily_aggregates.csv')
df['date'] = pd.to_datetime(df['date'])
data = df['alerts_count_combined'].values

print("[1/5] Loading data...")
print(f"  Loaded {len(df)} days, range: {df['date'].min().date()} to {df['date'].max().date()}")

# Train models
print("[2/5] Training models...")

# Prophet
df_prophet = pd.DataFrame({'ds': df['date'], 'y': data})
prophet_model = ProphetModel()
prophet_model.fit(df_prophet)
prophet_forecast = prophet_model.forecast(7)

# LSTM
lstm_model = LSTMModel(lookback=30)
lstm_model.fit(data)
lstm_forecast = lstm_model.forecast(7)

# Exponential Smoothing
es_model = ExponentialSmoothingModel(seasonal_periods=30)
es_model.fit(data)
es_forecast = es_model.forecast(7)

# Ensemble
ensemble = ModelEnsemble()
ensemble.add_model('Prophet', ProphetModel())
ensemble.add_model('LSTM', LSTMModel(lookback=30))
ensemble.add_model('ExponentialSmoothing', ExponentialSmoothingModel(seasonal_periods=30))
ensemble.fit(data)
ensemble_forecast = ensemble.ensemble_forecast(7, method='mean')

print("  [OK] All models trained")

# Create forecast dates
last_date = df['date'].max()
forecast_dates = [last_date + timedelta(days=i+1) for i in range(7)]

# Create visualization
print("[3/5] Creating visualization...")

fig, axes = plt.subplots(2, 1, figsize=(16, 10))

# Plot 1: Full history + forecasts
ax1 = axes[0]
ax1.plot(df['date'], data, 'k-', linewidth=2, label='Historical Data', alpha=0.7)
ax1.plot(forecast_dates, prophet_forecast, 'o-', linewidth=2.5, label='Prophet', markersize=8, color='#1f77b4')
ax1.plot(forecast_dates, lstm_forecast, 's-', linewidth=2.5, label='LSTM', markersize=8, color='#ff7f0e')
ax1.plot(forecast_dates, es_forecast, '^-', linewidth=2.5, label='Exp. Smoothing', markersize=8, color='#2ca02c')
ax1.plot(forecast_dates, ensemble_forecast, 'D-', linewidth=3, label='Ensemble (Mean)', markersize=9, color='#d62728', alpha=0.8)

ax1.axvline(x=last_date, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Forecast Start')
ax1.set_title('Air Raid Alerts: 7-Day Forecast (All Models)', fontsize=16, fontweight='bold')
ax1.set_ylabel('Number of Alerts', fontsize=12)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Plot 2: Last 90 days + forecasts (zoomed)
ax2 = axes[1]
last_90_idx = max(0, len(df) - 90)
df_90 = df.iloc[last_90_idx:]

ax2.plot(df_90['date'], df_90['alerts_count_combined'], 'k-', linewidth=2, label='Historical Data (Last 90 days)', alpha=0.7)
ax2.plot(forecast_dates, prophet_forecast, 'o-', linewidth=2.5, label='Prophet', markersize=8, color='#1f77b4')
ax2.plot(forecast_dates, lstm_forecast, 's-', linewidth=2.5, label='LSTM', markersize=8, color='#ff7f0e')
ax2.plot(forecast_dates, es_forecast, '^-', linewidth=2.5, label='Exp. Smoothing', markersize=8, color='#2ca02c')
ax2.plot(forecast_dates, ensemble_forecast, 'D-', linewidth=3, label='Ensemble (Mean)', markersize=9, color='#d62728', alpha=0.8)

ax2.axvline(x=last_date, color='gray', linestyle='--', linewidth=2, alpha=0.5)
ax2.fill_between(forecast_dates,
                  [min(prophet_forecast[i], lstm_forecast[i], es_forecast[i]) for i in range(7)],
                  [max(prophet_forecast[i], lstm_forecast[i], es_forecast[i]) for i in range(7)],
                  alpha=0.2, color='gray', label='Model Range')

ax2.set_title('Air Raid Alerts: 7-Day Forecast - Recent Trend (Last 90 Days)', fontsize=16, fontweight='bold')
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Number of Alerts', fontsize=12)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('figures/forecast_comparison.png', dpi=300, bbox_inches='tight')
print("  [OK] Saved: figures/forecast_comparison.png")

# Create forecast table
print("[4/5] Creating forecast table...")

forecast_table = pd.DataFrame({
    'Date': forecast_dates,
    'Prophet': [round(v, 1) for v in prophet_forecast],
    'LSTM': [round(v, 1) for v in lstm_forecast],
    'Exp.Smoothing': [round(v, 1) for v in es_forecast],
    'Ensemble': [round(v, 1) for v in ensemble_forecast]
})

# Save table
forecast_table.to_csv('figures/forecast_table.csv', index=False)
print("  [OK] Saved: figures/forecast_table.csv")

print("\n[5/5] Summary Statistics")
print("=" * 60)
print(f"Last Historical Value: {data[-1]:.1f} alerts")
print(f"7-Day Average Forecast:")
print(f"  Prophet:          {np.mean(prophet_forecast):.1f}")
print(f"  LSTM:             {np.mean(lstm_forecast):.1f}")
print(f"  Exp. Smoothing:   {np.mean(es_forecast):.1f}")
print(f"  Ensemble (Mean):  {np.mean(ensemble_forecast):.1f}")
print("=" * 60)

print("\n[SUCCESS] Visualization complete!")
print("\nFiles created:")
print("  1. figures/forecast_comparison.png")
print("  2. figures/forecast_table.csv")
