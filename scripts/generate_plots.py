"""
Interactive Plotly graph generation for Air Raid Alerts research report.

This module generates 3 interactive Plotly graphs:
1. Yearly trend: Line chart of alert escalation (2022-2026)
2. Regional heatmap: Intensity of alerts by region
3. Monthly pattern: Seasonal pattern by month
"""

import csv
from pathlib import Path
from typing import Dict, List

import plotly.graph_objects as go
import plotly.express as px


class PlotGenerator:
    """Generate interactive Plotly graphs for research report."""

    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize the PlotGenerator.

        Args:
            data_dir: Path to directory containing processed CSV files.
            output_dir: Path where the HTML plots will be saved.
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.data: Dict[str, List[Dict]] = {}

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_csv(self, filepath: Path) -> List[Dict]:
        """
        Read a CSV file and return list of dictionaries.

        Args:
            filepath: Path to CSV file.

        Returns:
            List of dictionaries with CSV data.
        """
        if not filepath.exists():
            return []

        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return data

    def load_data(self) -> None:
        """Load all required CSV files for graph generation."""
        # Load yearly statistics
        yearly_file = self.data_dir / "07_yearly_statistics.csv"
        if yearly_file.exists():
            self.data["yearly_statistics"] = self._read_csv(yearly_file)

        # Load regional summary
        regional_file = self.data_dir / "02_regional_summary.csv"
        if regional_file.exists():
            self.data["regional_summary"] = self._read_csv(regional_file)

        # Load monthly pattern
        monthly_file = self.data_dir / "08_monthly_pattern.csv"
        if monthly_file.exists():
            self.data["monthly_pattern"] = self._read_csv(monthly_file)

    def generate_yearly_trend(self) -> None:
        """
        Generate yearly trend line chart.

        Creates a line chart showing the number of alerts from 2022-2026
        with markers and red color.
        Output: figures/01_yearly_trend.html
        """
        if "yearly_statistics" not in self.data:
            self.load_data()

        if not self.data.get("yearly_statistics"):
            print("Warning: yearly_statistics data not loaded")
            return

        yearly_data = self.data["yearly_statistics"]

        years = []
        alerts = []

        for row in yearly_data:
            try:
                years.append(int(row.get("year", "")))
                alerts.append(int(row.get("total_alerts", 0)))
            except (ValueError, KeyError):
                continue

        # Sort by year
        sorted_data = sorted(zip(years, alerts), key=lambda x: x[0])
        years, alerts = zip(*sorted_data) if sorted_data else ([], [])

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(years),
            y=list(alerts),
            mode='lines+markers',
            name='Кількість тривог',
            line=dict(color='red', width=3),
            marker=dict(size=10),
            hovertemplate='<b>%{x}</b><br>Тривог: %{y:,}<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': 'Динаміка повітряних тривог 2022-2026',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'darkred'}
            },
            xaxis_title='Рік',
            yaxis_title='Кількість тривог',
            template='plotly_white',
            hovermode='x unified',
            height=500,
            width=900,
            font=dict(size=12),
            margin=dict(l=80, r=80, t=100, b=80)
        )

        output_file = self.output_dir / "01_yearly_trend.html"
        fig.write_html(str(output_file))
        print(f"[OK] Графік тренду збережено: {output_file}")

    def generate_regional_heatmap(self) -> None:
        """
        Generate regional heatmap of alert intensity.

        Creates a heatmap showing alert counts for top regions
        with red color scale.
        Output: figures/02_regional_heatmap.html
        """
        if "regional_summary" not in self.data:
            self.load_data()

        if not self.data.get("regional_summary"):
            print("Warning: regional_summary data not loaded")
            return

        regional_data = self.data["regional_summary"]

        # Get top 15 regions by alert count
        regions = []
        alert_counts = []

        for row in regional_data:
            try:
                region = row.get("oblast", "")
                count = int(row.get("total_alerts", 0))
                regions.append(region)
                alert_counts.append(count)
            except (ValueError, KeyError):
                continue

        # Sort by alert count descending
        sorted_data = sorted(zip(regions, alert_counts),
                           key=lambda x: x[1], reverse=True)
        regions, alert_counts = zip(*sorted_data[:15]) if sorted_data else ([], [])

        # Reshape data for heatmap: each region as a row, single value
        heatmap_data = [[count] for count in alert_counts]

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            y=list(regions),
            x=['Кількість тривог'],
            colorscale='Reds',
            hovertemplate='<b>%{y}</b><br>Тривог: %{z:,}<extra></extra>',
            colorbar=dict(title='Кількість<br>тривог')
        ))

        fig.update_layout(
            title={
                'text': 'Інтенсивність тривог по регіонам',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'darkred'}
            },
            xaxis_title='',
            yaxis_title='Область',
            template='plotly_white',
            height=600,
            width=900,
            font=dict(size=11),
            margin=dict(l=200, r=100, t=100, b=80)
        )

        output_file = self.output_dir / "02_regional_heatmap.html"
        fig.write_html(str(output_file))
        print(f"[OK] Тепловиру регіонів збережено: {output_file}")

    def generate_monthly_pattern(self) -> None:
        """
        Generate monthly seasonal pattern bar chart.

        Creates a bar chart showing average daily alerts by month.
        Output: figures/03_monthly_pattern.html
        """
        if "monthly_pattern" not in self.data:
            self.load_data()

        if not self.data.get("monthly_pattern"):
            print("Warning: monthly_pattern data not loaded")
            return

        monthly_data = self.data["monthly_pattern"]

        # Map month numbers to Ukrainian names
        month_names_uk = {
            1: 'Січень',
            2: 'Лютий',
            3: 'Березень',
            4: 'Квітень',
            5: 'Май',
            6: 'Червень',
            7: 'Липень',
            8: 'Серпень',
            9: 'Вересень',
            10: 'Жовтень',
            11: 'Листопад',
            12: 'Грудень'
        }

        months = []
        avg_daily = []

        for row in monthly_data:
            try:
                month_num = int(row.get("month", 0))
                avg_val = float(row.get("avg_daily_alerts", 0))
                if month_num in month_names_uk:
                    months.append((month_num, month_names_uk[month_num]))
                    avg_daily.append(avg_val)
            except (ValueError, KeyError):
                continue

        # Sort by month number
        sorted_data = sorted(zip(months, avg_daily), key=lambda x: x[0][0])
        months, avg_daily = zip(*sorted_data) if sorted_data else ([], [])

        month_names_list = [m[1] for m in months]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=month_names_list,
            y=list(avg_daily),
            marker=dict(color='orange'),
            hovertemplate='<b>%{x}</b><br>Середня кількість тривог: %{y:.1f}<extra></extra>',
            name='Середня кількість'
        ))

        fig.update_layout(
            title={
                'text': 'Сезонність тривог (по місяцях)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'darkorange'}
            },
            xaxis_title='Місяць',
            yaxis_title='Середня кількість тривог на день',
            template='plotly_white',
            hovermode='x unified',
            height=500,
            width=900,
            font=dict(size=12),
            margin=dict(l=80, r=80, t=100, b=80),
            showlegend=False
        )

        output_file = self.output_dir / "03_monthly_pattern.html"
        fig.write_html(str(output_file))
        print(f"[OK] Сезонний графік збережено: {output_file}")

    def generate_all_plots(self) -> None:
        """
        Generate all three plots.

        Calls generate_yearly_trend(), generate_regional_heatmap(),
        and generate_monthly_pattern() in sequence.
        """
        print("\n=== Генерування інтерактивних графіків ===\n")

        self.load_data()

        self.generate_yearly_trend()
        self.generate_regional_heatmap()
        self.generate_monthly_pattern()

        print(f"\n[DONE] Всі графіки збережено в {self.output_dir}/\n")


if __name__ == "__main__":
    # Example usage
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir = Path(__file__).parent.parent / "figures"

    generator = PlotGenerator(str(data_dir), str(output_dir))
    generator.generate_all_plots()
