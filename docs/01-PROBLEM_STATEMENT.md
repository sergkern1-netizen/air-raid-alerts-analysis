# Problem Statement: Understanding Air Raid Alerts in Ukraine

## The Question We're Investigating

**What is the pattern and intensity of air raid threats facing Ukraine since March 2022?**

This analysis seeks to answer critical questions:
- How has the threat intensity changed over time?
- Which regions are most affected?
- Is the threat expanding geographically?
- What are the trends and patterns?

## Why This Matters

Since Russia's full-scale invasion on February 24, 2022, Ukraine has faced unprecedented and continuous aerial threats. Understanding the patterns of these threats is essential for:

### For Civil Defense & Protection
- **Resource Allocation:** Where should civil defense resources be concentrated?
- **Infrastructure Planning:** Which regions need additional shelters and early-warning systems?
- **Preparedness:** Can we predict dangerous periods to enhance readiness?

### For Policy & Decision-Making
- **Strategic Planning:** How to plan long-term resilience strategies?
- **International Support:** Evidence for coordinating international humanitarian aid
- **Documentation:** Creating historical record of civilian impact

### For Humanitarian & Research Purposes
- **Understanding Impact:** Documenting the scale of threat on civilian population
- **Psychological Research:** Understanding sustained exposure to threat
- **Historical Record:** Documenting conflict patterns for future research

## The Data Sources

We analyzed **418,838 official air raid alert records** from two sources:

1. **GitHub Vadimkin** (273,274 records)
   - Official air raid alert data
   - Timestamps with precision to the second
   - Includes start and end times of each alert
   - Period: March 2022 — June 2026

2. **Kaggle dimakyn** (145,564 records)
   - Telegram-parsed alert notifications
   - Community-sourced but validated data
   - Period: February 2022 — September 2024

**Combined Coverage:** March 15, 2022 — June 24, 2026 (4 years 3 months)

## What This Data Tells Us

This dataset is unique because it:
- **Covers 1,563 consecutive days** of conflict
- **Includes all 25 regions** of Ukraine
- **Provides temporal precision** (exact timing of alerts)
- **Spans the full conflict period** from invasion to present

This is not theoretical; this is what Ukrainian civilians experienced: 152 air raid alerts *per day on average*, with some days exceeding 1,000 alerts.

## Research Methodology

This is a **descriptive statistical analysis** of historical data:
- ✅ We analyze *what happened*
- ❌ We do NOT predict *what will happen*
- ✅ We identify *patterns and trends*
- ✅ We understand *geographic distribution*
- ✅ We track *temporal evolution*

The analysis uses standard time-series techniques:
- Daily aggregation and smoothing
- Year-over-year comparison
- Regional breakdown and stratification
- Trend analysis and seasonality detection

## What We Did NOT Analyze

To keep the scope manageable:
- **Not analyzed:** Causes of alerts (missile, drone, aviation)
- **Not analyzed:** Actual damage or casualties
- **Not analyzed:** Economic impact or cost
- **Not analyzed:** Forecasting future threats

These important topics are for future research.

## Expected Findings

Based on public knowledge of the conflict:

We expect to find:
1. **Escalation over time** — conflict intensity increasing
2. **Regional concentration** — eastern regions more threatened
3. **Temporal patterns** — certain times/seasons more dangerous
4. **Duration variation** — different regions, different alert lengths

Our analysis will quantify these expectations with data.

## Impact of This Research

By understanding the *pattern* of threats, we help:
- **Ukraine:** Evidence for defense planning and resource allocation
- **International Community:** Understanding civilian impact of conflict
- **Researchers:** Data for studying conflict dynamics and civilian impact
- **Documentation:** Historical record for future analysis

---

**Next:** [Data Overview](02-DATA_OVERVIEW.md) — How the data was collected and prepared
