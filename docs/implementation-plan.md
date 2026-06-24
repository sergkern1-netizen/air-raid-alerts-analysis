# Air Raid Alerts Time Series Analysis — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Python data science pipeline for analyzing and forecasting air raid alerts time series with statistical analysis and machine learning models.

**Architecture:** Modular Python project with separate modules for data loading, processing, analysis, modeling and visualization. Data flows from sources → processing → exploratory analysis → time series modeling → predictions and visualization. Each module is independently testable.

**Tech Stack:** pandas, numpy, scikit-learn, statsmodels, matplotlib, seaborn, plotly, pytest

---

## Phase 1: Project Infrastructure & Dependencies

### Task 1: Create requirements.txt with all dependencies

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write requirements.txt with all dependencies**

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

# Development & Testing
pytest>=6.2.0
jupyter>=1.0.0
ipython>=7.0.0

# Optional: Deep Learning (for future phases)
# tensorflow>=2.8.0
# keras>=2.8.0

# Optional: Advanced forecasting
# prophet>=1.1.0
```

- [ ] **Step 2: Commit requirements**

```bash
git add requirements.txt
git commit -m "feat: add project dependencies"
```

### Task 2: Create project configuration module

**Files:**
- Create: `src/utils/config.py`

- [ ] **Step 1: Write config.py**

```python
# src/utils/config.py
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Data processing
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_ZONES = {
    "Kyiv": "Europe/Kyiv",
    "Ukraine": "Europe/Kyiv",
}

# Model configuration
TRAIN_TEST_SPLIT = 0.8
RANDOM_SEED = 42

# Time series
FREQ = "1H"  # Hourly frequency
MIN_HISTORY_DAYS = 30  # Minimum days for analysis
```

- [ ] **Step 2: Create __init__.py for utils module**

```python
# src/utils/__init__.py
from .config import PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR
from .metrics import calculate_mae, calculate_rmse, calculate_mape

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "calculate_mae",
    "calculate_rmse",
    "calculate_mape",
]
```

- [ ] **Step 3: Create metrics module**

```python
# src/utils/metrics.py
import numpy as np

def calculate_mae(y_true, y_pred):
    """Mean Absolute Error"""
    return np.mean(np.abs(y_true - y_pred))

def calculate_rmse(y_true, y_pred):
    """Root Mean Squared Error"""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def calculate_mape(y_true, y_pred):
    """Mean Absolute Percentage Error"""
    mask = y_true != 0
    if not np.any(mask):
        return 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
```

- [ ] **Step 4: Commit configuration modules**

```bash
git add src/utils/
git commit -m "feat: add project configuration and metrics utilities"
```

### Task 3: Create __init__.py files for package structure

**Files:**
- Create: `src/__init__.py`
- Create: `src/data/__init__.py`
- Create: `src/analysis/__init__.py`
- Create: `src/models/__init__.py`
- Create: `src/visualization/__init__.py`

- [ ] **Step 1: Create all __init__.py files**

```bash
# These can be empty for now
touch src/__init__.py
touch src/data/__init__.py
touch src/analysis/__init__.py
touch src/models/__init__.py
touch src/visualization/__init__.py
```

- [ ] **Step 2: Commit package structure**

```bash
git add src/
git commit -m "feat: create Python package structure"
```

---

## Phase 2: Data Loading & Processing

### Task 4: Create data loader module

**Files:**
- Create: `src/data/loader.py`
- Create: `tests/test_loader.py`

- [ ] **Step 1: Write failing test for load_csv**

```python
# tests/test_loader.py
import pytest
import pandas as pd
from pathlib import Path
from src.data.loader import load_csv, load_from_api

def test_load_csv_returns_dataframe():
    """Test that load_csv returns a DataFrame"""
    # This will fail until loader.py is created
    df = load_csv("sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_load_csv_with_date_parsing():
    """Test that dates are parsed correctly"""
    df = load_csv("sample.csv", date_column="timestamp")
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

def test_load_csv_file_not_found():
    """Test handling of missing files"""
    with pytest.raises(FileNotFoundError):
        load_csv("nonexistent.csv")
```

- [ ] **Step 2: Write data loader module**

```python
# src/data/loader.py
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from src.utils.config import RAW_DATA_DIR

def load_csv(
    filename: str,
    date_column: Optional[str] = None,
    data_dir: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """
    Load CSV file and parse dates if specified.
    
    Args:
        filename: Name of CSV file
        date_column: Column name to parse as datetime
        data_dir: Directory to load from (default: RAW_DATA_DIR)
    
    Returns:
        DataFrame with loaded data
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if data_dir is None:
        data_dir = RAW_DATA_DIR
    
    filepath = Path(data_dir) / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column])
    
    return df

def load_from_api(
    api_url: str,
    params: Optional[dict] = None,
    date_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load data from API endpoint.
    
    Args:
        api_url: URL of API endpoint
        params: Query parameters
        date_column: Column to parse as datetime
    
    Returns:
        DataFrame with API response data
    """
    import requests
    
    response = requests.get(api_url, params=params or {})
    response.raise_for_status()
    
    data = response.json()
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([data])
    
    if date_column and date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
    
    return df
```

- [ ] **Step 3: Run test to verify it passes**

```bash
pytest tests/test_loader.py -v
# Expected: All tests should pass
```

- [ ] **Step 4: Commit data loader**

```bash
git add src/data/loader.py tests/test_loader.py
git commit -m "feat: add data loader module with CSV and API support"
```

### Task 5: Create data processor module

**Files:**
- Create: `src/data/processor.py`
- Create: `tests/test_processor.py`

- [ ] **Step 1: Write tests for data processor**

```python
# tests/test_processor.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.processor import (
    clean_data,
    handle_missing_values,
    aggregate_by_time,
    detect_outliers,
)

def test_clean_data_removes_duplicates():
    """Test that clean_data removes duplicate rows"""
    df = pd.DataFrame({
        "timestamp": ["2024-01-01", "2024-01-01", "2024-01-02"],
        "value": [1, 1, 2]
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    result = clean_data(df, timestamp_col="timestamp")
    assert len(result) == 2

def test_handle_missing_values_forward_fill():
    """Test forward fill method"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "value": [1, np.nan, 3, np.nan, 5]
    })
    
    result = handle_missing_values(df, method="forward_fill")
    assert not result["value"].isna().any()
    assert result["value"].iloc[1] == 1

def test_aggregate_by_time():
    """Test time aggregation"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=24, freq="H"),
        "value": np.arange(24)
    })
    
    result = aggregate_by_time(df, freq="D", agg_func="sum")
    assert len(result) == 1
    assert result["value"].iloc[0] == sum(range(24))

def test_detect_outliers():
    """Test outlier detection"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "value": np.random.normal(10, 1, 100)
    })
    df.loc[50, "value"] = 100  # Add outlier
    
    result = detect_outliers(df, method="iqr")
    assert result["is_outlier"].sum() > 0
```

- [ ] **Step 2: Write data processor module**

```python
# src/data/processor.py
import pandas as pd
import numpy as np
from typing import Optional, Literal

def clean_data(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    remove_duplicates: bool = True,
) -> pd.DataFrame:
    """
    Clean data by removing duplicates and invalid rows.
    
    Args:
        df: Input DataFrame
        timestamp_col: Name of timestamp column
        remove_duplicates: Whether to remove duplicate rows
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    if remove_duplicates:
        df = df.drop_duplicates()
    
    # Sort by timestamp
    if timestamp_col in df.columns:
        df = df.sort_values(timestamp_col)
    
    return df.reset_index(drop=True)

def handle_missing_values(
    df: pd.DataFrame,
    method: Literal["forward_fill", "interpolate", "drop"] = "forward_fill",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    Handle missing values in DataFrame.
    
    Args:
        df: Input DataFrame
        method: Method to use (forward_fill, interpolate, drop)
        limit: Maximum number of consecutive fills
    
    Returns:
        DataFrame with missing values handled
    """
    df = df.copy()
    
    if method == "forward_fill":
        df = df.fillna(method="ffill", limit=limit)
        df = df.fillna(method="bfill")
    elif method == "interpolate":
        df = df.interpolate(method="linear", limit=limit)
    elif method == "drop":
        df = df.dropna()
    
    return df

def aggregate_by_time(
    df: pd.DataFrame,
    freq: str = "D",
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    agg_func: str = "sum",
) -> pd.DataFrame:
    """
    Aggregate data by time frequency.
    
    Args:
        df: Input DataFrame
        freq: Frequency (D=day, H=hour, W=week, M=month)
        timestamp_col: Timestamp column name
        value_col: Value column name to aggregate
        agg_func: Aggregation function (sum, mean, count, etc)
    
    Returns:
        Aggregated DataFrame
    """
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    result = df.set_index(timestamp_col).resample(freq)[value_col].agg(agg_func)
    return result.reset_index()

def detect_outliers(
    df: pd.DataFrame,
    method: Literal["iqr", "zscore"] = "iqr",
    value_col: str = "value",
    threshold: float = 1.5,
) -> pd.DataFrame:
    """
    Detect outliers in data.
    
    Args:
        df: Input DataFrame
        method: Detection method (iqr or zscore)
        value_col: Column to analyze
        threshold: Threshold for outlier detection
    
    Returns:
        DataFrame with is_outlier column added
    """
    df = df.copy()
    
    if method == "iqr":
        Q1 = df[value_col].quantile(0.25)
        Q3 = df[value_col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR
        df["is_outlier"] = (df[value_col] < lower) | (df[value_col] > upper)
    
    elif method == "zscore":
        from scipy import stats
        z_scores = np.abs(stats.zscore(df[value_col]))
        df["is_outlier"] = z_scores > threshold
    
    return df
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_processor.py -v
# Expected: All tests should pass
```

- [ ] **Step 4: Commit data processor**

```bash
git add src/data/processor.py tests/test_processor.py
git commit -m "feat: add data processor with cleaning, aggregation, and outlier detection"
```

---

## Phase 3: Exploratory Data Analysis (EDA)

### Task 6: Create exploratory analysis module

**Files:**
- Create: `src/analysis/exploratory.py`
- Create: `tests/test_exploratory.py`

- [ ] **Step 1: Write tests for EDA functions**

```python
# tests/test_exploratory.py
import pytest
import pandas as pd
import numpy as np
from src.analysis.exploratory import (
    get_summary_statistics,
    detect_patterns,
    correlation_analysis,
)

def test_get_summary_statistics():
    """Test that summary statistics are calculated"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "value": np.random.normal(10, 2, 100)
    })
    
    stats = get_summary_statistics(df, value_col="value")
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats

def test_detect_patterns():
    """Test pattern detection"""
    # Create data with clear daily pattern
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=168, freq="H"),
        "value": np.tile(np.arange(24), 7) + np.random.normal(0, 1, 168)
    })
    
    patterns = detect_patterns(df, timestamp_col="timestamp", value_col="value")
    assert "hourly_mean" in patterns
    assert len(patterns["hourly_mean"]) == 24

def test_correlation_analysis():
    """Test correlation between columns"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "region_a": np.random.normal(10, 2, 100),
        "region_b": np.random.normal(10, 2, 100),
    })
    
    corr = correlation_analysis(df)
    assert isinstance(corr, pd.DataFrame)
    assert corr.shape == (2, 2)
```

- [ ] **Step 2: Write exploratory analysis module**

```python
# src/analysis/exploratory.py
import pandas as pd
import numpy as np
from typing import Dict, Any

def get_summary_statistics(
    df: pd.DataFrame,
    value_col: str = "value"
) -> Dict[str, float]:
    """
    Calculate summary statistics for a value column.
    
    Args:
        df: Input DataFrame
        value_col: Column to analyze
    
    Returns:
        Dictionary with statistics
    """
    return {
        "count": df[value_col].count(),
        "mean": df[value_col].mean(),
        "std": df[value_col].std(),
        "min": df[value_col].min(),
        "q25": df[value_col].quantile(0.25),
        "median": df[value_col].median(),
        "q75": df[value_col].quantile(0.75),
        "max": df[value_col].max(),
        "skew": df[value_col].skew(),
        "kurtosis": df[value_col].kurtosis(),
    }

def detect_patterns(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
) -> Dict[str, Any]:
    """
    Detect temporal patterns in data.
    
    Args:
        df: Input DataFrame
        timestamp_col: Timestamp column
        value_col: Value column
    
    Returns:
        Dictionary with detected patterns
    """
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    patterns = {}
    
    # Hourly pattern
    if (df[timestamp_col].dt.hour >= 0).all():
        patterns["hourly_mean"] = df.groupby(df[timestamp_col].dt.hour)[value_col].mean()
    
    # Daily pattern (day of week)
    patterns["daily_mean"] = df.groupby(df[timestamp_col].dt.dayofweek)[value_col].mean()
    
    # Monthly pattern
    patterns["monthly_mean"] = df.groupby(df[timestamp_col].dt.month)[value_col].mean()
    
    return patterns

def correlation_analysis(
    df: pd.DataFrame,
    numeric_cols: Optional[list] = None,
) -> pd.DataFrame:
    """
    Calculate correlation matrix between columns.
    
    Args:
        df: Input DataFrame
        numeric_cols: Columns to analyze (default: all numeric)
    
    Returns:
        Correlation matrix
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return df[numeric_cols].corr()
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_exploratory.py -v
# Expected: All tests pass
```

- [ ] **Step 4: Commit EDA module**

```bash
git add src/analysis/exploratory.py tests/test_exploratory.py
git commit -m "feat: add exploratory data analysis functions"
```

### Task 7: Create time series analysis module

**Files:**
- Create: `src/analysis/timeseries.py`
- Create: `tests/test_timeseries.py`

- [ ] **Step 1: Write tests for time series functions**

```python
# tests/test_timeseries.py
import pytest
import pandas as pd
import numpy as np
from src.analysis.timeseries import (
    decompose_series,
    check_stationarity,
    calculate_acf,
)

def test_decompose_series():
    """Test time series decomposition"""
    # Create seasonal data
    t = np.arange(0, 100)
    trend = t * 0.1
    seasonal = 5 * np.sin(2 * np.pi * t / 12)
    noise = np.random.normal(0, 0.5, len(t))
    value = trend + seasonal + noise
    
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "value": value
    })
    
    result = decompose_series(df, period=12)
    assert "trend" in result
    assert "seasonal" in result
    assert "residual" in result

def test_check_stationarity():
    """Test stationarity check (ADF test)"""
    # Non-stationary data (random walk)
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "value": np.cumsum(np.random.normal(0, 1, 100))
    })
    
    result = check_stationarity(df, value_col="value")
    assert "adf_statistic" in result
    assert "p_value" in result
    assert "is_stationary" in result

def test_calculate_acf():
    """Test ACF calculation"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
        "value": np.random.normal(0, 1, 100)
    })
    
    acf_result = calculate_acf(df, value_col="value", nlags=20)
    assert len(acf_result) == 21  # lag 0 to 20
```

- [ ] **Step 2: Write time series analysis module**

```python
# src/analysis/timeseries.py
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf
from scipy import signal

def decompose_series(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    period: int = 12,
    model: str = "additive",
) -> Dict[str, np.ndarray]:
    """
    Decompose time series into trend, seasonal, and residual.
    
    Args:
        df: Input DataFrame
        timestamp_col: Timestamp column
        value_col: Value column
        period: Period for seasonality
        model: 'additive' or 'multiplicative'
    
    Returns:
        Dictionary with trend, seasonal, residual arrays
    """
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.set_index(timestamp_col)
    
    decomposition = seasonal_decompose(
        df[value_col],
        model=model,
        period=period,
        extrapolate="fill_mean"
    )
    
    return {
        "trend": decomposition.trend.values,
        "seasonal": decomposition.seasonal.values,
        "residual": decomposition.resid.values,
        "observed": decomposition.observed.values,
    }

def check_stationarity(
    df: pd.DataFrame,
    value_col: str = "value",
    alpha: float = 0.05,
) -> Dict[str, any]:
    """
    Check if time series is stationary using Augmented Dickey-Fuller test.
    
    Args:
        df: Input DataFrame
        value_col: Value column to test
        alpha: Significance level
    
    Returns:
        Dictionary with test results
    """
    result = adfuller(df[value_col].dropna(), autolag="AIC")
    
    return {
        "adf_statistic": result[0],
        "p_value": result[1],
        "n_lags": result[2],
        "n_obs": result[3],
        "is_stationary": result[1] < alpha,
        "critical_values": result[4],
    }

def calculate_acf(
    df: pd.DataFrame,
    value_col: str = "value",
    nlags: int = 40,
    alpha: float = 0.05,
) -> np.ndarray:
    """
    Calculate autocorrelation function (ACF).
    
    Args:
        df: Input DataFrame
        value_col: Value column
        nlags: Number of lags
        alpha: Confidence interval level
    
    Returns:
        ACF values
    """
    return acf(df[value_col].dropna(), nlags=nlags, alpha=alpha, fft=False)
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_timeseries.py -v
# Expected: All tests pass
```

- [ ] **Step 4: Commit time series module**

```bash
git add src/analysis/timeseries.py tests/test_timeseries.py
git commit -m "feat: add time series decomposition and stationarity analysis"
```

---

## Phase 4: Predictive Models

### Task 8: Create base model class

**Files:**
- Create: `src/models/base.py`

- [ ] **Step 1: Write base model class**

```python
# src/models/base.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class TimeSeriesModel(ABC):
    """Abstract base class for time series models"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.training_data = None
        self.history = None
    
    @abstractmethod
    def fit(self, data: np.ndarray, **kwargs) -> None:
        """Fit model to training data"""
        pass
    
    @abstractmethod
    def forecast(self, steps: int = 1) -> np.ndarray:
        """Make forecast for next N steps"""
        pass
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
        
        Returns:
            Dictionary with metrics
        """
        from src.utils.metrics import calculate_mae, calculate_rmse, calculate_mape
        
        return {
            "mae": calculate_mae(y_true, y_pred),
            "rmse": calculate_rmse(y_true, y_pred),
            "mape": calculate_mape(y_true, y_pred),
        }
```

- [ ] **Step 2: Commit base model**

```bash
git add src/models/base.py
git commit -m "feat: add base model class for time series"
```

### Task 9: Create ARIMA model implementation

**Files:**
- Create: `src/models/arima.py`
- Create: `tests/test_arima.py`

- [ ] **Step 1: Write test for ARIMA model**

```python
# tests/test_arima.py
import pytest
import numpy as np
import pandas as pd
from src.models.arima import ARIMAModel

def test_arima_fit_and_forecast():
    """Test ARIMA fitting and forecasting"""
    # Create simple time series
    np.random.seed(42)
    data = np.cumsum(np.random.normal(0, 1, 100))
    
    model = ARIMAModel(order=(1, 1, 1))
    model.fit(data)
    
    assert model.is_fitted
    
    forecast = model.forecast(steps=10)
    assert len(forecast) == 10

def test_arima_with_seasonal():
    """Test ARIMA with seasonal component"""
    # Create seasonal data
    t = np.arange(100)
    data = 10 + 5 * np.sin(2 * np.pi * t / 12) + np.random.normal(0, 1, 100)
    
    model = ARIMAModel(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model.fit(data)
    
    forecast = model.forecast(steps=24)
    assert len(forecast) == 24
```

- [ ] **Step 2: Write ARIMA model**

```python
# src/models/arima.py
import numpy as np
from typing import Tuple, Optional
from statsmodels.tsa.arima.model import ARIMA
from src.models.base import TimeSeriesModel

class ARIMAModel(TimeSeriesModel):
    """ARIMA (AutoRegressive Integrated Moving Average) Model"""
    
    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
    ):
        """
        Initialize ARIMA model.
        
        Args:
            order: (p, d, q) for AR, I, MA components
            seasonal_order: (P, D, Q, s) for seasonal ARIMA
        """
        super().__init__("ARIMA")
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted_model = None
    
    def fit(self, data: np.ndarray, **kwargs) -> None:
        """
        Fit ARIMA model to data.
        
        Args:
            data: Time series data
        """
        self.training_data = data.copy()
        
        if self.seasonal_order:
            self.model = ARIMA(
                data,
                order=self.order,
                seasonal_order=self.seasonal_order,
            )
        else:
            self.model = ARIMA(data, order=self.order)
        
        self.fitted_model = self.model.fit()
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
        
        forecast_result = self.fitted_model.get_forecast(steps=steps)
        return forecast_result.predicted_mean.values
    
    def get_diagnostics(self) -> dict:
        """Get model diagnostics"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return {
            "aic": self.fitted_model.aic,
            "bic": self.fitted_model.bic,
            "summary": str(self.fitted_model.summary()),
        }
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_arima.py -v
# Expected: All tests pass
```

- [ ] **Step 4: Commit ARIMA model**

```bash
git add src/models/arima.py tests/test_arima.py
git commit -m "feat: add ARIMA model for time series forecasting"
```

---

## Phase 5: Visualization

### Task 10: Create visualization module

**Files:**
- Create: `src/visualization/plotter.py`

- [ ] **Step 1: Write visualization functions**

```python
# src/visualization/plotter.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List

class TimeSeriesPlotter:
    """Utility class for time series visualization"""
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """Initialize plotter with style"""
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
        """
        Plot basic time series.
        
        Args:
            df: DataFrame with data
            timestamp_col: Column name for timestamps
            value_col: Column name for values
            title: Plot title
            figsize: Figure size
        
        Returns:
            Matplotlib figure
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
    
    def plot_decomposition(
        self,
        decomposition_dict: dict,
        timestamps: np.ndarray,
        figsize: tuple = (14, 10),
    ) -> plt.Figure:
        """
        Plot time series decomposition.
        
        Args:
            decomposition_dict: Dict with trend, seasonal, residual
            timestamps: Array of timestamps
            figsize: Figure size
        
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        
        axes[0].plot(timestamps, decomposition_dict["observed"], color="navy")
        axes[0].set_ylabel("Observed")
        
        axes[1].plot(timestamps, decomposition_dict["trend"], color="green")
        axes[1].set_ylabel("Trend")
        
        axes[2].plot(timestamps, decomposition_dict["seasonal"], color="orange")
        axes[2].set_ylabel("Seasonal")
        
        axes[3].plot(timestamps, decomposition_dict["residual"], color="red")
        axes[3].set_ylabel("Residual")
        axes[3].set_xlabel("Date")
        
        fig.suptitle("Time Series Decomposition", fontsize=14)
        fig.tight_layout()
        return fig
    
    def plot_forecast(
        self,
        df: pd.DataFrame,
        forecast: np.ndarray,
        timestamp_col: str = "timestamp",
        value_col: str = "value",
        title: str = "Forecast",
        figsize: tuple = (14, 5),
    ) -> plt.Figure:
        """
        Plot actual values and forecast.
        
        Args:
            df: DataFrame with actual data
            forecast: Array of forecasted values
            timestamp_col: Column name for timestamps
            value_col: Column name for values
            title: Plot title
            figsize: Figure size
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(df[timestamp_col], df[value_col], label="Observed", linewidth=1.5)
        
        # Forecast timestamps
        last_date = df[timestamp_col].iloc[-1]
        freq = pd.infer_freq(df[timestamp_col])
        forecast_dates = pd.date_range(start=last_date, periods=len(forecast) + 1, freq=freq)[1:]
        
        ax.plot(forecast_dates, forecast, label="Forecast", color="red", linestyle="--", linewidth=1.5)
        
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    def plot_acf_pacf(
        self,
        acf_values: np.ndarray,
        title: str = "Autocorrelation",
        figsize: tuple = (14, 5),
    ) -> plt.Figure:
        """
        Plot ACF values.
        
        Args:
            acf_values: Array of ACF values
            title: Plot title
            figsize: Figure size
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        lags = np.arange(len(acf_values))
        ax.stem(lags, acf_values, basefmt=" ")
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
        
        # Confidence interval
        n = 100  # Approximate from acf calculation
        conf_interval = 1.96 / np.sqrt(n)
        ax.axhline(y=conf_interval, color="red", linestyle="--", alpha=0.5)
        ax.axhline(y=-conf_interval, color="red", linestyle="--", alpha=0.5)
        
        ax.set_xlabel("Lag")
        ax.set_ylabel("ACF")
        ax.set_title(title)
        
        fig.tight_layout()
        return fig
```

- [ ] **Step 2: Commit visualization module**

```bash
git add src/visualization/plotter.py
git commit -m "feat: add time series visualization utilities"
```

---

## Phase 6: Create Example Notebook

### Task 11: Create EDA notebook

**Files:**
- Create: `notebooks/01-eda.ipynb`

- [ ] **Step 1: Create notebook with imports and data loading**

This notebook will:
- Load or generate sample data
- Perform basic statistics
- Create visualizations
- Detect patterns

Content example:

```python
# Cell 1: Imports
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Cell 2: Generate sample air raid alerts data
np.random.seed(42)
dates = pd.date_range("2024-01-01", periods=365, freq="D")
# Trend upward, seasonal pattern, random noise
trend = np.linspace(5, 15, 365)
seasonal = 5 * np.sin(2 * np.pi * np.arange(365) / 30)
noise = np.random.normal(0, 2, 365)
alerts = trend + seasonal + noise
alerts = np.maximum(alerts, 0)  # No negative alerts

df = pd.DataFrame({
    "date": dates,
    "alerts": alerts
})

# Cell 3: Load analysis modules
from src.analysis.exploratory import get_summary_statistics, detect_patterns
from src.analysis.timeseries import decompose_series, check_stationarity

# Cell 4: Summary statistics
stats = get_summary_statistics(df, value_col="alerts")
print(pd.Series(stats))

# Cell 5: Decomposition
decomp = decompose_series(df, timestamp_col="date", value_col="alerts", period=30)

# Cell 6: Check stationarity
stationarity = check_stationarity(df, value_col="alerts")
print(f"Is stationary: {stationarity['is_stationary']}")

# Cell 7: Visualizations
from src.visualization.plotter import TimeSeriesPlotter
plotter = TimeSeriesPlotter()
fig = plotter.plot_series(df, timestamp_col="date", value_col="alerts")
plt.show()
```

- [ ] **Step 2: Commit notebook**

```bash
git add notebooks/01-eda.ipynb
git commit -m "docs: add exploratory data analysis notebook"
```

---

## Phase 7: Final Setup

### Task 12: Create setup.py and installation guide

**Files:**
- Create: `setup.py`
- Modify: `README.md`

- [ ] **Step 1: Write setup.py**

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="air-raid-alerts-analysis",
    version="0.1.0",
    description="Time Series Analysis of Air Raid Alerts in Ukraine",
    author="Your Name",
    author_email="sergkern1@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "statsmodels>=0.13.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
    ],
    extras_require={
        "dev": ["pytest>=6.2.0", "jupyter>=1.0.0"],
    },
)
```

- [ ] **Step 2: Update README with setup instructions**

```markdown
# Air Raid Alerts Time Series Analysis

...

## Installation

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install project in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Run Tests
```bash
pytest tests/ -v
```

### Jupyter Analysis
```bash
jupyter notebook notebooks/
```

### Example Usage
```python
from src.data.loader import load_csv
from src.analysis.exploratory import get_summary_statistics
from src.models.arima import ARIMAModel

# Load data
df = load_csv("alerts.csv", date_column="timestamp")

# Analyze
stats = get_summary_statistics(df)

# Forecast
model = ARIMAModel(order=(1,1,1))
model.fit(df["value"].values)
forecast = model.forecast(steps=30)
```

...
```

- [ ] **Step 3: Commit setup files**

```bash
git add setup.py README.md
git commit -m "feat: add project setup and installation guide"
```

---

## Summary of All Tasks

✅ **Phase 1 - Infrastructure:**
- Task 1: requirements.txt
- Task 2: Config module
- Task 3: Package structure

✅ **Phase 2 - Data:**
- Task 4: Data loader
- Task 5: Data processor

✅ **Phase 3 - EDA:**
- Task 6: Exploratory analysis
- Task 7: Time series analysis

✅ **Phase 4 - Modeling:**
- Task 8: Base model class
- Task 9: ARIMA model

✅ **Phase 5 - Visualization:**
- Task 10: Visualization module

✅ **Phase 6-7 - Documentation:**
- Task 11: Example notebook
- Task 12: Setup and README

---

## Next Steps After Plan Completion

1. **Run all tests:** `pytest tests/ -v`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Test with real data:** Integrate actual air raid alerts data
4. **Extend models:** Add Prophet, LSTM, or ensemble methods
5. **Create reports:** Generate automated analysis reports
