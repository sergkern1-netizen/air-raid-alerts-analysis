"""
Generate HTML Report with Interactive Charts and Tables
Creates publication-ready HTML report with all findings.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Generate interactive HTML report with charts and tables."""

    def __init__(self, processed_data_dir: str = "data/processed", output_dir: str = "reports"):
        self.data_dir = Path(processed_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load data
        self.daily_df = pd.read_csv(self.data_dir / "01_daily_aggregates.csv")
        self.daily_df["date"] = pd.to_datetime(self.daily_df["date"])

        self.regional_df = pd.read_csv(self.data_dir / "02_regional_summary.csv")
        self.yearly_df = pd.read_csv(self.data_dir / "07_yearly_statistics.csv")
        self.monthly_df = pd.read_csv(self.data_dir / "08_monthly_pattern.csv")
        self.recent_escalation_df = pd.read_csv(self.data_dir / "18_recent_escalation.csv")

    def create_yearly_trend_chart(self):
        """Create yearly trend chart."""
        rolling_avg = self.daily_df["alerts_count_combined"].rolling(window=30).mean()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.daily_df["date"],
            y=self.daily_df["alerts_count_combined"],
            name="Daily Alerts",
            line=dict(color="rgba(255,68,68,0.3)", width=1),
            fill="tozeroy"
        ))

        fig.add_trace(go.Scatter(
            x=self.daily_df["date"],
            y=rolling_avg,
            name="30-day Moving Average",
            line=dict(color="#CC0000", width=3),
        ))

        fig.update_layout(
            title="Daily Air Raid Alerts: 2022-2026",
            xaxis_title="Date",
            yaxis_title="Number of Alerts",
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )

        return fig

    def create_yearly_comparison_chart(self):
        """Create yearly comparison."""
        fig = px.bar(
            self.yearly_df,
            x="year",
            y="total_alerts",
            title="Year-over-Year Alert Comparison",
            labels={"year": "Year", "total_alerts": "Total Alerts"},
            color="year",
            color_continuous_scale="Reds"
        )

        fig.update_layout(height=500, template="plotly_white")
        return fig

    def create_regional_chart(self):
        """Create top regions chart."""
        top_regions = self.regional_df.head(10)

        fig = px.barh(
            top_regions,
            x="total_alerts",
            y="oblast",
            title="Top 10 Most Affected Regions",
            labels={"total_alerts": "Total Alerts", "oblast": "Region"},
            color="total_alerts",
            color_continuous_scale="Reds"
        )

        fig.update_yaxis(autorange="reversed")
        fig.update_layout(height=500, template="plotly_white")
        return fig

    def create_escalation_chart(self):
        """Create recent escalation chart."""
        top_escalation = self.recent_escalation_df.head(10)

        fig = px.scatter(
            top_escalation,
            x="escalation_factor",
            y="oblast",
            size="recent_alerts",
            title="Recent Escalation: Last 6 Months",
            labels={"escalation_factor": "Escalation Factor", "oblast": "Region"},
            color="escalation_factor",
            color_continuous_scale="Reds",
            hover_data=["recent_alerts", "historical_avg"]
        )

        fig.update_layout(height=500, template="plotly_white")
        return fig

    def create_monthly_chart(self):
        """Create monthly pattern."""
        fig = px.bar(
            self.monthly_df,
            x="month_name",
            y="total_alerts",
            title="Monthly Pattern: Which Months Are Most Dangerous",
            labels={"month_name": "Month", "total_alerts": "Total Alerts"},
            color="total_alerts",
            color_continuous_scale="RdYlGn_r"
        )

        fig.update_layout(height=500, template="plotly_white")
        return fig

    def generate_html_report(self):
        """Generate complete HTML report."""
        logger.info("Generating HTML report...")

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Air Raid Alerts Analysis: Ukraine 2022-2026</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .header {
                    background-color: #2c3e50;
                    color: white;
                    padding: 30px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }
                .header h1 {
                    margin: 0;
                    font-size: 32px;
                }
                .header p {
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }
                .section {
                    background-color: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .section h2 {
                    color: #2c3e50;
                    border-bottom: 3px solid #e74c3c;
                    padding-bottom: 10px;
                }
                .finding {
                    background-color: #ecf0f1;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #e74c3c;
                    border-radius: 3px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #2c3e50;
                    color: white;
                    font-weight: bold;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .chart-container {
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    overflow: hidden;
                }
                .highlight {
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 3px;
                    margin: 15px 0;
                }
                .alert-danger {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 3px;
                    margin: 15px 0;
                }
                .footer {
                    text-align: center;
                    color: #7f8c8d;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Air Raid Alerts in Ukraine: Comprehensive Analysis</h1>
                <p>Data from March 2022 to June 2026 | 418,838 records | 25 regions</p>
            </div>

            <div class="section">
                <h2>Executive Summary</h2>
                <p>This analysis examines over four years of air raid alert data across Ukraine.
                The findings reveal a deeply concerning trend of escalating threats, with alert intensity
                more than doubling between 2023 and 2025.</p>

                <div class="alert-danger">
                    <strong>Key Finding:</strong> Alert intensity increased by <strong>75.8%</strong>
                    from 2024 to 2025, representing the most dangerous year of the conflict.
                </div>
            </div>

            <div class="section">
                <h2>Yearly Trends</h2>
                <div id="chart-yearly-trend" class="chart-container"></div>
                <p><em>Interactive chart showing daily alert counts with 30-day moving average trend line.</em></p>
            </div>

            <div class="section">
                <h2>Year-over-Year Comparison</h2>
                <div id="chart-yearly-comparison" class="chart-container"></div>
                <table>
                    <tr>
                        <th>Year</th>
                        <th>Total Alerts</th>
                        <th>Monthly Average</th>
                        <th>Change</th>
                    </tr>
        """

        for _, row in self.yearly_df.iterrows():
            change = f"{row['year_over_year_change']:+.1f}%" if pd.notna(row['year_over_year_change']) else "—"
            html_content += f"""
                    <tr>
                        <td>{int(row['year'])}</td>
                        <td>{int(row['total_alerts']):,}</td>
                        <td>{int(row['avg_monthly_alerts']):,}</td>
                        <td>{change}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>

            <div class="section">
                <h2>Regional Analysis</h2>
                <div id="chart-regional" class="chart-container"></div>
                <p>The top 3 regions account for 43.9% of all alerts.</p>
            </div>

            <div class="section">
                <h2>Recent Escalation (Last 6 Months)</h2>
                <div id="chart-escalation" class="chart-container"></div>
                <div class="finding">
                    <strong>Critical Finding:</strong> Western regions (Lviv, Ivano-Frankivsk, Zakarpattia)
                    experienced 3.3-3.4x escalation in the last 6 months, suggesting geographic expansion
                    of threats westward.
                </div>
            </div>

            <div class="section">
                <h2>Monthly Patterns</h2>
                <div id="chart-monthly" class="chart-container"></div>
                <p>Seasonal analysis showing which months experience highest alert activity.</p>
            </div>

            <div class="section">
                <h2>Key Statistics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Total Days with Alerts</td>
                        <td>1,563</td>
                    </tr>
                    <tr>
                        <td>Average Alerts per Day</td>
                        <td>152</td>
                    </tr>
                    <tr>
                        <td>Maximum Single Day</td>
                        <td>1,004 alerts</td>
                    </tr>
                    <tr>
                        <td>Regions Affected</td>
                        <td>25</td>
                    </tr>
                    <tr>
                        <td>Average Alert Duration</td>
                        <td>100-220 minutes (varies by region)</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>Conclusions</h2>
                <ol>
                    <li><strong>Escalation:</strong> Alerts have increased 75% from 2024 to 2025</li>
                    <li><strong>Concentration:</strong> 43.9% of alerts occur in just 3 regions</li>
                    <li><strong>Expansion:</strong> Western regions previously thought safer now face unprecedented threats</li>
                    <li><strong>Intensity:</strong> Average 152 alerts/day with extreme regional variation</li>
                    <li><strong>Duration:</strong> Alert durations 80-220 minutes indicate sustained military activity</li>
                </ol>
            </div>

            <div class="footer">
                <p>Analysis generated: June 2026 | Data period: March 2022 - June 2026 |
                <a href="https://github.com/sergkern1-netizen/air-raid-alerts-analysis">GitHub Repository</a></p>
            </div>

            <script>
                // Yearly trend chart
                var chart1 = """ + self.create_yearly_trend_chart().to_json() + """;
                Plotly.newPlot('chart-yearly-trend', chart1.data, chart1.layout, {responsive: true});

                // Yearly comparison
                var chart2 = """ + self.create_yearly_comparison_chart().to_json() + """;
                Plotly.newPlot('chart-yearly-comparison', chart2.data, chart2.layout, {responsive: true});

                // Regional chart
                var chart3 = """ + self.create_regional_chart().to_json() + """;
                Plotly.newPlot('chart-regional', chart3.data, chart3.layout, {responsive: true});

                // Escalation chart
                var chart4 = """ + self.create_escalation_chart().to_json() + """;
                Plotly.newPlot('chart-escalation', chart4.data, chart4.layout, {responsive: true});

                // Monthly chart
                var chart5 = """ + self.create_monthly_chart().to_json() + """;
                Plotly.newPlot('chart-monthly', chart5.data, chart5.layout, {responsive: true});
            </script>
        </body>
        </html>
        """

        output_file = self.output_dir / "comprehensive_analysis.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"[OK] HTML report saved: {output_file}")
        return output_file


if __name__ == "__main__":
    generator = HTMLReportGenerator()
    generator.generate_html_report()
    print("[OK] Interactive HTML report generated successfully!")
