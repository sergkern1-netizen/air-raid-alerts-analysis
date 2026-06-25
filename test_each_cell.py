#!/usr/bin/env python
"""Test each notebook cell individually to find errors."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

sys.path.insert(0, str(Path.cwd()))

# Set correct working directory (should be project root, not notebooks)
import os
project_root = Path.cwd() if 'air-raid-alerts-analysis' in Path.cwd().name else Path.cwd().parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING EACH NOTEBOOK CELL")
print("=" * 80)

# Cell 1: Imports
print("\n[CELL 1] Imports and setup")
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    import sys
    import warnings

    from src.models.prophet import ProphetModel
    from src.models.exponential_smoothing import ExponentialSmoothingModel
    from src.models.lstm import LSTMModel
    from src.visualization.plotter import TimeSeriesPlotter
    from src.utils.metrics import calculate_metrics

    sns.set_style('darkgrid')
    plt.rcParams['figure.figsize'] = (15, 5)
    warnings.filterwarnings('ignore')

    print("    [OK] All imports successful")
except Exception as e:
    print(f"    [ERROR] {e}")
    sys.exit(1)

# Cell 2: Load data
print("\n[CELL 2] Load pre-calculated daily aggregates")
try:
    agg_path = Path.cwd() / 'data' / 'processed' / '01_daily_aggregates.csv'
    df_agg = pd.read_csv(agg_path)
    df_agg['date'] = pd.to_datetime(df_agg['date'])
    df_agg = df_agg.rename(columns={'date': 'timestamp', 'alerts_count_combined': 'value'})
    df_agg = df_agg.sort_values('timestamp')

    print(f"    [OK] {len(df_agg)} days loaded")
    print(f"        Columns: {df_agg.columns.tolist()}")
except Exception as e:
    print(f"    [ERROR] {e}")
    sys.exit(1)

# Cell 3: Visualize time series
print("\n[CELL 3] Visualize time series")
try:
    plotter = TimeSeriesPlotter()
    # Don't actually plot, just test the code path
    fig = plotter.plot_series(
        df_agg,
        timestamp_col='timestamp',
        value_col='value',
        title='Daily Air Raid Alert Duration',
        figsize=(16, 5)
    )
    plt.close(fig)

    print(f"    [OK] Visualization created")
    print(f"        Mean: {df_agg['value'].mean():.1f} alerts/day")
    print(f"        Peak: {df_agg['value'].max():.1f} alerts")
except Exception as e:
    print(f"    [ERROR] {e}")

# Cell 4: Train-test split
print("\n[CELL 4] Train-test split (70-30)")
try:
    total_days = len(df_agg)
    train_size = int(total_days * 0.7)
    df_train = df_agg.iloc[:train_size].copy()
    df_test = df_agg.iloc[train_size:].copy()

    print(f"    [OK] Split created")
    print(f"        Train: {len(df_train)} days")
    print(f"        Test: {len(df_test)} days")
except Exception as e:
    print(f"    [ERROR] {e}")
    sys.exit(1)

# Cell 5: Train models
print("\n[CELL 5] Train all models")
try:
    # Prophet
    print("    Training Prophet...")
    prophet_df = df_train[['timestamp', 'value']].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_model = ProphetModel(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95
    )
    prophet_model.fit(prophet_df)
    print(f"        Prophet: OK")

    # ExSmoothing
    print("    Training Exponential Smoothing...")
    es_model = ExponentialSmoothingModel(
        seasonal_periods=30,
        trend='add',
        seasonal='add'
    )
    es_model.fit(df_train)
    print(f"        ExSmoothing: OK")

    # LSTM
    print("    Training LSTM...")
    lstm_model = LSTMModel(
        lookback=30,
        units=64,
        layers=2,
        dropout=0.2,
        epochs=10,
        batch_size=16,
        verbose=0
    )
    lstm_model.fit(df_train)
    print(f"        LSTM: OK")

    print(f"    [OK] All models trained")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cell 6: Generate forecasts
print("\n[CELL 6] Generate 7-day forecasts")
try:
    forecasts = {}
    forecasts['Prophet'] = prophet_model.forecast(steps=7)
    forecasts['ExponentialSmoothing'] = es_model.forecast(steps=7)
    forecasts['LSTM'] = lstm_model.forecast(steps=7)

    ensemble_forecast = (forecasts['Prophet'] + forecasts['ExponentialSmoothing'] + forecasts['LSTM']) / 3

    print(f"    [OK] Forecasts generated")
    for name, forecast in forecasts.items():
        print(f"        {name}: mean={forecast.mean():.1f}")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Cell 7: Visualize forecasts
print("\n[CELL 7] Visualize forecast comparison")
try:
    df_plot = df_train.tail(60).reset_index(drop=True)
    prophet_df_plot = df_plot[['timestamp', 'value']].copy()
    prophet_df_plot.columns = ['ds', 'y']

    fig = plotter.plot_model_comparison(
        prophet_df_plot,
        forecasts,
        timestamp_col='ds',
        value_col='y',
        title='Model Forecast Comparison',
        figsize=(17, 6)
    )
    plt.close(fig)

    print(f"    [OK] Forecast visualization created")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Cell 8: Evaluate models
print("\n[CELL 8] Evaluate models on test set")
try:
    actual_values = df_test['value'].values
    n_test = len(df_test)

    results = []

    for model_name, model in [
        ('Prophet', prophet_model),
        ('ExponentialSmoothing', es_model),
        ('LSTM', lstm_model)
    ]:
        forecast = model.forecast(steps=n_test)
        metrics = calculate_metrics(actual_values, forecast)
        results.append({
            'Model': model_name,
            'MAE': metrics.get('MAE'),
            'RMSE': metrics.get('RMSE'),
            'MAPE': metrics.get('MAPE')
        })
        print(f"        {model_name}: MAE={metrics.get('MAE'):.2f}, MAPE={metrics.get('MAPE'):.2f}%")

    results_df = pd.DataFrame(results)
    print(f"    [OK] Evaluation complete")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Cell 9: Visualize metrics
print("\n[CELL 9] Visualize metrics comparison")
try:
    fig = plotter.plot_metrics_comparison(
        results,
        title='Model Performance Comparison',
        figsize=(16, 5)
    )
    plt.close(fig)

    best_mae_idx = results_df['MAE'].idxmin()
    print(f"    [OK] Metrics visualization created")
    print(f"        Best MAE: {results_df.loc[best_mae_idx, 'Model']}")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Cell 10: Summary
print("\n[CELL 10] Summary and recommendations")
try:
    print(f"    [OK] Summary would be generated")
    print(f"        Dataset: {len(df_agg)} days")
    print(f"        Best model: {results_df.loc[results_df['MAE'].idxmin(), 'Model']}")
except Exception as e:
    print(f"    [ERROR] {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nIf all cells show [OK], then notebook is ready!")
