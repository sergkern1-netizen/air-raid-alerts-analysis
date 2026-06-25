"""
Model Comparison Analysis — Compare Prophet, ExponentialSmoothing, LSTM on test set
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from src.models.prophet import ProphetModel
from src.models.exponential_smoothing import ExponentialSmoothingModel
from src.models.lstm import LSTMModel
from src.models.ensemble import ModelEnsemble
from src.utils.metrics import calculate_mae, calculate_rmse, calculate_mape


class ModelComparisonAnalyzer:
    """Compare all models on test set"""

    def __init__(self, data_dir: str = "data/processed", test_size: float = 0.3):
        self.data_dir = Path(data_dir)
        self.test_size = test_size
        self.train_data = None
        self.test_data = None
        self.models_results = {}

    def load_and_split_data(self):
        """Load data and split into train/test"""
        # Load daily aggregates
        daily_df = pd.read_csv(self.data_dir / "01_daily_aggregates.csv")
        daily_df["date"] = pd.to_datetime(daily_df["date"])
        daily_df = daily_df.sort_values("date")

        # Get alert counts
        alerts = daily_df["alerts_count_combined"].values

        # Split
        split_idx = int(len(alerts) * (1 - self.test_size))
        self.train_data = alerts[:split_idx]
        self.test_data = alerts[split_idx:]

        # Create dataframes with timestamp
        self.train_df = pd.DataFrame({
            "timestamp": daily_df["date"].iloc[:split_idx].values,
            "value": self.train_data
        })

        self.test_df = pd.DataFrame({
            "timestamp": daily_df["date"].iloc[split_idx:].values,
            "value": self.test_data
        })

        print(f"[OK] Data split: {len(self.train_data)} train, {len(self.test_data)} test")

    def train_prophet(self):
        """Train Prophet model"""
        print("\n[TRAIN] Prophet...")
        try:
            model = ProphetModel()
            model.fit(self.train_df)

            # Forecast on test period
            forecast = model.forecast(steps=len(self.test_data))
            forecast = np.maximum(forecast, 0)  # No negative forecasts

            mae = calculate_mae(self.test_data, forecast)
            rmse = calculate_rmse(self.test_data, forecast)
            mape = calculate_mape(self.test_data, forecast)

            self.models_results["prophet"] = {
                "forecast": forecast,
                "mae": mae,
                "rmse": rmse,
                "mape": mape
            }

            print(f"  [OK] Prophet: MAE={mae:.1f}, RMSE={rmse:.1f}, MAPE={mape:.1f}%")
        except Exception as e:
            print(f"  [FAIL] Prophet failed: {e}")

    def train_exponential_smoothing(self):
        """Train ExponentialSmoothing model"""
        print("\n[TRAIN] ExponentialSmoothing...")
        try:
            model = ExponentialSmoothingModel()
            model.fit(self.train_df)

            forecast = model.forecast(steps=len(self.test_data))
            forecast = np.maximum(forecast, 0)

            mae = calculate_mae(self.test_data, forecast)
            rmse = calculate_rmse(self.test_data, forecast)
            mape = calculate_mape(self.test_data, forecast)

            self.models_results["exponential_smoothing"] = {
                "forecast": forecast,
                "mae": mae,
                "rmse": rmse,
                "mape": mape
            }

            print(f"  [OK] ExponentialSmoothing: MAE={mae:.1f}, RMSE={rmse:.1f}, MAPE={mape:.1f}%")
        except Exception as e:
            print(f"  [FAIL] ExponentialSmoothing failed: {e}")

    def train_lstm(self):
        """Train LSTM model"""
        print("\n[TRAIN] LSTM...")
        try:
            model = LSTMModel(lookback=30, epochs=20, verbose=0)
            model.fit(self.train_df)

            forecast = model.forecast(steps=len(self.test_data))
            forecast = np.maximum(forecast, 0)

            mae = calculate_mae(self.test_data, forecast)
            rmse = calculate_rmse(self.test_data, forecast)
            mape = calculate_mape(self.test_data, forecast)

            self.models_results["lstm"] = {
                "forecast": forecast,
                "mae": mae,
                "rmse": rmse,
                "mape": mape
            }

            print(f"  [OK] LSTM: MAE={mae:.1f}, RMSE={rmse:.1f}, MAPE={mape:.1f}%")
        except Exception as e:
            print(f"  [FAIL] LSTM failed: {e}")

    def train_ensemble(self):
        """Train Ensemble model (average of available models)"""
        print("\n[TRAIN] Creating Ensemble...")
        try:
            if len(self.models_results) < 2:
                print("  [FAIL] Need at least 2 models for ensemble")
                return

            # Average forecasts
            forecasts = [m["forecast"] for m in self.models_results.values()]
            ensemble_forecast = np.mean(forecasts, axis=0)

            mae = calculate_mae(self.test_data, ensemble_forecast)
            rmse = calculate_rmse(self.test_data, ensemble_forecast)
            mape = calculate_mape(self.test_data, ensemble_forecast)

            self.models_results["ensemble"] = {
                "forecast": ensemble_forecast,
                "mae": mae,
                "rmse": rmse,
                "mape": mape
            }

            print(f"  [OK] Ensemble: MAE={mae:.1f}, RMSE={rmse:.1f}, MAPE={mape:.1f}%")
        except Exception as e:
            print(f"  [FAIL] Ensemble failed: {e}")

    def get_comparison_table(self) -> pd.DataFrame:
        """Get comparison table"""
        rows = []
        for model_name, results in self.models_results.items():
            rows.append({
                "Model": model_name.replace("_", " ").title(),
                "MAE": f"{results['mae']:.1f}",
                "RMSE": f"{results['rmse']:.1f}",
                "MAPE": f"{results['mape']:.1f}%"
            })

        comparison_df = pd.DataFrame(rows)

        # Sort by MAPE
        comparison_df["MAPE_num"] = comparison_df["MAPE"].str.rstrip("%").astype(float)
        comparison_df = comparison_df.sort_values("MAPE_num")
        comparison_df = comparison_df.drop("MAPE_num", axis=1)

        return comparison_df

    def generate_report(self) -> str:
        """Generate comparison report"""
        self.load_and_split_data()
        self.train_prophet()
        self.train_exponential_smoothing()
        self.train_lstm()
        self.train_ensemble()

        report = "\n" + "="*60 + "\n"
        report += "MODEL COMPARISON — TEST SET RESULTS\n"
        report += "="*60 + "\n\n"

        comparison_df = self.get_comparison_table()
        report += comparison_df.to_string(index=False)

        # Best model
        best_model = comparison_df.iloc[0]["Model"]
        best_mape = comparison_df.iloc[0]["MAPE"]
        report += f"\n\n[BEST] Best Model: {best_model} ({best_mape})\n"

        # Improvement vs worst
        worst_mape = float(comparison_df.iloc[-1]["MAPE"].rstrip("%"))
        best_mape_num = float(comparison_df.iloc[0]["MAPE"].rstrip("%"))
        improvement = worst_mape - best_mape_num
        report += f"[STAT] Improvement vs worst: {improvement:.1f}% (relative)\n"

        report += "\n" + "="*60 + "\n"

        return report

    def save_results_csv(self, output_file: str = "reports/model_comparison.csv"):
        """Save comparison to CSV"""
        comparison_df = self.get_comparison_table()
        comparison_df.to_csv(output_file, index=False)
        print(f"\n[OK] Saved to {output_file}")


if __name__ == "__main__":
    analyzer = ModelComparisonAnalyzer()
    report = analyzer.generate_report()
    print(report)
    analyzer.save_results_csv()
