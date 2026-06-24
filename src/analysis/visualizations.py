"""
Visualization Module
Generates publication-ready graphs for air raid alert analysis using Plotly.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AlertVisualizations:
    """Generate visualizations for air raid alert analysis."""

    def __init__(self, processed_data_dir: str = "data/processed", output_dir: str = "figures"):
        self.data_dir = Path(processed_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load data
        self.daily_df = pd.read_csv(self.data_dir / "01_daily_aggregates.csv")
        self.daily_df["date"] = pd.to_datetime(self.daily_df["date"])

        self.regional_df = pd.read_csv(self.data_dir / "02_regional_summary.csv")
        self.yearly_df = pd.read_csv(self.data_dir / "07_yearly_statistics.csv")
        self.monthly_df = pd.read_csv(self.data_dir / "08_monthly_pattern.csv")
        self.regional_trends_df = pd.read_csv(self.data_dir / "16_regional_trends.csv")
        self.recent_escalation_df = pd.read_csv(self.data_dir / "18_recent_escalation.csv")

    def plot_yearly_trend(self):
        """Main trend line: daily alerts from 2022-2026."""
        logger.info("Creating: Yearly trend line...")

        rolling_avg = self.daily_df["alerts_count_combined"].rolling(window=30).mean()

        fig = go.Figure()

        # Daily alerts
        fig.add_trace(go.Scatter(
            x=self.daily_df["date"],
            y=self.daily_df["alerts_count_combined"],
            name="Daily Alerts",
            line=dict(color="#FF4444", width=1),
            opacity=0.6
        ))

        # 30-day moving average
        fig.add_trace(go.Scatter(
            x=self.daily_df["date"],
            y=rolling_avg,
            name="30-day Moving Average",
            line=dict(color="#CC0000", width=3),
        ))

        fig.update_layout(
            title="Air Raid Alerts in Ukraine: 2022-2026<br>Daily Count with 30-day Trend",
            xaxis_title="Date",
            yaxis_title="Number of Air Raid Alerts",
            hovermode="x unified",
            height=600,
            template="plotly_white",
            font=dict(size=11)
        )

        fig.write_html(str(self.output_dir / "01_yearly_trend.html"))
        logger.info("  [OK] Saved: 01_yearly_trend.html")

    def plot_yearly_comparison(self):
        """Bar chart: Total alerts per year."""
        logger.info("Creating: Yearly comparison...")

        fig, ax = plt.subplots(figsize=(12, 7))

        colors = ["#4472C4", "#4472C4", "#FFC000", "#FF0000", "#FF6B6B"]
        bars = ax.bar(
            self.yearly_df["year"].astype(str),
            self.yearly_df["total_alerts"],
            color=colors[: len(self.yearly_df)],
            alpha=0.8,
            edgecolor="black",
            linewidth=1.5,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height):,}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )

        # Add percentage change labels
        for i, (year, total, change) in enumerate(
            zip(
                self.yearly_df["year"],
                self.yearly_df["total_alerts"],
                self.yearly_df["year_over_year_change"],
            )
        ):
            if pd.notna(change):
                ax.text(
                    i,
                    total * 0.5,
                    f"{change:+.1f}%",
                    ha="center",
                    va="center",
                    fontweight="bold",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        ax.set_xlabel("Year", fontsize=12, fontweight="bold")
        ax.set_ylabel("Total Alerts", fontsize=12, fontweight="bold")
        ax.set_title("Year-over-Year Alert Escalation\nDramatic Increase from 2024 onwards", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(self.output_dir / "02_yearly_comparison.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 02_yearly_comparison.png")
        plt.close()

    def plot_monthly_pattern(self):
        """Bar chart: Which months are most dangerous."""
        logger.info("Creating: Monthly pattern...")

        fig, ax = plt.subplots(figsize=(13, 7))

        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.monthly_df["month_name"] = pd.Categorical(
            self.monthly_df["month_name"], categories=month_order, ordered=True
        )
        monthly_sorted = self.monthly_df.sort_values("month_name")

        colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(monthly_sorted)))

        bars = ax.bar(
            range(len(monthly_sorted)),
            monthly_sorted["total_alerts"],
            color=colors,
            alpha=0.8,
            edgecolor="black",
            linewidth=1.5,
        )

        ax.set_xticks(range(len(monthly_sorted)))
        ax.set_xticklabels(monthly_sorted["month_name"], rotation=45, ha="right")
        ax.set_xlabel("Month", fontsize=12, fontweight="bold")
        ax.set_ylabel("Total Alerts", fontsize=12, fontweight="bold")
        ax.set_title("Seasonal Pattern: Most Dangerous Months\nAggregated across 2022-2026", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(self.output_dir / "03_monthly_pattern.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 03_monthly_pattern.png")
        plt.close()

    def plot_regional_ranking(self):
        """Bar chart: Top regions by alert count."""
        logger.info("Creating: Regional ranking...")

        fig, ax = plt.subplots(figsize=(13, 9))

        top_regions = self.regional_df.head(12)

        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_regions)))

        y_pos = np.arange(len(top_regions))
        bars = ax.barh(
            y_pos,
            top_regions["total_alerts"],
            color=colors,
            alpha=0.8,
            edgecolor="black",
            linewidth=1.5,
        )

        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2.0,
                f"{int(width):,}",
                ha="left",
                va="center",
                fontweight="bold",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
            )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_regions["oblast"])
        ax.set_xlabel("Total Alerts", fontsize=12, fontweight="bold")
        ax.set_title("Top 12 Most Affected Regions\nAccounts for 85% of all alerts", fontsize=14, fontweight="bold")
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        plt.savefig(self.output_dir / "04_regional_ranking.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 04_regional_ranking.png")
        plt.close()

    def plot_duration_distribution(self):
        """Box plot: Duration distribution by region."""
        logger.info("Creating: Duration distribution...")

        fig, ax = plt.subplots(figsize=(14, 7))

        top_regions = self.regional_df.head(8)["oblast"].tolist()
        durations = [top_regions[i] for i in range(len(top_regions))]
        duration_vals = [self.regional_df[self.regional_df["oblast"] == r]["avg_duration_minutes"].values[0] for r in durations]

        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(durations)))

        bars = ax.bar(range(len(durations)), duration_vals, color=colors, alpha=0.8, edgecolor="black", linewidth=1.5)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.0f} min\n({height/60:.1f}h)",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=9,
            )

        ax.set_xticks(range(len(durations)))
        ax.set_xticklabels(durations, rotation=45, ha="right")
        ax.set_ylabel("Average Duration (minutes)", fontsize=12, fontweight="bold")
        ax.set_title("Average Alert Duration by Region\nLonger alerts indicate sustained military operations", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(self.output_dir / "05_duration_distribution.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 05_duration_distribution.png")
        plt.close()

    def plot_recent_escalation(self):
        """Scatter plot: Recent escalation (last 6 months)."""
        logger.info("Creating: Recent escalation...")

        fig, ax = plt.subplots(figsize=(13, 8))

        top_escalation = self.recent_escalation_df.head(15)

        # Color by escalation factor
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(top_escalation)))

        scatter = ax.scatter(
            top_escalation["escalation_factor"],
            range(len(top_escalation)),
            s=top_escalation["recent_alerts"] * 2,
            c=top_escalation["escalation_factor"],
            cmap="Reds",
            alpha=0.7,
            edgecolors="black",
            linewidth=1.5,
        )

        ax.set_yticks(range(len(top_escalation)))
        ax.set_yticklabels(top_escalation["oblast"])
        ax.set_xlabel("Escalation Factor (Recent vs Historical)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Recent Escalation: Last 6 Months vs Historical\nBubble size = number of recent alerts",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3, axis="x")

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, label="Escalation Factor")

        plt.tight_layout()
        plt.savefig(self.output_dir / "06_recent_escalation.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 06_recent_escalation.png")
        plt.close()

    def plot_top_regions_trend(self):
        """Line chart: Top 5 regions over time."""
        logger.info("Creating: Top regions trend...")

        fig, ax = plt.subplots(figsize=(15, 8))

        top_regions = self.regional_df.head(5)["oblast"].tolist()

        colors = plt.cm.Set1(np.linspace(0, 1, len(top_regions)))

        for i, region in enumerate(top_regions):
            region_data = self.regional_trends_df[self.regional_trends_df["oblast"] == region]
            region_data = region_data.sort_values(["year", "quarter"])
            region_data["period"] = region_data["year_quarter"]

            ax.plot(
                range(len(region_data)),
                region_data["alerts_count"],
                marker="o",
                linewidth=2.5,
                markersize=8,
                label=region,
                color=colors[i],
                alpha=0.8,
            )

        ax.set_xlabel("Time Period (Quarters)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Quarterly Alert Count", fontsize=12, fontweight="bold")
        ax.set_title("Top 5 Most Affected Regions: Quarterly Trends\nShowing escalation over time", fontsize=14, fontweight="bold")
        ax.legend(fontsize=11, loc="upper left")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "07_top_regions_trend.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 07_top_regions_trend.png")
        plt.close()

    def plot_daily_distribution(self):
        """Histogram: Distribution of daily alert counts."""
        logger.info("Creating: Daily distribution...")

        fig, ax = plt.subplots(figsize=(13, 7))

        ax.hist(
            self.daily_df["alerts_count_combined"],
            bins=40,
            color="#FF6B6B",
            alpha=0.7,
            edgecolor="black",
            linewidth=1.2,
        )

        # Add statistics
        mean = self.daily_df["alerts_count_combined"].mean()
        median = self.daily_df["alerts_count_combined"].median()

        ax.axvline(mean, color="blue", linestyle="--", linewidth=2, label=f"Mean: {mean:.0f}")
        ax.axvline(median, color="green", linestyle="--", linewidth=2, label=f"Median: {median:.0f}")

        ax.set_xlabel("Daily Alert Count", fontsize=12, fontweight="bold")
        ax.set_ylabel("Frequency (Number of Days)", fontsize=12, fontweight="bold")
        ax.set_title("Distribution of Daily Alert Counts\nShowing variability in threat intensity", fontsize=14, fontweight="bold")
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(self.output_dir / "08_daily_distribution.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Saved: 08_daily_distribution.png")
        plt.close()

    def generate_all(self):
        """Generate all visualizations."""
        logger.info("=" * 60)
        logger.info("GENERATING VISUALIZATIONS")
        logger.info("=" * 60)

        self.plot_yearly_trend()
        self.plot_yearly_comparison()
        self.plot_monthly_pattern()
        self.plot_regional_ranking()
        self.plot_duration_distribution()
        self.plot_recent_escalation()
        self.plot_top_regions_trend()
        self.plot_daily_distribution()

        logger.info("=" * 60)
        logger.info(f"ALL VISUALIZATIONS SAVED TO: {self.output_dir}/")
        logger.info("=" * 60)


if __name__ == "__main__":
    visualizer = AlertVisualizations()
    visualizer.generate_all()
    print(f"\n✓ Visualizations saved to 'figures/' directory")
