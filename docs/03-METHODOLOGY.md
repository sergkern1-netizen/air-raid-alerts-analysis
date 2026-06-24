# Methodology: How We Analyzed the Data

## Analysis Approach

This is a **descriptive time-series analysis** of historical alert data. We use standard statistical techniques to understand patterns, trends, and regional variations.

### What This Is
- ✅ **Descriptive:** Describing what happened in the data
- ✅ **Statistical:** Using quantitative analysis methods
- ✅ **Exploratory:** Discovering patterns and anomalies
- ✅ **Comparative:** Comparing regions, time periods, and trends

### What This Is NOT
- ❌ **Predictive:** We don't forecast future alerts
- ❌ **Causal:** We don't explain *why* alerts occurred
- ❌ **Experimental:** No controlled experiments or A/B testing
- ❌ **Machine Learning:** No complex ML models used

## Analysis Steps

### 1. Data Preparation
- Loaded and merged two independent data sources
- Normalized region names and timestamps
- Calculated derived metrics (duration, aggregates)
- Validated data quality and completeness
- **Output:** 20 clean CSV files ready for analysis

### 2. Descriptive Statistics
For each region and time period, we calculated:
- **Count:** Total number of alerts
- **Central Tendency:** Mean, median, mode
- **Dispersion:** Standard deviation, range, quartiles
- **Time Distribution:** First alert date, last alert date

**Purpose:** Understand basic characteristics of the data

### 3. Temporal Analysis
Examined how alerts changed over time:
- **Trends:** Overall direction (increasing/decreasing)
- **Seasonality:** Regular patterns (monthly, yearly cycles)
- **Volatility:** How much daily alert counts varied
- **Change Points:** When the pattern significantly shifted

**Methods:**
- Year-over-year comparison
- Month-over-month analysis
- Rolling averages (30-day smoothing)
- Percentage change calculation

**Output:** Tables showing trends by year, month, quarter

### 4. Regional Analysis
Examined geographic variation:
- **Ranking:** Which regions had most/least alerts
- **Concentration:** How alerts distributed across regions
- **Variation:** How duration differed by region
- **Recent Changes:** Where escalation occurred recently

**Methods:**
- Regional aggregation
- Ranking and sorting
- Comparison of historical vs. recent periods
- Escalation factor calculation (recent/historical ratio)

### 5. Pattern Recognition
Identified interesting patterns:
- Peak periods (when alerts were highest)
- Quiet periods (when alerts were lowest)
- Regional disparities (unequal distribution)
- Recent escalation in western regions

**Methods:**
- Sorting and ranking
- Threshold analysis
- Comparative analysis

## Key Metrics We Used

### Daily Alert Count
- **What it measures:** Total air raid alerts per day
- **Why:** Indicates intensity of threat on specific dates
- **Limitation:** Doesn't distinguish alert severity or impact

### Average Alert Duration
- **What it measures:** How long typical alert lasts (in minutes)
- **Why:** Longer alerts may indicate more serious threat
- **Limitation:** Duration may reflect distance or alert procedures, not severity

### Year-over-Year Change
- **What it measures:** Percentage change from one year to same period previous year
- **Why:** Shows acceleration or deceleration of threat
- **Formula:** (Current Year - Previous Year) / Previous Year × 100%

### Escalation Factor
- **What it measures:** How much alert frequency increased recently vs. historically
- **Why:** Identifies regions where situation is rapidly worsening
- **Formula:** Recent Period Average / Historical Period Average

### Regional Ranking
- **What it measures:** Where regions stand relative to each other
- **Why:** Shows geographic concentration of threat
- **Method:** Simple ranking by total alert count

## Statistical Techniques Used

### Aggregation
- Grouped raw data by day, month, year, region
- Summed alerts for each group
- Calculated averages within each group

### Comparison
- Compared regions to identify disparities
- Compared years to identify trends
- Compared recent vs. historical periods

### Rolling Averages
- Used 30-day moving average to smooth daily variability
- Shows underlying trend without day-to-day noise
- Helps identify major shifts

### Percentages and Ratios
- Year-over-year percentage change
- Escalation factors (recent/historical ratio)
- Percentage of total for regional breakdown

## Tools Used

### Programming Language
- **Python 3.11.9** — Data processing and analysis

### Python Libraries
- **pandas** — Data manipulation and aggregation
- **numpy** — Numerical calculations
- **scikit-learn** — Statistical functions

### Data Formats
- **CSV** — For data storage and export
- **Markdown** — For documentation
- **Text** — For formatted tables

## Limitations of This Approach

1. **No Causality:** We describe what happened, not why
2. **Simple Statistics:** We don't use advanced ML or econometric models
3. **No Uncertainty Intervals:** We report point estimates, not confidence ranges
4. **Snapshot in Time:** Analysis reflects data available as of June 2026
5. **No Validation:** Results not validated against independent dataset

## How to Interpret Results

### When You See "Escalation of 75.8%"
- This means: alerts increased from 52,270 (2024) to 91,878 (2025)
- This is: a real, measurable change in the data
- This is NOT: a prediction of future escalation
- Consider: What events in 2025 might explain this increase?

### When You See "Top 3 Regions = 43.9%"
- This means: Dnipropetrovska, Kharkivska, Donetska had 43.9% of all alerts
- This reflects: Geographic concentration of military operations
- This suggests: These regions faced disproportionate threat
- Consider: What makes these regions strategically important?

### When You See "3.4x Escalation in Lviv"
- This means: Recent period (6 months) had 3.4× more alerts than historical average
- This is: Especially important because Lviv was previously less affected
- This suggests: Threat is expanding to previously safer regions
- This is NOT: An absolute measure of danger (depends on baseline)

## Reproducibility

All analysis is fully reproducible:
1. Raw data is available in `data/raw/`
2. Processing code is in `src/analysis/`
3. Processed data is in `data/processed/`
4. All steps are documented and scriptable

To reproduce:
```bash
python src/analysis/data_preparation.py
python src/analysis/temporal_analysis.py
python src/analysis/regional_analysis.py
python src/analysis/generate_findings.py
```

---

**Next:** [Key Findings](04-FINDINGS.md) — What the data revealed
