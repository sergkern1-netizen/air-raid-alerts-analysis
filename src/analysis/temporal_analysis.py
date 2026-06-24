"""
Temporal Analysis Module
Analyzes trends, seasonality, and year-over-year patterns in alert data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TemporalAnalyzer:
    """Analyze temporal patterns in air raid alert data."""

    def __init__(self, processed_data_dir: str = "data/processed"):
        self.data_dir = Path(processed_data_dir)
        self.daily_df = pd.read_csv(self.data_dir / "01_daily_aggregates.csv")
        self.daily_df["date"] = pd.to_datetime(self.daily_df["date"])
        self.yearly_df = pd.read_csv(self.data_dir / "04_yearly_comparison.csv")

    def get_overall_statistics(self) -> dict:
        """Calculate overall statistics."""
        return {
            "total_days": len(self.daily_df),
            "total_alerts": self.daily_df["alerts_count_combined"].sum(),
            "avg_daily_alerts": self.daily_df["alerts_count_combined"].mean(),
            "median_daily_alerts": self.daily_df["alerts_count_combined"].median(),
            "max_daily_alerts": self.daily_df["alerts_count_combined"].max(),
            "min_daily_alerts": self.daily_df["alerts_count_combined"].min(),
            "std_daily_alerts": self.daily_df["alerts_count_combined"].std(),
            "date_range": f"{self.daily_df['date'].min().date()} to {self.daily_df['date'].max().date()}",
        }

    def get_yearly_statistics(self) -> pd.DataFrame:
        """Calculate yearly statistics."""
        monthly_totals = self.yearly_df.groupby("year").agg(
            total_alerts=("alerts_count", "sum"),
            avg_monthly_alerts=("alerts_count", "mean"),
            max_monthly_alerts=("alerts_count", "max"),
            min_monthly_alerts=("alerts_count", "min"),
            months_with_data=("alerts_count", "count"),
        ).reset_index()

        monthly_totals = monthly_totals.sort_values("year")
        monthly_totals["year_over_year_change"] = monthly_totals["total_alerts"].pct_change() * 100

        return monthly_totals

    def get_monthly_pattern(self) -> pd.DataFrame:
        """Analyze monthly patterns (which months are most dangerous)."""
        self.daily_df["month"] = self.daily_df["date"].dt.month
        self.daily_df["year"] = self.daily_df["date"].dt.year

        monthly = self.daily_df.groupby("month").agg(
            total_alerts=("alerts_count_combined", "sum"),
            avg_daily_alerts=("alerts_count_combined", "mean"),
            max_daily_alerts=("alerts_count_combined", "max"),
            num_days=("alerts_count_combined", "count"),
        ).reset_index()

        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        monthly["month_name"] = monthly["month"].map(month_names)
        monthly = monthly.sort_values("total_alerts", ascending=False)

        return monthly

    def get_quarterly_pattern(self) -> pd.DataFrame:
        """Analyze quarterly patterns."""
        self.daily_df["quarter"] = self.daily_df["date"].dt.quarter
        self.daily_df["year"] = self.daily_df["date"].dt.year

        quarterly = self.daily_df.groupby(["year", "quarter"]).agg(
            total_alerts=("alerts_count_combined", "sum"),
            avg_daily_alerts=("alerts_count_combined", "mean"),
        ).reset_index()

        quarterly["year_quarter"] = quarterly["year"].astype(str) + "-Q" + quarterly["quarter"].astype(str)

        return quarterly

    def get_month_year_matrix(self) -> pd.DataFrame:
        """Create matrix of year x month."""
        self.daily_df["month"] = self.daily_df["date"].dt.month
        self.daily_df["year"] = self.daily_df["date"].dt.year

        monthly_data = self.daily_df.groupby(["year", "month"])["alerts_count_combined"].sum().reset_index()

        pivot = monthly_data.pivot(index="month", columns="year", values="alerts_count_combined")

        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        pivot["month_name"] = pivot.index.map(month_names)
        pivot = pivot.reset_index(drop=True)

        return pivot

    def get_peak_periods(self) -> pd.DataFrame:
        """Identify peak periods (worst weeks/months)."""
        self.daily_df["week"] = self.daily_df["date"].dt.isocalendar().week
        self.daily_df["year"] = self.daily_df["date"].dt.year

        weekly = self.daily_df.groupby(["year", "week"]).agg(
            total_alerts=("alerts_count_combined", "sum"),
            avg_daily=("alerts_count_combined", "mean"),
            max_daily=("alerts_count_combined", "max"),
        ).reset_index()

        weekly = weekly.nlargest(20, "total_alerts")  # Top 20 worst weeks

        return weekly

    def get_trend_analysis(self) -> dict:
        """Simple trend analysis (increasing/decreasing)."""
        # Split into quarters
        q1 = self.daily_df[self.daily_df["date"] < "2024-03-01"]["alerts_count_combined"].mean()
        q2 = self.daily_df[(self.daily_df["date"] >= "2024-03-01") & (self.daily_df["date"] < "2025-03-01")][
            "alerts_count_combined"
        ].mean()
        q3 = self.daily_df[self.daily_df["date"] >= "2025-03-01"]["alerts_count_combined"].mean()

        return {
            "early_period_avg": round(q1, 1),
            "mid_period_avg": round(q2, 1),
            "recent_period_avg": round(q3, 1),
            "trend": "Increasing" if q3 > q2 > q1 else "Decreasing" if q3 < q2 < q1 else "Fluctuating",
        }

    def save_analysis(self):
        """Save all temporal analysis results."""
        output_dir = Path("data/processed")

        # Overall stats
        stats = self.get_overall_statistics()
        with open(output_dir / "06_overall_statistics.txt", "w") as f:
            f.write("OVERALL STATISTICS\n")
            f.write("=" * 50 + "\n\n")
            for key, value in stats.items():
                f.write(f"{key:.<35} {value}\n")

        # Yearly stats
        yearly_stats = self.get_yearly_statistics()
        yearly_stats.to_csv(output_dir / "07_yearly_statistics.csv", index=False)

        # Monthly pattern
        monthly = self.get_monthly_pattern()
        monthly.to_csv(output_dir / "08_monthly_pattern.csv", index=False)

        # Month-year matrix
        matrix = self.get_month_year_matrix()
        matrix.to_csv(output_dir / "09_month_year_matrix.csv", index=False)

        # Quarterly pattern
        quarterly = self.get_quarterly_pattern()
        quarterly.to_csv(output_dir / "10_quarterly_pattern.csv", index=False)

        # Peak periods
        peaks = self.get_peak_periods()
        peaks.to_csv(output_dir / "11_peak_weeks.csv", index=False)

        # Trend analysis
        trend = self.get_trend_analysis()
        with open(output_dir / "12_trend_analysis.txt", "w") as f:
            f.write("TREND ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            for key, value in trend.items():
                f.write(f"{key:.<35} {value}\n")

        logger.info("✓ Temporal analysis saved")

        return {
            "overall_stats": stats,
            "yearly_stats": yearly_stats,
            "monthly_pattern": monthly,
            "monthly_matrix": matrix,
            "quarterly_pattern": quarterly,
            "peak_periods": peaks,
            "trend_analysis": trend,
        }


if __name__ == "__main__":
    analyzer = TemporalAnalyzer()
    results = analyzer.save_analysis()

    print("\n" + "=" * 60)
    print("TEMPORAL ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nOVERALL STATISTICS:")
    for key, val in results["overall_stats"].items():
        print(f"  {key}: {val}")

    print("\nYEARLY COMPARISON:")
    print(results["yearly_stats"].to_string())
