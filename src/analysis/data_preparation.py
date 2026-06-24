"""
Data Preparation Module
Loads, cleans, and aggregates air raid alert data from multiple sources.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparator:
    """Load and prepare air raid alert data from GitHub and Kaggle sources."""

    def __init__(self, raw_data_dir: str = "data/raw", processed_data_dir: str = "data/processed"):
        self.raw_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_data_dir)
        self.processed_dir.mkdir(exist_ok=True)

        # Regional mapping (normalize oblast names)
        self.oblast_mapping = {
            "Vinnytska oblast": "Вінницька область",
            "Zhytomyrska oblast": "Житомирська область",
            "Zaporizhzhia oblast": "Запорізька область",
            "Ivano-Frankivsk oblast": "Івано-Франківська область",
            "Kyiv City": "Київ",
            "Kyiv oblast": "Київська область",
            "Kirovograd oblast": "Кіровоградська область",
            "Crimea": "Крим",
            "Luhansk oblast": "Луганська область",
            "Lviv oblast": "Львівська область",
            "Mykolaiv oblast": "Миколаївська область",
            "Odesa oblast": "Одеська область",
            "Poltava oblast": "Полтавська область",
            "Rivne oblast": "Рівненська область",
            "Sumy oblast": "Сумська область",
            "Ternopil oblast": "Тернопільська область",
            "Kharkiv oblast": "Харківська область",
            "Kherson oblast": "Херсонська область",
            "Khmelnytsky oblast": "Хмельницька область",
            "Cherkasy oblast": "Черкаська область",
            "Chernihiv oblast": "Чернігівська область",
            "Chernivtsi oblast": "Чернівецька область",
            "Dnipropetrovsk oblast": "Дніпропетровська область",
            "Donetsk oblast": "Донецька область",
        }

    def load_github_data(self) -> pd.DataFrame:
        """Load GitHub official alerts data."""
        logger.info("Loading GitHub data...")
        df = pd.read_csv(self.raw_dir / "github_vadimkin.csv")

        # Normalize oblast names
        df["oblast_normalized"] = df["oblast"].map(self.oblast_mapping).fillna(df["oblast"])

        # Convert timestamps
        df["started_at"] = pd.to_datetime(df["started_at"]).dt.tz_localize(None)
        df["finished_at"] = pd.to_datetime(df["finished_at"]).dt.tz_localize(None)

        # Calculate duration in minutes
        df["duration_minutes"] = (df["finished_at"] - df["started_at"]).dt.total_seconds() / 60

        logger.info(f"  Loaded {len(df)} records from GitHub")
        return df

    def load_kaggle_data(self) -> pd.DataFrame:
        """Load Kaggle Telegram-parsed alerts data."""
        logger.info("Loading Kaggle data...")
        df = pd.read_csv(self.raw_dir / "kaggle_dimakyn.csv", on_bad_lines="skip")

        # Normalize region names (remove "область" suffix if present)
        df["region_normalized"] = (
            df["region"]
            .str.strip()
            .str.replace(" область", "", regex=False)
            .str.replace(" oblast", "", regex=False)
            + " область"
        )

        # Convert date
        df["timestamp"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df["date_only"] = df["timestamp"].dt.date

        logger.info(f"  Loaded {len(df)} records from Kaggle")
        return df

    def normalize_oblast_name(self, name: str) -> str:
        """Normalize oblast name to Ukrainian standard."""
        if pd.isna(name):
            return name

        name = name.strip()
        # Try direct mapping
        if name in self.oblast_mapping:
            return self.oblast_mapping[name]

        # Try to find partial match
        for key, value in self.oblast_mapping.items():
            if key.lower() in name.lower() or name.lower() in key.lower():
                return value

        return name

    def create_daily_aggregates(self, github_df: pd.DataFrame, kaggle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create daily aggregated data.
        Counts alerts per day across all regions.
        """
        logger.info("Creating daily aggregates...")

        # From GitHub: count unique alert events per day
        github_df["date"] = github_df["started_at"].dt.date
        github_daily = github_df.groupby("date").agg(
            alerts_count=("oblast_normalized", "count"),
            avg_duration_minutes=("duration_minutes", "mean"),
            max_duration_minutes=("duration_minutes", "max"),
            min_duration_minutes=("duration_minutes", "min"),
        ).reset_index()
        github_daily["source"] = "GitHub"

        # From Kaggle: count alerts per day (only "alert" status, not "all_clear")
        kaggle_alerts = kaggle_df[kaggle_df["status"] == "alert"].copy()
        kaggle_daily = kaggle_alerts.groupby("date_only").size().reset_index(name="alerts_count")
        kaggle_daily["source"] = "Kaggle"
        kaggle_daily.rename(columns={"date_only": "date"}, inplace=True)

        # Combine both sources
        daily_combined = pd.concat(
            [
                github_daily[["date", "alerts_count", "source"]],
                kaggle_daily[["date", "alerts_count", "source"]],
            ],
            ignore_index=True,
        )

        # Convert date to datetime
        daily_combined["date"] = pd.to_datetime(daily_combined["date"])

        # For days with both sources, average them
        daily_pivot = daily_combined.pivot_table(index="date", columns="source", values="alerts_count", aggfunc="sum")
        daily_pivot["alerts_count_combined"] = daily_pivot[["GitHub", "Kaggle"]].mean(axis=1)
        daily_pivot["date"] = daily_pivot.index
        daily_pivot = daily_pivot.reset_index(drop=True)

        # Sort by date
        daily_pivot = daily_pivot.sort_values("date").reset_index(drop=True)

        logger.info(f"  Created {len(daily_pivot)} daily records")
        return daily_pivot

    def create_regional_aggregates(self, github_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create regional aggregated data.
        Aggregates all alerts by oblast.
        """
        logger.info("Creating regional aggregates...")

        regional = github_df.groupby("oblast_normalized").agg(
            total_alerts=("oblast_normalized", "count"),
            avg_duration_minutes=("duration_minutes", "mean"),
            max_duration_minutes=("duration_minutes", "max"),
            min_duration_minutes=("duration_minutes", "min"),
            first_alert=("started_at", "min"),
            last_alert=("started_at", "max"),
        ).reset_index()

        regional.rename(columns={"oblast_normalized": "oblast"}, inplace=True)
        regional = regional.sort_values("total_alerts", ascending=False).reset_index(drop=True)
        regional["rank"] = range(1, len(regional) + 1)

        logger.info(f"  Created regional data for {len(regional)} oblasts")
        return regional

    def create_regional_daily_aggregates(self, github_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create daily aggregates by region.
        Shows alert counts for each oblast on each day.
        """
        logger.info("Creating regional-daily aggregates...")

        github_df["date"] = github_df["started_at"].dt.date

        regional_daily = (
            github_df.groupby(["date", "oblast_normalized"])
            .agg(
                alerts_count=("oblast_normalized", "count"),
                avg_duration_minutes=("duration_minutes", "mean"),
            )
            .reset_index()
        )

        regional_daily.rename(columns={"oblast_normalized": "oblast"}, inplace=True)
        regional_daily["date"] = pd.to_datetime(regional_daily["date"])
        regional_daily = regional_daily.sort_values(["date", "oblast"]).reset_index(drop=True)

        logger.info(f"  Created {len(regional_daily)} regional-daily records")
        return regional_daily

    def create_yearly_comparison(self, github_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create yearly comparison data.
        Shows total alerts per month for each year.
        """
        logger.info("Creating yearly comparison...")

        github_df["year_month"] = github_df["started_at"].dt.to_period("M")
        github_df["year"] = github_df["started_at"].dt.year
        github_df["month"] = github_df["started_at"].dt.month

        yearly = github_df.groupby(["year", "month"]).size().reset_index(name="alerts_count")

        logger.info(f"  Created yearly comparison data")
        return yearly

    def create_duration_statistics(self, github_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create duration statistics by oblast.
        """
        logger.info("Creating duration statistics...")

        duration_stats = github_df.groupby("oblast_normalized").agg(
            total_alerts=("oblast_normalized", "count"),
            avg_duration_min=("duration_minutes", "mean"),
            median_duration_min=("duration_minutes", "median"),
            max_duration_min=("duration_minutes", "max"),
            min_duration_min=("duration_minutes", "min"),
            std_duration_min=("duration_minutes", "std"),
        ).reset_index()

        duration_stats.rename(columns={"oblast_normalized": "oblast"}, inplace=True)
        duration_stats = duration_stats.sort_values("total_alerts", ascending=False).reset_index(drop=True)

        logger.info(f"  Created duration statistics")
        return duration_stats

    def process_all(self) -> Dict[str, pd.DataFrame]:
        """Run complete data preparation pipeline."""
        logger.info("=" * 60)
        logger.info("STARTING DATA PREPARATION PIPELINE")
        logger.info("=" * 60)

        # Load raw data
        github_df = self.load_github_data()
        kaggle_df = self.load_kaggle_data()

        # Create aggregates
        daily_agg = self.create_daily_aggregates(github_df, kaggle_df)
        regional_agg = self.create_regional_aggregates(github_df)
        regional_daily_agg = self.create_regional_daily_aggregates(github_df)
        yearly_comparison = self.create_yearly_comparison(github_df)
        duration_stats = self.create_duration_statistics(github_df)

        # Save to CSV
        logger.info("=" * 60)
        logger.info("SAVING TO CSV FILES")
        logger.info("=" * 60)

        daily_agg.to_csv(self.processed_dir / "01_daily_aggregates.csv", index=False)
        logger.info(f"  ✓ Saved: 01_daily_aggregates.csv ({len(daily_agg)} rows)")

        regional_agg.to_csv(self.processed_dir / "02_regional_summary.csv", index=False)
        logger.info(f"  ✓ Saved: 02_regional_summary.csv ({len(regional_agg)} rows)")

        regional_daily_agg.to_csv(self.processed_dir / "03_regional_daily.csv", index=False)
        logger.info(f"  ✓ Saved: 03_regional_daily.csv ({len(regional_daily_agg)} rows)")

        yearly_comparison.to_csv(self.processed_dir / "04_yearly_comparison.csv", index=False)
        logger.info(f"  ✓ Saved: 04_yearly_comparison.csv ({len(yearly_comparison)} rows)")

        duration_stats.to_csv(self.processed_dir / "05_duration_statistics.csv", index=False)
        logger.info(f"  ✓ Saved: 05_duration_statistics.csv ({len(duration_stats)} rows)")

        logger.info("=" * 60)
        logger.info("DATA PREPARATION COMPLETE")
        logger.info("=" * 60)

        return {
            "daily_aggregates": daily_agg,
            "regional_summary": regional_agg,
            "regional_daily": regional_daily_agg,
            "yearly_comparison": yearly_comparison,
            "duration_statistics": duration_stats,
        }


if __name__ == "__main__":
    preparator = DataPreparator()
    data = preparator.process_all()
