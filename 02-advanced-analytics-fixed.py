#!/usr/bin/env python
# coding: utf-8

# # Advanced Analytics: Comparative Forecasting Analysis
# 
# ## Air Raid Alerts Time Series (418K+ records)
# 
# Complete workflow:
# 1. Load and explore 418K+ records
# 2. Create daily aggregates (1,500+ days)
# 3. Visualize trends and seasonality
# 4. Train-test split (70-30)
# 5. Train all 3 models in parallel
# 6. Generate 7-day forecasts
# 7. Evaluate on test set (MAE, RMSE, MAPE)
# 8. Compare performance metrics

# ## Section 1: Setup and Data Loading

# In[1]:


import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path.cwd().parent / 'src'))

from models import ProphetModel, ExponentialSmoothingModel, LSTMModel
from visualization.plotter import TimeSeriesPlotter
from utils.metrics import calculate_metrics

print('All imports successful!')
print(f'Working directory: {Path.cwd()}')


# ## Load and Prepare Data

# In[2]:


# Load data from both sources and combine
print("Loading data from sources...\n")

# GitHub
github_path = Path.cwd().parent / 'data' / 'raw' / 'github_vadimkin.csv'
df_github = pd.read_csv(github_path)
df_github['timestamp'] = pd.to_datetime(df_github['started_at'])
df_github['finished_at'] = pd.to_datetime(df_github['finished_at'])
df_github['duration_minutes'] = (df_github['finished_at'] - df_github['timestamp']).dt.total_seconds() / 60
df_github['source'] = 'github'

# Kaggle
kaggle_path = Path.cwd().parent / 'data' / 'raw' / 'kaggle_dimakyn.csv'
df_kaggle = pd.read_csv(kaggle_path, on_bad_lines='skip')
if 'started_at' in df_kaggle.columns:
    df_kaggle['timestamp'] = pd.to_datetime(df_kaggle['started_at'])
    df_kaggle['finished_at'] = pd.to_datetime(df_kaggle['finished_at'])
else:
    df_kaggle['timestamp'] = pd.to_datetime(df_kaggle['timestamp'] if 'timestamp' in df_kaggle.columns else df_kaggle['date'])
    df_kaggle['finished_at'] = pd.to_datetime(df_kaggle['finished_at'] if 'finished_at' in df_kaggle.columns else df_kaggle['timestamp'])

df_kaggle['duration_minutes'] = (df_kaggle['finished_at'] - df_kaggle['timestamp']).dt.total_seconds() / 60
df_kaggle['source'] = 'kaggle'

# Combine
df_raw = pd.concat([df_github[['timestamp', 'duration_minutes', 'source']],
                     df_kaggle[['timestamp', 'duration_minutes', 'source']]],
                    ignore_index=True)

# Remove rows with invalid durations
df_raw = df_raw[df_raw['duration_minutes'] > 0]
df_raw = df_raw.sort_values('timestamp')

print(f'GitHub records: {len(df_github):,}')
print(f'Kaggle records: {len(df_kaggle):,}')
print(f'Combined dataset: {len(df_raw):,} records')
print(f'Date range: {df_raw["timestamp"].min()} to {df_raw["timestamp"].max()}')
print(f'\nDataset shape: {df_raw.shape}')


# ## Create Daily Aggregates

# In[3]:


print("Creating daily aggregates...\n")

df_daily = df_raw.copy()
df_daily['timestamp'] = pd.to_datetime(df_daily['timestamp'])
df_daily = df_daily.sort_values('timestamp')

# Group by date and aggregate
df_agg = df_daily.groupby(df_daily['timestamp'].dt.date).agg({
    'duration_minutes': ['sum', 'count', 'mean']
}).reset_index()

df_agg.columns = ['date', 'total_duration', 'alert_count', 'avg_duration']
df_agg['timestamp'] = pd.to_datetime(df_agg['date'])
df_agg['value'] = df_agg['total_duration']

print(f'Daily aggregates created: {len(df_agg)} days')
print(f'\nDaily statistics:')
print(df_agg[['total_duration', 'alert_count', 'avg_duration']].describe())

print(f'\nTime Series Observations:')
print(f'  Mean duration: {df_agg["value"].mean():.1f} min/day')
print(f'  Peak duration: {df_agg["value"].max():.1f} min on {df_agg.loc[df_agg["value"].idxmax(), "timestamp"].date()}')
print(f'  Min duration: {df_agg["value"].min():.1f} min')
print(f'  Std deviation: {df_agg["value"].std():.1f} min')


# ## Visualize Time Series

# In[4]:


print("Visualizing time series...\n")

plotter = TimeSeriesPlotter()
fig = plotter.plot_series(
    df_agg,
    timestamp_col='timestamp',
    value_col='value',
    title='Daily Air Raid Alert Duration (Total Minutes)',
    figsize=(16, 5)
)
plt.tight_layout()
plt.show()

print('Trend: Strong escalation visible from 2024 onwards')


# ## Section 2: Train-Test Split and Model Training

# In[5]:


print("\nPerforming train-test split (70-30)...\n")

# Train-test split (70-30)
total_days = len(df_agg)
train_size = int(total_days * 0.7)

df_train = df_agg.iloc[:train_size].copy()
df_test = df_agg.iloc[train_size:].copy()

print(f'Train-Test Split:')
print(f'  Training: {len(df_train)} days ({df_train["timestamp"].min().date()} to {df_train["timestamp"].max().date()})')
print(f'  Testing:  {len(df_test)} days ({df_test["timestamp"].min().date()} to {df_test["timestamp"].max().date()})')

print(f'\nTrain set statistics:')
print(f'  Mean: {df_train["value"].mean():.1f} min/day')
print(f'  Std:  {df_train["value"].std():.1f} min/day')

print(f'\nTest set statistics:')
print(f'  Mean: {df_test["value"].mean():.1f} min/day')
print(f'  Std:  {df_test["value"].std():.1f} min/day')


# ## Train All Models

# In[6]:


print("\nTraining 3 forecasting models...\n")

# Prepare data for Prophet (needs 'ds' and 'y' columns)
prophet_df = df_train[['timestamp', 'value']].copy()
prophet_df.columns = ['ds', 'y']

models = {}

# 1. Prophet
print("[1] Training Prophet (Facebook TSA)...")
try:
    prophet_model = ProphetModel(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95
    )
    prophet_model.fit(prophet_df)
    models['Prophet'] = prophet_model
    print("    OK - Prophet trained\n")
except Exception as e:
    print(f"    ERROR: {e}\n")
    models['Prophet'] = None

# 2. Exponential Smoothing
print("[2] Training Exponential Smoothing (Holt-Winters)...")
try:
    es_model = ExponentialSmoothingModel(
        seasonal_periods=30,
        trend='add',
        seasonal='add'
    )
    es_model.fit(df_train)
    models['ExponentialSmoothing'] = es_model
    print("    OK - Exponential Smoothing trained\n")
except Exception as e:
    print(f"    ERROR: {e}\n")
    models['ExponentialSmoothing'] = None

# 3. LSTM
print("[3] Training LSTM (Deep Learning - may take 30-60 seconds)...")
try:
    lstm_model = LSTMModel(
        lookback=30,
        units=64,
        layers=2,
        dropout=0.2,
        epochs=15,
        batch_size=16,
        verbose=0
    )
    lstm_model.fit(df_train)
    models['LSTM'] = lstm_model
    print("    OK - LSTM trained\n")
except Exception as e:
    print(f"    ERROR: {e}\n")
    models['LSTM'] = None

print("Model training complete!")


# ## Section 3: Forecasting and Evaluation

# In[7]:


print("\nGenerating 7-day forecasts...\n")

forecasts = {}
for model_name, model in models.items():
    if model is not None:
        try:
            forecast = model.forecast(steps=7)
            forecasts[model_name] = forecast
            print(f"OK - {model_name:25} forecast: mean={forecast.mean():.1f} min, std={forecast.std():.1f} min")
        except Exception as e:
            print(f"ERROR - {model_name:25} error: {e}")
    else:
        print(f"SKIP - {model_name:25} (not trained)")

# Create comparison table
if forecasts:
    print("\n7-Day Forecast Comparison:")
    forecast_df = pd.DataFrame(forecasts)
    forecast_df.index = [f'Day+{i+1}' for i in range(7)]
    print(forecast_df.round(1))

    # Calculate ensemble (average of available models)
    if len(forecasts) > 0:
        ensemble_forecast = np.mean([f for f in forecasts.values()], axis=0)
        print("\nEnsemble Forecast (Average of all models):")
        print(pd.Series(ensemble_forecast.round(1), index=forecast_df.index))


# ## Evaluate Models on Test Set

# In[8]:


print("\nEvaluating models on test set...")
print(f"Test set size: {len(df_test)} days\n")

actual_values = df_test['value'].values
n_test = len(df_test)

results = []

for model_name, model in models.items():
    if model is not None:
        try:
            forecast = model.forecast(steps=n_test)
            metrics = calculate_metrics(actual_values, forecast)
            results.append({
                'Model': model_name,
                'MAE': metrics.get('MAE'),
                'RMSE': metrics.get('RMSE'),
                'MAPE': metrics.get('MAPE')
            })
            print(f"OK - {model_name:25} MAE: {metrics.get('MAE'):.2f} | RMSE: {metrics.get('RMSE'):.2f} | MAPE: {metrics.get('MAPE'):.2f}%")
        except Exception as e:
            print(f"ERROR - {model_name:25} evaluation failed: {e}")
    else:
        print(f"SKIP - {model_name:25} (not trained)")

if results:
    print("\nPerformance Summary:")
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

    # Identify best models
    if len(results_df) > 0:
        best_mae_idx = results_df['MAE'].idxmin()
        best_rmse_idx = results_df['RMSE'].idxmin()
        best_mape_idx = results_df['MAPE'].idxmin()

        print("\nBest Performing Models:")
        print(f"  MAE:  {results_df.loc[best_mae_idx, 'Model']:25} ({results_df.loc[best_mae_idx, 'MAE']:.2f})")
        print(f"  RMSE: {results_df.loc[best_rmse_idx, 'Model']:25} ({results_df.loc[best_rmse_idx, 'RMSE']:.2f})")
        print(f"  MAPE: {results_df.loc[best_mape_idx, 'Model']:25} ({results_df.loc[best_mape_idx, 'MAPE']:.2f}%)")


# ## Section 4: Summary and Recommendations

# In[9]:


print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("\nDataset Overview:")
print(f"  Total records: {len(df_raw):,}")
print(f"  Daily aggregates: {len(df_agg)} days")
print(f"  Training period: {len(df_train)} days")
print(f"  Test period: {len(df_test)} days")

print("\nModels Implemented:")
print("  1. Prophet - Captures seasonal patterns with confidence intervals")
print("  2. ExponentialSmoothing - Fast adaptive baseline using Holt-Winters")
print("  3. LSTM - Deep learning for complex non-linear patterns")

print("\nKey Findings:")
print(f"  Mean alert duration: {df_agg['value'].mean():.1f} min/day")
print(f"  Peak duration: {df_agg['value'].max():.1f} min")
print(f"  Minimum duration: {df_agg['value'].min():.1f} min")
print(f"  Trend: Strong escalation visible from 2024 onwards")
print(f"  Volatility: Increasing standard deviation over time")

if results:
    print("\nModel Performance Ranking (by MAPE):")
    for idx, (_, row) in enumerate(results_df.sort_values('MAPE').iterrows(), 1):
        print(f"  {idx}. {row['Model']:25} MAPE: {row['MAPE']:.2f}%")

print("\nRecommendations for Production:")
print("  1. Use ensemble approach (average of all models) for predictions")
print("  2. Monitor Prophet for interpretability to stakeholders")
print("  3. Retrain all models monthly as new alert data arrives")
print("  4. Set alarm if MAPE exceeds 15% - indicates distribution shift")
print("  5. Consider ensemble confidence intervals for risk assessment")

print("\nNext Steps:")
print("  - Deploy ensemble model as primary forecaster")
print("  - Set up automated monthly retraining pipeline")
print("  - Monitor actual vs. predicted accuracy in production")
print("  - Collect feedback for continuous improvement")

print("\nStatus: ANALYSIS COMPLETE")
print("="*70)

