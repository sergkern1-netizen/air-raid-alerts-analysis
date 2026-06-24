# src/loader.py
import pandas as pd
from pathlib import Path
from typing import Dict

class DataLoader:
    """Load air raid alerts from 2 sources"""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)

    def load_github(self) -> pd.DataFrame:
        """Load GitHub Vadimkin dataset"""
        df = pd.read_csv(self.data_dir / "github_vadimkin.csv")
        df['timestamp'] = pd.to_datetime(df['started_at'])
        df['source'] = 'github'
        return df.sort_values('timestamp')

    def load_kaggle(self) -> pd.DataFrame:
        """Load Kaggle dimakyn dataset"""
        df = pd.read_csv(self.data_dir / "kaggle_dimakyn.csv", on_bad_lines='skip')
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif 'date' in df.columns:
            # 'date' column in Kaggle already contains full datetime
            df['timestamp'] = pd.to_datetime(df['date'])
        df['source'] = 'kaggle'
        return df.sort_values('timestamp')

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all 2 sources"""
        return {
            'github': self.load_github(),
            'kaggle': self.load_kaggle(),
        }
