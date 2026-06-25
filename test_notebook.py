#!/usr/bin/env python
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

print("=" * 80)
print("COMPLETE NOTEBOOK TEST")
print("=" * 80)

try:
    # TEST 1: Load daily aggregates
    print("\n[1/8] Loading daily aggregates...")
    agg_path = Path.cwd() / 'data' / 'processed' / '01_daily_aggregates.csv'
    df_agg = pd.read_csv(agg_path)
    df_agg['date'] = pd.to_datetime(df_agg['date'])
    df_agg = df_agg.rename(columns={'date': 'timestamp', 'alerts_count_combined': 'value'})
    df_agg = df_agg.sort_values('timestamp')
    print(f"    [OK] SUCCESS: {len(df_agg)} days loaded")
    print(f"    Date range: {df_agg['timestamp'].min().date()} to {df_agg['timestamp'].max().date()}")

    # TEST 2: Train-test split
    print("\n[2/8] Creating train-test split (70-30)...")
    total_days = len(df_agg)
    train_size = int(total_days * 0.7)
    df_train = df_agg.iloc[:train_size].copy()
    df_test = df_agg.iloc[train_size:].copy()
    print(f"    [OK] Train={len(df_train)} days, Test={len(df_test)} days")

    # TEST 3: Import models
    print("\n[3/8] Importing models...")
    from src.models.prophet import ProphetModel
    from src.models.exponential_smoothing import ExponentialSmoothingModel
    from src.models.lstm import LSTMModel
    from src.utils.metrics import calculate_metrics
    print(f"    [OK] All 3 models imported")

    # TEST 4: Train Prophet
    print("\n[4/8] Training Prophet model...")
    prophet_df = df_train[['timestamp', 'value']].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_model = ProphetModel(yearly_seasonality=True, weekly_seasonality=True)
    prophet_model.fit(prophet_df)
    prophet_forecast = prophet_model.forecast(steps=7)
    print(f"    [OK] Prophet trained")
    print(f"    7-day forecast (mean): {prophet_forecast.mean():.1f} alerts/day")

    # TEST 5: Train Exponential Smoothing
    print("\n[5/8] Training Exponential Smoothing model...")
    es_model = ExponentialSmoothingModel(seasonal_periods=30)
    es_model.fit(df_train)
    es_forecast = es_model.forecast(steps=7)
    print(f"    [OK] Exponential Smoothing trained")
    print(f"    7-day forecast (mean): {es_forecast.mean():.1f} alerts/day")

    # TEST 6: Train LSTM
    print("\n[6/8] Training LSTM model (may take 30-60 seconds)...")
    lstm_model = LSTMModel(lookback=30, epochs=10, batch_size=16, verbose=0)
    lstm_model.fit(df_train)
    lstm_forecast = lstm_model.forecast(steps=7)
    print(f"    [OK] LSTM trained")
    print(f"    7-day forecast (mean): {lstm_forecast.mean():.1f} alerts/day")

    # TEST 7: Evaluate models on test set
    print("\n[7/8] Evaluating models on test set...")
    actual_values = df_test['value'].values

    results = []
    for name, model in [('Prophet', prophet_model), ('ExponentialSmoothing', es_model), ('LSTM', lstm_model)]:
        forecast = model.forecast(steps=len(df_test))
        metrics = calculate_metrics(actual_values, forecast)
        results.append({
            'Model': name,
            'MAE': metrics.get('MAE'),
            'RMSE': metrics.get('RMSE'),
            'MAPE': metrics.get('MAPE')
        })
        print(f"    {name:20} MAE={metrics.get('MAE', 0):.2f} | RMSE={metrics.get('RMSE', 0):.2f} | MAPE={metrics.get('MAPE', 0):.2f}%")

    results_df = pd.DataFrame(results)

    # TEST 8: Summary
    print("\n[8/8] SUMMARY")
    print(f"    Dataset: {len(df_agg)} days ({df_agg['timestamp'].min().date()} to {df_agg['timestamp'].max().date()})")
    print(f"    Training: {len(df_train)} days, Testing: {len(df_test)} days")
    print(f"    Best model (MAE): {results_df.loc[results_df['MAE'].idxmin(), 'Model']}")
    print(f"    Best model (RMSE): {results_df.loc[results_df['RMSE'].idxmin(), 'Model']}")
    print(f"    Best model (MAPE): {results_df.loc[results_df['MAPE'].idxmin(), 'Model']}")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! NOTEBOOK IS READY TO RUN")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Open notebook in Jupyter: notebooks/02-advanced-analytics.ipynb")
    print("2. Run cells in order (Shift+Enter) or Run All")
    print("3. All 12 cells should execute without errors")

except Exception as e:
    print(f"\n[FAIL] ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
