# Air Raid Alerts MVP Design — 1 Day Challenge

**Goal:** Complete working project with analysis and model in 1 day (12 hours)

**Architecture:** 3-source system with cross-validation

**Tech Stack:** pandas, numpy, matplotlib, alerts-ua-py, statsmodels

---

## 🎯 System Design

### Data Flow:
```
3 DATA SOURCES (parallel)
    ├─ GitHub Vadimkin (CSV) → 30 min
    ├─ Kaggle dimakyn (CSV) → 15 min
    └─ Alerts-ua-py API → 90 min (+ registration)
        ↓
VALIDATION & CROSS-CHECK (30 min)
    ├─ Do data match for common period?
    ├─ Anomalies in sources?
    └─ Final dataset (combined)
        ↓
ANALYSIS (EDA) (3 hours)
    ├─ Regional statistics
    ├─ Daily/weekly patterns
    ├─ Trends
    └─ Visualization
        ↓
MODEL (ARIMA) (2 hours)
    ├─ Train on historical dataset
    ├─ Forecast for 7 days
    └─ Validation
        ↓
REPORT (Jupyter Notebook) (1 hour)
    └─ Conclusions + graphs + insights
```

---

## 📁 Project Structure (SIMPLIFIED for 1 day)

```
air-raid-alerts-analysis/
├── data/
│   ├── raw/
│   │   ├── github_vadimkin.csv         # Downloaded
│   │   ├── kaggle_dimakyn.csv          # Downloaded
│   │   └── alerts_api_live.csv         # Loaded via API
│   └── processed/
│       └── validated_combined.csv      # Combined dataset
├── src/
│   ├── loader.py                       # Load from 3 sources
│   ├── validator.py                    # Cross-validation
│   └── analyzer.py                     # EDA + ARIMA
├── notebooks/
│   └── 01-full-analysis.ipynb          # MAIN RESULT
├── requirements.txt
└── README.md
```

---

## 🔧 Components (Minimal)

### 1. **Loader** (src/loader.py)
- `load_github()` — read CSV from GitHub
- `load_kaggle()` — read CSV from Kaggle
- `load_alerts_api()` — fetch from Alerts-ua-py API

### 2. **Validator** (src/validator.py)
- `cross_validate()` — compare 3 sources
- `detect_anomalies()` — find discrepancies
- `combine_sources()` — merge reliable data

### 3. **Analyzer** (src/analyzer.py)
- `basic_stats()` — statistics
- `detect_patterns()` — patterns
- `arima_forecast()` — forecasting

### 4. **Notebook** (notebooks/01-full-analysis.ipynb)
- Import modules
- Load + validation
- EDA with graphs
- ARIMA model
- Conclusions

---

## ⏱️ EXACT TIMELINE

| Phase | What | Time | Solution |
|-------|------|------|----------|
| 1 | Load GitHub CSV | 30 min | `pd.read_csv()` |
| 2 | Load Kaggle CSV | 15 min | `pd.read_csv()` |
| 3 | Register Alerts.in.ua + token | 15 min | Web form |
| 4 | Load Alerts-ua-py API | 60 min | `AlertsUA()` |
| 5 | Cross-validate 3 sources | 30 min | `validator.py` |
| 6 | EDA + Visualization | 3 hours | `analyzer.py` |
| 7 | ARIMA model + forecast | 2 hours | `statsmodels` |
| 8 | Final Notebook | 1 hour | `.ipynb` |
| **TOTAL** | | **~12 hours** | ✅ |

---

## 📊 Expected Result for Day

✅ **Loaded data:** ~100,000+ records from 3 sources  
✅ **Validation:** Consistency checked between sources  
✅ **EDA:** 5-7 graphs + pattern insights  
✅ **Model:** ARIMA with 7-day forecast  
✅ **Report:** Jupyter notebook with conclusions  
✅ **Code:** Python modules for reuse  

---

## 🎁 Bonus: Cross-Validate Three Sources

```python
# Example: do data match?
github_daily = github_df.groupby('date').size()
kaggle_daily = kaggle_df.groupby('date').size()
alerts_daily = alerts_df.groupby('date').size()

# Compare for common period
common_period = (
    max(github_df['date'].min(), kaggle_df['date'].min(), alerts_df['date'].min()),
    min(github_df['date'].max(), kaggle_df['date'].max(), alerts_df['date'].max())
)

# Correlation between sources
correlation = github_daily.corr(kaggle_daily)
print(f"GitHub ↔ Kaggle correlation: {correlation:.2%}")
```

---

## 🚀 Getting Started

1. Create `src/loader.py`, `src/validator.py`, `src/analyzer.py`
2. Download GitHub + Kaggle CSV to `data/raw/`
3. Create Alerts API token
4. Write API loader
5. Cross-validate data
6. Write EDA analysis
7. Build ARIMA model
8. Assemble everything in Notebook
9. Commit and done! ✅

---

## ❌ WHAT WE DON'T DO (to fit in one day)

- ❌ Ensemble models (Prophet, LSTM)
- ❌ Interactive Streamlit applications
- ❌ Web API (FastAPI)
- ❌ Docker containers
- ❌ CI/CD pipelines
- ❌ Extended documentation

All that comes later, after MVP! 🚀
