# src/validator.py
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class DataValidator:
    """Cross-validate data between sources"""

    def __init__(self, sources: Dict[str, pd.DataFrame]):
        self.sources = sources

    def find_common_period(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """Find date range common to all sources"""
        min_dates = {}
        max_dates = {}

        for name, df in self.sources.items():
            ts_min = df['timestamp'].min()
            ts_max = df['timestamp'].max()
            # Normalize to naive timestamps for comparison
            if ts_min.tzinfo is not None:
                ts_min = ts_min.tz_localize(None)
            if ts_max.tzinfo is not None:
                ts_max = ts_max.tz_localize(None)
            min_dates[name] = ts_min
            max_dates[name] = ts_max

        start = max(min_dates.values())
        end = min(max_dates.values())

        return start, end

    def daily_comparison(self) -> pd.DataFrame:
        """Compare daily alert counts between sources"""
        comparison = {}

        for name, df in self.sources.items():
            daily = df.groupby(df['timestamp'].dt.date).size()
            comparison[name] = daily

        return pd.DataFrame(comparison).fillna(0).astype(int)

    def correlation_matrix(self) -> pd.DataFrame:
        """Calculate correlation between sources"""
        daily = self.daily_comparison()
        return daily.corr()

    def detect_anomalies(self) -> Dict[str, dict]:
        """Find data anomalies in each source"""
        anomalies = {}

        for name, df in self.sources.items():
            dupes = df['timestamp'].duplicated().sum()
            missing = df.isnull().sum().sum()

            anomalies[name] = {
                'duplicates': dupes,
                'missing_values': missing,
            }

        return anomalies

    def combine_sources(self) -> pd.DataFrame:
        """Combine all sources into single validated dataset"""
        dfs = []

        for name, df in self.sources.items():
            cols_to_keep = ['timestamp']
            if 'oblast' in df.columns:
                cols_to_keep.append('oblast')
            if 'region' in df.columns:
                cols_to_keep.append('region')

            subset = df[cols_to_keep + ['source']].copy()
            # Normalize timestamp to naive for comparison
            if subset['timestamp'].dt.tz is not None:
                subset['timestamp'] = subset['timestamp'].dt.tz_localize(None)
            dfs.append(subset)

        combined = pd.concat(dfs, ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp'])

        return combined.sort_values('timestamp')
