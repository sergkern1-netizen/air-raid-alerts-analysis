# Advanced Analytics Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing ARIMA baseline with three advanced forecasting models (Prophet, LSTM, Exponential Smoothing) to enable comparative performance analysis and identify best-fit approach for air raid alerts time series.

**Architecture:** Add three new model classes following the existing `TimeSeriesModel` base class pattern in `src/models/`. Each model integrates with the test suite and visualization pipeline. An ensemble module provides side-by-side evaluation of all four approaches (ARIMA + Prophet + ExSmooth + LSTM) on the same 274K-record dataset. New notebook demonstrates comparative analysis workflow.

**Tech Stack:** Prophet (Facebook's TSA library), TensorFlow/Keras (LSTM), statsmodels.tsa.holtwinters (ExponentialSmoothing), existing pandas/numpy stack

---

## Phase 2a: Dependencies & Setup

### Task 1: Update requirements.txt for Advanced Analytics libraries

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Read current requirements**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
cat requirements.txt
```

Expected output shows pandas, numpy, scipy, statsmodels, matplotlib, seaborn, plotly, pytest, jupyter

- [ ] **Step 2: Add Prophet, TensorFlow, and other dependencies**

Replace `requirements.txt` with:

```txt
# Data & Numerical Computing
pandas>=1.3.0
numpy>=1.21.0

# Statistical Analysis & Time Series
statsmodels>=0.13.0
scipy>=1.7.0

# Machine Learning
scikit-learn>=1.0.0

# Visualization
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0

# Advanced Time Series
prophet>=1.1.0

# Deep Learning (for LSTM)
tensorflow>=2.10.0
keras>=2.10.0

# Development & Testing
pytest>=6.2.0
jupyter>=1.0.0
ipython>=7.0.0
```

- [ ] **Step 3: Install new dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install successfully (may take 2-3 min for tensorflow)

- [ ] **Step 4: Verify installations**

```bash
python -c "import prophet; import tensorflow; import keras; print('All imports OK')"
```

Expected: "All imports OK"

- [ ] **Step 5: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add requirements.txt
git commit -m "feat: add prophet, tensorflow, keras for advanced analytics"
```

---

## Phase 2b: Prophet Model

### Task 2: Implement Prophet forecasting model

**Files:**
- Create: `src/models/prophet.py`
- Create: `tests/test_prophet.py`

- [ ] **Step 1: Write test for Prophet model**

Create `tests/test_prophet.py`:

```python
import pytest
import numpy as np
import pandas as pd
from src.models.prophet import ProphetModel

def test_prophet_initialization():
    """Test Prophet model can be initialized"""
    model = ProphetModel(interval_width=0.95)
    assert model.name == "Prophet"
    assert not model.is_fitted

def test_prophet_fit():
    """Test Prophet fitting with data"""
    # Create sample time series (daily data like air raid alerts)
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    values = 50 + 10 * np.sin(np.arange(100) * 2 * np.pi / 30) + np.random.normal(0, 5, 100)
    
    df = pd.DataFrame({
        "ds": dates,
        "y": values
    })
    
    model = ProphetModel()
    model.fit(df)
    
    assert model.is_fitted
    assert model.model is not None

def test_prophet_forecast():
    """Test Prophet forecasting"""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    values = 50 + 10 * np.sin(np.arange(100) * 2 * np.pi / 30) + np.random.normal(0, 5, 100)
    
    df = pd.DataFrame({
        "ds": dates,
        "y": values
    })
    
    model = ProphetModel()
    model.fit(df)
    forecast = model.forecast(steps=7)
    
    assert len(forecast) == 7
    assert all(np.isfinite(forecast))

def test_prophet_with_seasonality():
    """Test Prophet with explicit seasonality settings"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    # Strong yearly seasonality
    values = 100 + 30 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 5, 365)
    
    df = pd.DataFrame({
        "ds": dates,
        "y": values
    })
    
    model = ProphetModel(yearly_seasonality=True, daily_seasonality=False)
    model.fit(df)
    forecast = model.forecast(steps=30)
    
    assert len(forecast) == 30
```

- [ ] **Step 2: Implement Prophet model class**

Create `src/models/prophet.py`:

```python
import pandas as pd
import numpy as np
from typing import Optional
from prophet import Prophet
from src.models.base import TimeSeriesModel

class ProphetModel(TimeSeriesModel):
    """Facebook Prophet time series forecasting model"""
    
    def __init__(
        self,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
        interval_width: float = 0.95,
        changepoint_prior_scale: float = 0.05,
    ):
        """
        Initialize Prophet model.
        
        Args:
            yearly_seasonality: Model yearly patterns
            weekly_seasonality: Model weekly patterns
            daily_seasonality: Model daily patterns (hourly frequency)
            interval_width: Confidence interval width (0-1)
            changepoint_prior_scale: Flexibility of trend changes
        """
        super().__init__("Prophet")
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.interval_width = interval_width
        self.changepoint_prior_scale = changepoint_prior_scale
        self.model = None
        self.fitted_model = None
    
    def fit(self, data, **kwargs) -> None:
        """
        Fit Prophet model to data.
        
        Args:
            data: Either:
              - DataFrame with 'ds' (datetime) and 'y' (values) columns
              - numpy array of values (will convert to DataFrame)
        """
        # Convert data to Prophet format if needed
        if isinstance(data, np.ndarray):
            dates = pd.date_range(start="2024-01-01", periods=len(data), freq="D")
            df = pd.DataFrame({"ds": dates, "y": data})
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
            if "ds" not in df.columns or "y" not in df.columns:
                raise ValueError("DataFrame must have 'ds' and 'y' columns")
        else:
            raise ValueError("Data must be numpy array or DataFrame")
        
        self.training_data = df.copy()
        
        # Initialize Prophet
        self.model = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=self.daily_seasonality,
            interval_width=self.interval_width,
            changepoint_prior_scale=self.changepoint_prior_scale,
        )
        
        # Suppress Prophet logging
        import logging
        logging.getLogger("prophet").setLevel(logging.WARNING)
        
        # Fit model
        self.fitted_model = self.model.fit(df)
        self.is_fitted = True
    
    def forecast(self, steps: int = 1) -> np.ndarray:
        """
        Forecast next N steps.
        
        Args:
            steps: Number of steps to forecast
        
        Returns:
            Array of forecast values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before forecasting")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=steps)
        forecast_df = self.model.predict(future)
        
        # Return only the new forecasts (last 'steps' rows)
        forecast_values = forecast_df["yhat"].values[-steps:]
        
        # Ensure no NaN values
        forecast_values = np.nan_to_num(forecast_values)
        
        return forecast_values
    
    def get_diagnostics(self) -> dict:
        """Get model diagnostics including component analysis"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return {
            "model_name": self.name,
            "n_observations": len(self.training_data),
            "yearly_seasonality": self.yearly_seasonality,
            "weekly_seasonality": self.weekly_seasonality,
        }
```

- [ ] **Step 3: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add src/models/prophet.py tests/test_prophet.py
git commit -m "feat: add Prophet time series model with yearly/weekly seasonality"
```

---

## Phase 2c: Exponential Smoothing Model

### Task 3: Implement Exponential Smoothing model

**Files:**
- Create: `src/models/exponential_smoothing.py`
- Create: `tests/test_exponential_smoothing.py`

- [ ] **Step 1: Write tests for Exponential Smoothing**

Create `tests/test_exponential_smoothing.py`:

```python
import pytest
import numpy as np
import pandas as pd
from src.models.exponential_smoothing import ExponentialSmoothingModel

def test_exponential_smoothing_initialization():
    """Test ExponentialSmoothing model can be initialized"""
    model = ExponentialSmoothingModel(seasonal_periods=30)
    assert model.name == "ExponentialSmoothing"
    assert not model.is_fitted

def test_exponential_smoothing_fit():
    """Test ExponentialSmoothing fitting with data"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    trend = np.linspace(50, 70, 365)
    seasonal = 10 * np.sin(np.arange(365) * 2 * np.pi / 30)
    values = trend + seasonal + np.random.normal(0, 3, 365)
    
    df = pd.DataFrame({"timestamp": dates, "value": values})
    
    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(df)
    
    assert model.is_fitted
    assert model.fitted_model is not None

def test_exponential_smoothing_forecast():
    """Test ExponentialSmoothing forecasting"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    trend = np.linspace(50, 70, 365)
    seasonal = 10 * np.sin(np.arange(365) * 2 * np.pi / 30)
    values = trend + seasonal + np.random.normal(0, 3, 365)
    
    df = pd.DataFrame({"timestamp": dates, "value": values})
    
    model = ExponentialSmoothingModel(seasonal_periods=30)
    model.fit(df)
    forecast = model.forecast(steps=30)
    
    assert len(forecast) == 30
    assert all(np.isfinite(forecast))

def test_exponential_smoothing_different_seasonal_periods():
    """Test with different seasonal periods"""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    values = 100 + np.random.normal(0, 5, 365)
    
    df = pd.DataFrame({"timestamp": dates, "value": values})
    
    # Test with weekly seasonality (7 days)
    model = ExponentialSmoothingModel(seasonal_periods=7)
    model.fit(df)
    forecast = model.forecast(steps=14)
    
    assert len(forecast) == 14
```

- [ ] **Step 2: Implement Exponential Smoothing model class**

Create `src/models/exponential_smoothing.py`:

```python
import pandas as pd
import numpy as np
from typing import Optional
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from src.models.base import TimeSeriesModel

class ExponentialSmoothingModel(TimeSeriesModel):
    """Holt-Winters Exponential Smoothing with trend and seasonality"""
    
    def __init__(
        self,
        seasonal_periods: int = 30,
        trend: str = "add",
        seasonal: str = "add",
        seasonal_periods_validation: bool = True,
    ):
        """
        Initialize Exponential Smoothing model.
        
        Args:
            seasonal_periods: Length of seasonal cycle (e.g., 30 for monthly, 7 for weekly)
            trend: 'add' for additive trend, 'mul' for multiplicative
            seasonal: 'add' for additive seasonality, 'mul' for multiplicative
            seasonal_periods_validation: Ensure training data is at least 2x seasonal_periods
        """
        super().__init__("ExponentialSmoothing")
        self.seasonal_periods = seasonal_periods
        self.trend = trend
        self.seasonal = seasonal
        self.seasonal_periods_validation = seasonal_periods_validation
        self.fitted_model = None
    
    def fit(self, data, **kwargs) -> None:
        """
        Fit Exponential Smoothing model.
        
        Args:
            data: Either:
              - DataFrame with 'value' column (datetime index expected)
              - numpy array of values
        """
        # Convert data to proper format
        if isinstance(data, np.ndarray):
            values = data
        elif isinstance(data, pd.DataFrame):
            if "value" in data.columns:
                values = data["value"].values
            else:
                # Try first numeric column
                values = data.iloc[:, 0].values
        else:
            raise ValueError("Data must be numpy array or DataFrame")
        
        self.training_data = values.copy()
        
        # Validate we have enough data for seasonality
        min_length = self.seasonal_periods * 2
        if self.seasonal_periods_validation and len(values) < min_length:
            raise ValueError(
                f"Require at least {min_length} observations for seasonal_periods={self.seasonal_periods}, "
                f"got {len(values)}"
            )
        
        try:
            # Fit Exponential Smoothing
            self.fitted_model = ExponentialSmoothing(
                values,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods,
            ).fit(optimized=True)
            
            self.is_fitted = True
        except Exception as e:
            # Fallback: try without seasonal component if it fails
            print(f"ExponentialSmoothing with seasonal failed: {e}. Trying without seasonal...")
            self.fitted_model = ExponentialSmoothing(
                values,
                trend=self.trend,
                seasonal=None,
            ).fit(optimized=True)
            self.is_fitted = True
    
    def forecast(self, steps: int = 1) -> np.ndarray:
        """
        Forecast next N steps.
        
        Args:
            steps: Number of steps to forecast
        
        Returns:
            Array of forecast values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before forecasting")
        
        # Get forecast
        start_index = len(self.training_data)
        end_index = start_index + steps - 1
        
        forecast_values = self.fitted_model.forecast(start=start_index, end=end_index)
        
        # Ensure no NaN values and proper shape
        forecast_values = np.nan_to_num(forecast_values)
        
        return np.array(forecast_values).flatten()[:steps]
    
    def get_diagnostics(self) -> dict:
        """Get model diagnostics"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return {
            "model_name": self.name,
            "seasonal_periods": self.seasonal_periods,
            "trend": self.trend,
            "seasonal": self.seasonal,
            "n_observations": len(self.training_data),
        }
```

- [ ] **Step 3: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add src/models/exponential_smoothing.py tests/test_exponential_smoothing.py
git commit -m "feat: add Exponential Smoothing model with flexible seasonality"
```

---

## Phase 2d: LSTM Neural Network Model

### Task 4: Implement LSTM deep learning model

**Files:**
- Create: `src/models/lstm.py`
- Create: `tests/test_lstm.py`

**Note:** LSTM tests may take 1-2 minutes each due to neural network training. This is expected.

- [ ] **Step 1: Implement LSTM model class**

Create `src/models/lstm.py` with proper MinMaxScaler normalization and sequence generation

- [ ] **Step 2: Write comprehensive tests**

Create `tests/test_lstm.py` with 4 test cases

- [ ] **Step 3: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add src/models/lstm.py tests/test_lstm.py
git commit -m "feat: add LSTM neural network model for time series forecasting"
```

---

## Phase 2e: Ensemble & Comparison

### Task 5: Implement model ensemble and comparison

**Files:**
- Create: `src/models/ensemble.py`
- Create: `tests/test_ensemble.py`

- [ ] **Step 1: Implement ensemble class**

Create `src/models/ensemble.py` with ModelEnsemble and compare_models functions

- [ ] **Step 2: Write tests**

Create `tests/test_ensemble.py` with 5 test cases

- [ ] **Step 3: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add src/models/ensemble.py tests/test_ensemble.py
git commit -m "feat: add model ensemble for comparative analysis of forecasts"
```

---

## Phase 2f: Enhanced Visualization

### Task 6: Extend visualization module for model comparison

**Files:**
- Modify: `src/visualization/plotter.py`

- [ ] **Step 1: Add plot_model_comparison method**

Extend TimeSeriesPlotter class with method for plotting multiple model forecasts

- [ ] **Step 2: Add plot_metrics_comparison method**

Extend TimeSeriesPlotter class with method for comparing model performance metrics (MAE, RMSE, MAPE)

- [ ] **Step 3: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add src/visualization/plotter.py
git commit -m "feat: add model comparison and metrics visualization methods"
```

---

## Phase 2g: Advanced Analytics Notebook

### Task 7: Create advanced analytics notebook

**Files:**
- Create: `notebooks/02-advanced-analytics.ipynb`

- [ ] **Step 1: Create notebook with 12 cells**

Notebook structure:
1. Imports and setup
2. Load data (processed validated data or synthetic)
3. Data visualization
4. Train-test split
5. Build ensemble with all 4 models
6. Fit all models
7. Generate 7-day forecasts
8. Visualize forecast comparison
9. Quantitative comparison on test set
10. Visualize metrics comparison
11. Ensemble forecast (mean of all models)
12. Recommendations and summary

- [ ] **Step 2: Commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add notebooks/02-advanced-analytics.ipynb
git commit -m "docs: add advanced analytics notebook with model comparison workflow"
```

---

## Phase 2h: Integration Testing & Documentation

### Task 8: Run full test suite and document results

**Files:**
- Modify: `docs/session-history.md`

- [ ] **Step 1: Run complete test suite**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
pytest tests/ -v --tb=short
```

Expected: All tests pass (37+ tests total)

- [ ] **Step 2: Run coverage report**

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

- [ ] **Step 3: Update session history**

Add section documenting Phase 2 completion with:
- All 4 models implemented and tested
- Ensemble framework in place
- 7-day forecast comparison working
- All tests passing

- [ ] **Step 4: Final commit**

```bash
cd "d:\Нова папка\air-raid-alerts-analysis"
git add docs/session-history.md
git commit -m "docs: update session history with Phase 2 Advanced Analytics completion"
```

---

## Summary

**8 Tasks, 3 Phases:**
- **Phase 2a** (Task 1): Dependencies setup
- **Phase 2b** (Task 2): Prophet model
- **Phase 2c** (Task 3): Exponential Smoothing model
- **Phase 2d** (Task 4): LSTM neural network
- **Phase 2e** (Task 5): Ensemble & comparison
- **Phase 2f** (Task 6): Visualization enhancements
- **Phase 2g** (Task 7): Advanced analytics notebook
- **Phase 2h** (Task 8): Integration & documentation

**Expected Outcome:**
- 4 fully functional forecasting models (ARIMA baseline + 3 new)
- Comparative analysis framework
- 37+ unit tests all passing
- Interactive notebook demonstrating all models
- Complete documentation of Phase 2 in session history
