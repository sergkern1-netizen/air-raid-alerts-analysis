#!/usr/bin/env python
"""Demonstration script: train and compare all time series models on air raid alerts data."""

import numpy as np
import pandas as pd
from datetime import datetime
from src.loader import DataLoader
from src.models.arima import ARIMAModel
from src.models.lstm import LSTMModel
from src.models.prophet import ProphetModel
from src.models.exponential_smoothing import ExponentialSmoothingModel
from src.models.ensemble import ModelEnsemble

def main():
    print("=" * 80)
    print("AIR RAID ALERTS TIME SERIES — COMPLETE MODEL DEMONSTRATION")
    print("=" * 80)
    print()

    # Load data
    print("[*] ЗАГРУЗКА ДАННЫХ...")
    loader = DataLoader()

    print("   - Загрузка GitHub источника...", end=" ", flush=True)
    github_data = loader.load_github()
    print(f"OK ({len(github_data)} записей)")

    print("   - Загрузка Kaggle источника...", end=" ", flush=True)
    kaggle_data = loader.load_kaggle()
    print(f"OK ({len(kaggle_data)} записей)")

    print()

    # Combine and aggregate to daily level
    print("[*] ПОДГОТОВКА ДАННЫХ...")

    # Normalize timestamps - convert to string then back to remove TZ issues
    github_data_copy = github_data.copy()
    kaggle_data_copy = kaggle_data.copy()

    github_data_copy['timestamp'] = pd.to_datetime(github_data_copy['timestamp']).astype(str).str[:10]
    kaggle_data_copy['timestamp'] = pd.to_datetime(kaggle_data_copy['timestamp']).astype(str).str[:10]

    combined_timestamps = pd.concat([
        github_data_copy['timestamp'],
        kaggle_data_copy['timestamp']
    ], ignore_index=True)

    daily_data = combined_timestamps.groupby(combined_timestamps).size().reset_index(name='value')
    daily_data.columns = ['timestamp', 'value']
    daily_data['timestamp'] = pd.to_datetime(daily_data['timestamp'])
    daily_data = daily_data.sort_values('timestamp').reset_index(drop=True)

    print(f"   - Объединено: {len(daily_data)} дней данных")
    print(f"   - Период: {daily_data['timestamp'].min().date()} по {daily_data['timestamp'].max().date()}")
    print(f"   - Среднее тревог в день: {daily_data['value'].mean():.1f} +/- {daily_data['value'].std():.1f}")
    print()

    # Use last 6 months for training
    train_data = daily_data.tail(180).copy()
    print(f"   - Тренировочный набор: {len(train_data)} дней")
    print()

    # Train all models
    print("[*] ТРЕНИРОВКА МОДЕЛЕЙ...")
    models = {}

    # ARIMA
    print("   [1/5] ARIMA(1,1,1)...", end=" ", flush=True)
    try:
        models['arima'] = ARIMAModel()
        models['arima'].fit(train_data)
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        models['arima'] = None

    # ExponentialSmoothing
    print("   [2/5] ExponentialSmoothing...", end=" ", flush=True)
    try:
        models['exp_smooth'] = ExponentialSmoothingModel(seasonal_periods=30)
        models['exp_smooth'].fit(train_data)
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        models['exp_smooth'] = None

    # Prophet
    print("   [3/5] Prophet...", end=" ", flush=True)
    try:
        prophet_data = train_data[['timestamp', 'value']].copy()
        prophet_data.columns = ['ds', 'y']
        models['prophet'] = ProphetModel()
        models['prophet'].fit(prophet_data)
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        models['prophet'] = None

    # LSTM
    print("   [4/5] LSTM(lookback=30)...", end=" ", flush=True)
    try:
        models['lstm'] = LSTMModel(lookback=30, units=64, epochs=10, verbose=0)
        models['lstm'].fit(train_data)
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        models['lstm'] = None

    # Ensemble
    print("   [5/5] Ensemble (все модели)...", end=" ", flush=True)
    try:
        ensemble = ModelEnsemble()
        for name, model in models.items():
            if model is not None:
                ensemble.add_model(name, model)
        ensemble.fit(train_data)
        models['ensemble'] = ensemble
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        models['ensemble'] = None

    print()

    # Forecast
    forecast_steps = 7
    print(f"[*] ПРОГНОЗ НА {forecast_steps} ДНЕЙ...")
    forecasts = {}

    for name, model in models.items():
        if model is not None:
            try:
                forecast = model.forecast(forecast_steps)
                forecasts[name] = forecast
                print(f"   + {name.upper():20s}: {forecast[:3].astype(int)} ... (avg: {forecast.mean():.1f})")
            except Exception as e:
                print(f"   - {name.upper():20s}: {e}")

    print()

    # Comparison table
    print("[*] СРАВНЕНИЕ ПРОГНОЗОВ (следующие 7 дней):")
    print()

    comparison = pd.DataFrame()
    for name, forecast in forecasts.items():
        comparison[name] = forecast

    # Add formatted output
    print(f"{'День':<8} " + " ".join(f"{name:>12}" for name in comparison.columns))
    print("-" * (8 + 14 * len(comparison.columns)))

    for day in range(forecast_steps):
        row = f"День +{day+1:<1} "
        for col in comparison.columns:
            if col in forecasts:
                value = forecasts[col][day]
                row += f"{int(value):>12} "
            else:
                row += f"{'N/A':>12} "
        print(row)

    print()
    print("[*] СТАТИСТИКА ПРОГНОЗОВ:")
    for name, forecast in forecasts.items():
        print(f"   {name.upper():20s}: mean={forecast.mean():.1f}, min={forecast.min():.1f}, max={forecast.max():.1f}")

    print()

    # Save results
    output_file = 'DEMO_RESULTS.txt'
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AIR RAID ALERTS TIME SERIES - COMPLETE MODEL DEMONSTRATION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("DATA:\n")
        f.write(f"  Total records (GitHub + Kaggle): {len(github_data) + len(kaggle_data)}\n")
        f.write(f"  Daily aggregates: {len(daily_data)}\n")
        f.write(f"  Period: {daily_data['timestamp'].min().date()} to {daily_data['timestamp'].max().date()}\n")
        f.write(f"  Training set: {len(train_data)} days\n\n")

        f.write("MODEL RESULTS:\n")
        f.write(comparison.to_string())
        f.write("\n\n")

        f.write("STATISTICS:\n")
        for name, forecast in forecasts.items():
            f.write(f"  {name.upper():20s}: mean={forecast.mean():.1f}, std={forecast.std():.1f}\n")

    print(f"[OK] Results saved to {output_file}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
