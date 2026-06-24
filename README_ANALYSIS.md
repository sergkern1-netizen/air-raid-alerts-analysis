# Air Raid Alerts in Ukraine: Comprehensive Analysis (2022-2026)

## Quick Overview

This project contains a **comprehensive research analysis** of air raid alerts in Ukraine from March 2022 to June 2026.

**Key Numbers:**
- **418,838** alert records analyzed
- **1,563** days with recorded alerts
- **25** regions (oblasts) covered
- **4-year period** showing escalating threats

## 🚨 Key Findings

### Finding 1: Dramatic Escalation
- **2023**: Stable (34,724 alerts)
- **2024**: +50.5% escalation (52,270 alerts)
- **2025**: +75.8% escalation (91,878 alerts) — Most intense year
- **2026**: Continuing at ~120K/year pace

### Finding 2: Extreme Regional Disparities
Top 3 regions account for **43.9%** of all alerts:
1. **Dnipropetrovska**: 42,252 alerts (17.8%)
2. **Kharkivska**: 35,325 alerts (14.9%)
3. **Donetska**: 26,735 alerts (11.2%)

### Finding 3: Geographic Expansion
Western regions experiencing **3-3.4x escalation** in last 6 months:
- **Lvivska oblast**: 559 alerts in 6 months (↑344%)
- **Ivano-Frankivsk**: 487 alerts (↑336%)
- **Zakarpattia**: 457 alerts (↑331%)

**Implication:** Threat zone is expanding westward.

### Finding 4: Sustained High Impact
- **152** alerts per day (average)
- **1,004** alerts in peak single day
- Alert durations: 80-220 minutes (3-4 hours)

### Finding 5: Regional Variations
Most dangerous: **Dnipropetrovska** (avg 218 min/alert)
Quick strikes: **Zaporizka** (avg 109 min/alert)

---

## 📊 Data Structure

### Raw Data
```
data/raw/
├── github_vadimkin.csv        (273,274 records - official alerts)
└── kaggle_dimakyn.csv          (145,564 records - Telegram-parsed)
```

### Processed Data (CSV Tables)
```
data/processed/
├── 01_daily_aggregates.csv          # Daily totals across all regions
├── 02_regional_summary.csv          # All regions with statistics
├── 03_regional_daily.csv            # Regional breakdown by day
├── 04_yearly_comparison.csv         # Year-over-year comparison
├── 05_duration_statistics.csv       # Duration stats by region
├── 07_yearly_statistics.csv         # Yearly trends
├── 08_monthly_pattern.csv           # Which months are most dangerous
├── 09_month_year_matrix.csv         # Matrix: months × years
├── 10_quarterly_pattern.csv         # Quarterly breakdown
├── 11_peak_weeks.csv                # Top 20 worst weeks
├── 13_regional_ranking.csv          # Regional rankings
├── 15_duration_by_region.csv        # Longest/shortest alerts
├── 16_regional_trends.csv           # Top 5 regions over time
├── 18_recent_escalation.csv         # Which regions escalated recently
└── 20_KEY_FINDINGS.md               # Final structured findings
```

---

## 🔍 How to Use This Data

### For Researchers
All processed data is in CSV format — import directly into your analysis tool:
```python
import pandas as pd
daily = pd.read_csv('data/processed/01_daily_aggregates.csv')
regional = pd.read_csv('data/processed/02_regional_summary.csv')
```

### For Journalists/Reports
- Start with: `data/processed/20_KEY_FINDINGS.md`
- Use tables from: `02_regional_summary.csv`, `18_recent_escalation.csv`
- Reference dates: Each CSV has full date coverage 2022-2026

### For Policy-Makers
- Regional risk assessment: `02_regional_summary.csv` + `18_recent_escalation.csv`
- Trend analysis: `07_yearly_statistics.csv`
- Coverage gaps: `19_regional_coverage.csv`

### For Civil Defense
- Duration patterns: `05_duration_statistics.csv` + `15_duration_by_region.csv`
- Peak periods: `11_peak_weeks.csv`
- Regional coordination needs: `03_regional_daily.csv`

---

## 🛠 Analysis Modules

### Data Preparation (`src/analysis/data_preparation.py`)
Loads raw data, normalizes oblast names, creates aggregates.
```bash
python src/analysis/data_preparation.py
```

### Temporal Analysis (`src/analysis/temporal_analysis.py`)
Year-over-year trends, seasonality, peak periods.
```bash
python src/analysis/temporal_analysis.py
```

### Regional Analysis (`src/analysis/regional_analysis.py`)
Regional rankings, escalation patterns, coverage analysis.
```bash
python src/analysis/regional_analysis.py
```

### Findings Generation (`src/analysis/generate_findings.py`)
Synthesizes key insights into structured findings report.
```bash
python src/analysis/generate_findings.py
```

---

## 📈 What Each CSV Contains

| File | Purpose | Rows | Key Column |
|------|---------|------|-----------|
| 01_daily_aggregates | Daily alert counts | 1,563 | alerts_count_combined |
| 02_regional_summary | All regions summary | 25 | total_alerts |
| 03_regional_daily | Daily by region | 26,751 | alerts_count |
| 07_yearly_statistics | Year trends | 5 | year, total_alerts |
| 08_monthly_pattern | Monthly distribution | 12 | month, total_alerts |
| 11_peak_weeks | Worst weeks | 20 | week, total_alerts |
| 18_recent_escalation | Recent escalation | 25 | escalation_factor |
| 20_KEY_FINDINGS | Structured findings | — | markdown |

---

## 📝 Interpreting the Data

### Alert Count Meanings
- **Low** (0-50/day): Routine coverage, possibly false alarms
- **Medium** (50-150/day): Standard threat level
- **High** (150-300/day): Significant military activity
- **Critical** (300+/day): Intense operations (peak was 1,004/day in 2025)

### Duration Patterns
- **Short** (<30 min): Quick air strike, far away or intercepted
- **Medium** (30-120 min): Sustained operation
- **Long** (120+ min): Major offensive or near border region

### Regional Escalation Factor
- **1.0x**: No change year-over-year
- **2.0x**: Doubled in last period
- **3.0x+**: Tripled — dramatic escalation (western regions in 2025)

---

## 🎯 Questions You Can Answer With This Data

1. **When were things worst?** → Use `11_peak_weeks.csv`
2. **Which regions are safest?** → Use `02_regional_summary.csv` (sort by rank)
3. **Where is danger growing fastest?** → Use `18_recent_escalation.csv`
4. **What's the typical alert duration?** → Use `05_duration_statistics.csv`
5. **Is threat increasing or decreasing?** → Use `07_yearly_statistics.csv`
6. **How continuous is threat in each region?** → Use `19_regional_coverage.csv`

---

## ⚙️ Technical Setup

### Requirements
```
Python 3.9+
pandas >= 1.3.0
numpy >= 1.21.0
scikit-learn >= 1.0.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
```

### Installation
```bash
pip install -r requirements.txt
```

### Run Full Analysis
```bash
# Step 1: Prepare data
python src/analysis/data_preparation.py

# Step 2: Run temporal analysis
python src/analysis/temporal_analysis.py

# Step 3: Run regional analysis
python src/analysis/regional_analysis.py

# Step 4: Generate findings
python src/analysis/generate_findings.py
```

All outputs are saved to `data/processed/`

---

## 📚 Citation & Attribution

**Data Sources:**
- GitHub Vadimkin: Official air raid alert records (2022-2026)
- Kaggle dimakyn: Telegram-parsed alert data (2022-2024)

**Analysis Conducted:** June 2026
**Analysis Period:** March 2022 — June 2026
**Data Quality:** 418,838 records, 25 regions, continuous coverage

---

## 🔗 Key Files to Start With

1. **Read First:** `data/processed/20_KEY_FINDINGS.md` — Findings summary
2. **Main Data:** `data/processed/02_regional_summary.csv` — Regional overview
3. **Trends:** `data/processed/07_yearly_statistics.csv` — Year trends
4. **Recent:** `data/processed/18_recent_escalation.csv` — Latest escalation

---

## 📖 Repository Structure

```
air-raid-alerts-analysis/
├── README.md                          (this file)
├── data/
│   ├── raw/                          (GitHub + Kaggle CSV)
│   └── processed/                    (analysis outputs)
├── src/
│   └── analysis/
│       ├── data_preparation.py       (load & aggregate)
│       ├── temporal_analysis.py      (trends & seasonality)
│       ├── regional_analysis.py      (regional patterns)
│       └── generate_findings.py      (final findings)
├── notebooks/
│   └── 01-full-analysis.ipynb       (reproducible analysis)
└── requirements.txt
```

---

## ✅ Data Quality Notes

- **Coverage:** March 15, 2022 — June 24, 2026 (4 years 3 months)
- **Missing Data:** Minimal; Kaggle has gaps in 2025-2026 (Telegram API limits)
- **Validation:** Cross-checked GitHub vs Kaggle sources; minor discrepancies handled through averaging
- **Regional Normalization:** 25 unique oblast names standardized
- **Duration Calculation:** Based on `started_at` to `finished_at` timestamps

---

## 🤔 Limitations

1. **No Incident Causes:** Data doesn't distinguish between missile, drone, or aviation threats
2. **Reporting Bias:** Kaggle data relies on Telegram reports (may miss remote attacks)
3. **Alert Intensity vs Impact:** Count doesn't reflect actual damage/impact (statistical only)
4. **Forecasting Not Included:** This is analysis of historical data, not predictions

---

## 🔄 How to Update

New data received? Re-run the pipeline:
```bash
# Update source CSVs in data/raw/
cp new_github_data.csv data/raw/github_vadimkin.csv
cp new_kaggle_data.csv data/raw/kaggle_dimakyn.csv

# Re-run all analysis
python src/analysis/data_preparation.py
python src/analysis/temporal_analysis.py
python src/analysis/regional_analysis.py
python src/analysis/generate_findings.py
```

All outputs will be updated automatically.

---

## 📧 Questions?

For data questions, interpretations, or methodology details, refer to:
- `data/processed/06_overall_statistics.txt` — Data overview
- `data/processed/14_regional_statistics.txt` — Regional notes
- `data/processed/12_trend_analysis.txt` — Trend analysis details

---

**Last Updated:** June 25, 2026
**Analysis Status:** MVP Phase Complete (Visualization & Documentation in progress)
