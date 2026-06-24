"""
Regional Analysis Module
Analyzes alert patterns by region/oblast.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RegionalAnalyzer:
    """Analyze regional patterns in air raid alert data."""

    def __init__(self, processed_data_dir: str = "data/processed"):
        self.data_dir = Path(processed_data_dir)
        self.regional_df = pd.read_csv(self.data_dir / "02_regional_summary.csv")
        self.regional_daily_df = pd.read_csv(self.data_dir / "03_regional_daily.csv")
        self.regional_daily_df["date"] = pd.to_datetime(self.regional_daily_df["date"])

    def get_regional_ranking(self, top_n: int = 10) -> pd.DataFrame:
        """Get top regions by alert count."""
        return self.regional_df.head(top_n)[
            ["rank", "oblast", "total_alerts", "avg_duration_minutes", "first_alert", "last_alert"]
        ].copy()

    def get_regional_statistics(self) -> dict:
        """Overall regional statistics."""
        return {
            "total_oblasts": len(self.regional_df),
            "alerts_per_oblast_avg": self.regional_df["total_alerts"].mean(),
            "alerts_per_oblast_median": self.regional_df["total_alerts"].median(),
            "most_affected": self.regional_df.iloc[0]["oblast"],
            "most_affected_alerts": int(self.regional_df.iloc[0]["total_alerts"]),
            "least_affected": self.regional_df.iloc[-1]["oblast"],
            "least_affected_alerts": int(self.regional_df.iloc[-1]["total_alerts"]),
        }

    def get_duration_by_region(self, top_n: int = 10) -> pd.DataFrame:
        """Get average alert duration by region."""
        regional_sorted = self.regional_df.sort_values("avg_duration_minutes", ascending=False).head(top_n)
        return regional_sorted[["oblast", "total_alerts", "avg_duration_minutes", "max_duration_minutes"]].copy()

    def get_regional_trends(self) -> pd.DataFrame:
        """Get regional trends over time (alerts per quarter for top regions)."""
        top_oblasts = self.regional_df.head(5)["oblast"].tolist()

        self.regional_daily_df["year"] = self.regional_daily_df["date"].dt.year
        self.regional_daily_df["quarter"] = self.regional_daily_df["date"].dt.quarter

        trends = self.regional_daily_df[self.regional_daily_df["oblast"].isin(top_oblasts)].groupby(
            ["oblast", "year", "quarter"]
        )["alerts_count"].sum().reset_index()

        trends["year_quarter"] = trends["year"].astype(str) + "-Q" + trends["quarter"].astype(str)

        return trends.sort_values(["oblast", "year", "quarter"])

    def get_emergency_regions(self, threshold_percentile: float = 75) -> pd.DataFrame:
        """Identify regions with highest alert intensity."""
        threshold = self.regional_df["total_alerts"].quantile(threshold_percentile / 100)
        high_alert = self.regional_df[self.regional_df["total_alerts"] >= threshold].copy()
        return high_alert[["rank", "oblast", "total_alerts", "avg_duration_minutes"]].copy()

    def get_recently_affected_regions(self) -> pd.DataFrame:
        """Regions that recently (last 6 months) experienced escalation."""
        recent_date = self.regional_daily_df["date"].max() - pd.Timedelta(days=180)

        recent = self.regional_daily_df[self.regional_daily_df["date"] >= recent_date].groupby("oblast").agg(
            recent_alerts=("alerts_count", "sum"),
            recent_avg_daily=("alerts_count", "mean"),
            days_with_alerts=("alerts_count", "count"),
        ).reset_index()

        recent = recent.sort_values("recent_alerts", ascending=False)

        # Add historical average
        historical = (
            self.regional_daily_df[self.regional_daily_df["date"] < recent_date]
            .groupby("oblast")["alerts_count"]
            .mean()
            .reset_index(name="historical_avg")
        )

        merged = recent.merge(historical, on="oblast", how="left")
        merged["escalation_factor"] = merged["recent_avg_daily"] / merged["historical_avg"]

        return merged.sort_values("escalation_factor", ascending=False)

    def get_regional_coverage(self) -> pd.DataFrame:
        """Which regions have continuous coverage vs sporadic."""
        coverage = self.regional_daily_df.groupby("oblast").agg(
            total_alerts=("alerts_count", "sum"),
            avg_daily=("alerts_count", "mean"),
            max_daily=("alerts_count", "max"),
            days_with_alerts=("alerts_count", "count"),
            date_range_days=(
                "date",
                lambda x: (x.max() - x.min()).days,
            ),
        ).reset_index()

        coverage["coverage_percentage"] = (coverage["days_with_alerts"] / coverage["date_range_days"] * 100).round(1)

        return coverage.sort_values("coverage_percentage", ascending=False)

    def save_analysis(self):
        """Save all regional analysis results."""
        output_dir = Path("data/processed")

        # Regional ranking
        ranking = self.get_regional_ranking(top_n=25)
        ranking.to_csv(output_dir / "13_regional_ranking.csv", index=False)

        # Regional statistics
        stats = self.get_regional_statistics()
        with open(output_dir / "14_regional_statistics.txt", "w") as f:
            f.write("REGIONAL STATISTICS\n")
            f.write("=" * 50 + "\n\n")
            for key, value in stats.items():
                f.write(f"{key:.<35} {value}\n")

        # Duration by region
        duration = self.get_duration_by_region(top_n=10)
        duration.to_csv(output_dir / "15_duration_by_region.csv", index=False)

        # Regional trends
        trends = self.get_regional_trends()
        trends.to_csv(output_dir / "16_regional_trends.csv", index=False)

        # Emergency regions
        emergency = self.get_emergency_regions(threshold_percentile=75)
        emergency.to_csv(output_dir / "17_high_alert_regions.csv", index=False)

        # Recently affected
        recent = self.get_recently_affected_regions()
        recent.to_csv(output_dir / "18_recent_escalation.csv", index=False)

        # Coverage
        coverage = self.get_regional_coverage()
        coverage.to_csv(output_dir / "19_regional_coverage.csv", index=False)

        logger.info("✓ Regional analysis saved")

        return {
            "ranking": ranking,
            "statistics": stats,
            "duration": duration,
            "trends": trends,
            "emergency_regions": emergency,
            "recent_escalation": recent,
            "coverage": coverage,
        }


if __name__ == "__main__":
    analyzer = RegionalAnalyzer()
    results = analyzer.save_analysis()

    print("\n" + "=" * 60)
    print("REGIONAL ANALYSIS COMPLETE")
    print("=" * 60)

    print("\nREGIONAL STATISTICS:")
    for key, val in results["statistics"].items():
        print(f"  {key}: {val}")

    print("\nTOP 10 REGIONS BY ALERTS:")
    print(results["ranking"].to_string(index=False))

    print("\nRECENT ESCALATION (Last 6 months):")
    print(results["recent_escalation"].head(10).to_string(index=False))
