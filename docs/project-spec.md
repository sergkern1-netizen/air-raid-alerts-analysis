# Air Raid Alerts Time Series Analysis — Project Specification

## 1. Project Overview

**Name:** Time Series Analysis of Air Raid Alerts in Ukraine

**Goal:** Develop a Python application for analyzing and forecasting time series of air raid alerts in Ukraine, including pattern detection, statistical analysis, and predictive model building.

**Type:** Data Science Pet-Project

**Implementation Language:** Python 3.9+

## 2. Functional Requirements

### 2.1 Data Loading & Processing
- Obtain air raid alert data from open sources (API or CSV)
- Data parsing and validation
- Handle missing values and outliers
- Aggregate data by time periods (hour, day, week)
- Geospatial information (by regions, if available)

### 2.2 Exploratory Data Analysis (EDA)
- Statistical description of data (mean, std, quantiles)
- Distribution analysis
- Temporal pattern detection (daily, weekly, seasonal)
- Correlation analysis between regions
- Anomaly and outlier detection

### 2.3 Time Series Analysis
- Time series decomposition (trend, seasonality, residual)
- Autocorrelation analysis (ACF, PACF)
- Stationarity tests (ADF test)
- Spectral density analysis

### 2.4 Predictive Models
- ARIMA/SARIMA for univariate series
- Prophet for seasonal data (optional)
- LSTM/RNN for deep learning (optional)
- Ensemble methods for forecast combination
- Cross-validation and metric evaluation (MAE, RMSE, MAPE)

### 2.5 Visualization & Reports
- Time series plots (raw series, aggregated data)
- Seasonal and trend components
- Forecasts with confidence intervals
- Model comparison
- Interactive visualizations (optional)

## 3. Technical Stack

### Core Libraries:
- **pandas** — tabular data manipulation
- **numpy** — numerical computing
- **matplotlib, seaborn** — static visualization
- **plotly** — interactive graphs
- **scikit-learn** — ML models and metrics
- **statsmodels** — time series analysis (ARIMA, decomposition)
- **prophet** — forecasting (optional)
- **tensorflow/keras** — deep learning (optional)

### Additional:
- **pytest** — unit testing
- **jupyter** — interactive analysis
- **requests** — API interaction

## 4. Project Architecture

```
src/
├── data/
│   ├── loader.py           # Load data from sources
│   └── processor.py        # Data transformation & processing
├── analysis/
│   ├── exploratory.py      # EDA functions
│   ├── timeseries.py       # Time series analysis
│   └── statistics.py       # Statistical functions
├── models/
│   ├── base.py             # Base model class
│   ├── arima.py            # ARIMA model
│   ├── ensemble.py         # Model ensembles
│   └── neural.py           # Neural networks (optional)
├── visualization/
│   ├── plotter.py          # Visualization functions
│   └── reports.py          # Report generation
└── utils/
    ├── config.py           # Project configuration
    └── metrics.py          # Evaluation metrics

notebooks/
├── 01-eda.ipynb            # Exploratory analysis
├── 02-timeseries-analysis.ipynb
├── 03-modeling.ipynb       # Model building
└── 04-results.ipynb        # Results and conclusions
```

## 5. Data Sources

### Potential Sources:
1. **Telegram API** (main source of alert news)
2. **Open databases** of air raid alerts
3. **CSV files** with historical data (if available)
4. **Web scraping** (if necessary)

## 6. Development Phases

### Phase 1: Infrastructure & Data
- Dependency installation
- Data loading and processing module creation
- Test data preparation

### Phase 2: EDA & Exploration
- Basic exploratory analysis
- Pattern detection
- Visualization

### Phase 3: Time Series Analysis
- Decomposition
- Stationarity tests
- Autocorrelation analysis

### Phase 4: Predictive Models
- ARIMA model
- Evaluation and validation
- Comparison with baseline models

### Phase 5: Extensions (optional)
- Model ensemble
- Deep learning
- Interactive visualization

## 7. Success Criteria

✓ Real air raid alert data loaded  
✓ Complete EDA analysis with pattern detection completed  
✓ Working ARIMA model with adequate metrics built  
✓ Visualization of main results implemented  
✓ Conclusions and insights documented

## 8. Timeline

- Phase 1-2: 2-3 days
- Phase 3-4: 3-5 days
- Phase 5: 2-3 days (optional)
- Total: 7-11 days

## 9. Known Limitations

- Data quality and completeness depend on source
- Predictive models are limited by historical patterns
- New events (new types of attacks) may break patterns
