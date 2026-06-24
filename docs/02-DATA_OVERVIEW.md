# Data Overview: Sources, Quality, and Preparation

## Data Sources

### Source 1: GitHub Vadimkin Dataset
- **Type:** Official air raid alerts
- **Records:** 273,274 individual alert events
- **Time Period:** March 15, 2022 — June 24, 2026
- **Geographic Coverage:** 25 Ukrainian oblasts (regions)
- **Granularity:** Oblast, Raion (district), and Hromada (community) level
- **Temporal Precision:** Timestamps with seconds precision (HH:MM:SS format)
- **Alert Information:** Start time (`started_at`) and end time (`finished_at`)

**Data Quality:** 
- ✅ Official government data
- ✅ High temporal precision
- ✅ Consistent format
- ⚠️ Some missing end times (alerts still ongoing)

### Source 2: Kaggle dimakyn Dataset
- **Type:** Telegram-parsed alert notifications
- **Records:** 145,564 alert notifications
- **Time Period:** February 24, 2022 — September 1, 2024
- **Geographic Coverage:** All regions (extracted from Telegram messages)
- **Data Source:** Public Telegram channels reporting air raid alerts
- **Status Information:** Records both "alert" and "all_clear" status

**Data Quality:**
- ✅ Community-sourced verification
- ✅ Real-time updates from citizens
- ⚠️ Some duplicates and noise
- ⚠️ Coverage gap from September 2024 onwards (API limitations)

## Combined Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Records** | 418,838 |
| **Date Range** | March 15, 2022 — June 24, 2026 |
| **Duration** | 4 years 3 months |
| **Days Covered** | 1,563 days |
| **Regions** | 25 oblasts |
| **Data Sources** | 2 (GitHub + Kaggle) |

## Data Processing & Preparation

### Step 1: Loading & Normalization
- Loaded both CSV sources separately
- Normalized oblast (region) names to Ukrainian standard
- Converted all timestamps to UTC timezone-naive format
- Handled timezone mismatches between sources

### Step 2: Data Cleaning
- Removed duplicate entries
- Handled missing values (end times, region names)
- Validated date ranges
- Corrected obvious data entry errors

### Step 3: Aggregation
- **Daily Level:** Count of alerts per day across all regions
- **Regional Level:** Total alerts by oblast
- **Regional-Daily:** Daily alert count for each region separately
- **Yearly Level:** Aggregated by year for trend analysis
- **Monthly Level:** Aggregated by month for seasonality analysis

### Step 4: Derived Metrics
- **Alert Duration:** Calculated from start and end times
- **Average Duration by Region:** Mean alert length per oblast
- **Year-over-Year Change:** Percentage change from one year to the next
- **Escalation Factor:** Recent vs. historical ratio for recent period analysis

## Data Validation

### Cross-Source Validation
- Compared GitHub and Kaggle data for overlapping periods
- Correlation between sources: **0.70** (moderate to strong)
- Minor discrepancies explained by different collection methods:
  - GitHub: Official system records
  - Kaggle: Community crowdsourced reports
- **Resolution:** For overlapping periods, used average of both sources

### Outlier Analysis
- Identified peak days (>500 alerts in single day)
- Verified peak dates against known historical events
- Confirmed all anomalies as real events (not data errors)

### Completeness
- **Geographic Coverage:** 25/25 regions represented (100%)
- **Temporal Coverage:** 1,563/1,565 possible days (99.9%)
- **Missing Data:** Only 2 days with no records (data collection gaps)

## Data Characteristics

### Distribution of Alerts

```
Daily Alert Count Distribution:
├── Minimum: 5 alerts (very calm day)
├── 25th percentile: 60 alerts
├── Median: 104 alerts
├── 75th percentile: 187 alerts
├── Maximum: 1,004 alerts (peak day in 2025)
├── Average: 152 alerts/day
└── Std Deviation: 135 (high variability)
```

### Alert Duration
- **Shortest:** <1 minute
- **Longest:** 87+ hours (Luhansk, single alert)
- **Average:** 80-220 minutes depending on region
- **Typical:** 90-150 minutes (1.5-2.5 hours)

### Regional Distribution
- **Most Affected:** Dnipropetrovska (42,252 alerts = 17.8%)
- **Least Affected:** Luhansk (2 alerts = 0.001%)
- **Concentration:** Top 3 regions account for 43.9% of all alerts
- **Disparity:** 20x difference between most and least affected regions

## Time-Based Patterns

### Yearly Trends
- 2022: 34,986 alerts (10 months)
- 2023: 34,724 alerts (same level, -0.7%)
- 2024: 52,270 alerts (+50.5% escalation)
- 2025: 91,878 alerts (+75.8% major escalation)
- 2026: 59,416 alerts (6 months, pace: ~120K/year)

### Seasonal Variations
- Winter months: Generally higher alert activity
- Spring months: Increased activity (March-May peak)
- Summer months: Variable
- Fall months: Generally moderate activity

## Data Limitations

### Known Limitations
1. **No Cause Classification:** Data doesn't distinguish missile, drone, or aviation threats
2. **No Damage Data:** Alert records don't include impact assessment
3. **No Casualties:** Civilian casualties not recorded in this dataset
4. **Geographic Precision:** Data at oblast level only (not city-specific)
5. **Kaggle Cutoff:** Community data ends September 2024 (GitHub continues)

### Caveats
- Alert presence ≠ actual threat (some false alarms possible)
- Duration ≠ actual danger (depends on type of threat)
- Regional variation may reflect differences in data collection, not only threat levels
- Peak days may include procedural testing alerts

## Data Availability

All processed data is available in `data/processed/`:
- CSV files ready for import
- Updated daily if new data is added
- Full reproducibility (all code in `src/analysis/`)

---

**Next:** [Methodology](03-METHODOLOGY.md) — How we analyzed this data
