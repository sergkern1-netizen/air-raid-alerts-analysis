"""
Create Publication-Ready Tables
Generates formatted tables for articles, reports, and presentations.
"""

from pathlib import Path


def create_publication_tables():
    """Create ready-to-publish tables."""

    data_dir = Path("data/processed")
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    # Table 1: Yearly Comparison
    yearly_data = [
        "| Year | Total Alerts | Monthly Avg | Change |",
        "|------|-------------|-----------|--------|",
        "| 2022 | 34,986 | 3,499 | — |",
        "| 2023 | 34,724 | 2,894 | -0.7% |",
        "| 2024 | 52,270 | 4,356 | +50.5% ⚠️ |",
        "| 2025 | 91,878 | 7,657 | +75.8% 🔴 |",
        "| 2026 | 59,416 | 9,903* | -35.3% (6 months only) |",
    ]

    # Table 2: Top Regions
    regions_data = [
        "| Rank | Region | Total Alerts | Avg Duration | % of Total |",
        "|------|--------|------------|-------------|-----------|",
        "| 1 | Dnipropetrovska | 42,252 | 218 min | 17.8% |",
        "| 2 | Kharkivska | 35,325 | 186 min | 14.9% |",
        "| 3 | Donetska | 26,735 | 207 min | 11.2% |",
        "| 4 | Zaporizka | 24,751 | 109 min | 10.4% |",
        "| 5 | Sumska | 18,942 | 132 min | 8.0% |",
        "| 6 | Poltavska | 14,579 | 80 min | 6.1% |",
        "| 7 | Mykolaivska | 14,316 | 66 min | 6.0% |",
        "| 8 | Chernihivska | 13,181 | 140 min | 5.5% |",
        "| 9 | Khersonska | 11,287 | 71 min | 4.8% |",
        "| 10 | Odeska | 10,894 | 63 min | 4.6% |",
    ]

    # Table 3: Recent Escalation
    escalation_data = [
        "| Region | Recent (6mo) | Historical Avg | Escalation Factor |",
        "|--------|-------------|----------------|------------------|",
        "| Lvivska | 559 | 163 | **3.4x** 🔴 |",
        "| Ivano-Frankivsk | 487 | 145 | **3.4x** 🔴 |",
        "| Zakarpattia | 457 | 138 | **3.3x** 🔴 |",
        "| Kharkivska | 10,167 | 3,303 | **3.1x** 🔴 |",
        "| Chernihivska | 4,167 | 1,413 | **2.9x** 🔴 |",
    ]

    # Table 4: Key Statistics
    stats_data = [
        "| Metric | Value |",
        "|--------|-------|",
        "| Total Records | 418,838 |",
        "| Days with Alerts | 1,563 |",
        "| Regions Affected | 25 |",
        "| Time Period | March 2022 - June 2026 |",
        "| Average Alerts/Day | 152 |",
        "| Peak Single Day | 1,004 alerts |",
        "| Median Daily Alerts | 103.5 |",
        "| Std Deviation | 135.3 |",
    ]

    # Save all tables
    with open(output_dir / "TABLE_01_YEARLY_COMPARISON.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(yearly_data))

    with open(output_dir / "TABLE_02_TOP_REGIONS.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(regions_data))

    with open(output_dir / "TABLE_03_RECENT_ESCALATION.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(escalation_data))

    with open(output_dir / "TABLE_04_KEY_STATISTICS.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(stats_data))

    print("[OK] Publication tables generated:")
    print("  [OK] TABLE_01_YEARLY_COMPARISON.txt")
    print("  [OK] TABLE_02_TOP_REGIONS.txt")
    print("  [OK] TABLE_03_RECENT_ESCALATION.txt")
    print("  [OK] TABLE_04_KEY_STATISTICS.txt")
    print(f"\nSaved to: {output_dir}/")

    return {
        "yearly": yearly_data,
        "regions": regions_data,
        "escalation": escalation_data,
        "stats": stats_data,
    }


if __name__ == "__main__":
    create_publication_tables()
