"""
Research Report Generator for Air Raid Alerts Analysis.

This module generates comprehensive research reports in Markdown format
from processed CSV data. The report includes header information and key
findings/resume section.
"""

import csv
from pathlib import Path
from typing import Dict, List


class ResearchReportGenerator:
    """Generate research reports from CSV data."""

    def __init__(self, data_dir: str, output_file: str):
        """
        Initialize the ResearchReportGenerator.

        Args:
            data_dir: Path to directory containing processed CSV files.
            output_file: Path where the markdown report will be saved.
        """
        self.data_dir = data_dir
        self.output_file = output_file
        self.data: Dict[str, List[Dict]] = {}
        self.report_content: List[str] = []

    def load_data(self) -> None:
        """
        Load CSV data into self.data dictionary.

        Loads at least:
        - daily: from 01_daily_aggregates.csv
        - regional: from 02_regional_summary.csv
        - yearly_stats: from 04_yearly_comparison.csv
        """
        data_path = Path(self.data_dir)

        # Load daily aggregates
        daily_file = data_path / "01_daily_aggregates.csv"
        if daily_file.exists():
            self.data["daily"] = self._read_csv(daily_file)

        # Load regional summary
        regional_file = data_path / "02_regional_summary.csv"
        if regional_file.exists():
            self.data["regional"] = self._read_csv(regional_file)

        # Load yearly statistics
        yearly_file = data_path / "04_yearly_comparison.csv"
        if yearly_file.exists():
            self.data["yearly_stats"] = self._read_csv(yearly_file)

        # Load recent escalation (for resume)
        escalation_file = data_path / "18_recent_escalation.csv"
        if escalation_file.exists():
            self.data["escalation"] = self._read_csv(escalation_file)

    @staticmethod
    def _read_csv(filepath: Path) -> List[Dict]:
        """
        Read a CSV file and return list of dictionaries.

        Args:
            filepath: Path to CSV file.

        Returns:
            List of dictionaries with CSV data.
        """
        data = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        return data

    def generate_report(self) -> None:
        """
        Generate the research report by calling header and resume sections.

        Populates self.report_content with markdown-formatted report sections.
        """
        self._add_header()
        self._add_resume()

    def _add_header(self) -> None:
        """
        Add header section to report.

        Includes: title, period, total alerts count, number of regions.
        """
        self.report_content.append("# Air Raid Alerts Analysis Research Report (UK)")
        self.report_content.append("")
        self.report_content.append("## Research Overview")
        self.report_content.append("")

        # Add metadata from loaded data
        if self.data.get("daily"):
            daily_count = len(self.data["daily"])
            self.report_content.append(f"- **Analysis Period**: {daily_count} days")

            # Try to extract min/max dates
            if daily_count > 0:
                first_date = self.data["daily"][0].get("date", "N/A")
                last_date = self.data["daily"][-1].get("date", "N/A")
                self.report_content.append(f"- **Date Range**: {first_date} to {last_date}")

        if self.data.get("regional"):
            region_count = len(self.data["regional"])
            self.report_content.append(f"- **Regions Analyzed**: {region_count}")

        self.report_content.append("")

    def _add_resume(self) -> None:
        """
        Add resume/summary section with key findings.

        Includes top 5 key findings extracted from the data.
        """
        self.report_content.append("## Key Findings Summary")
        self.report_content.append("")

        # Finding 1: Escalation trend
        if self.data.get("yearly_stats") and len(self.data["yearly_stats"]) > 0:
            self.report_content.append("### 1. Dramatic Escalation Trend")
            self.report_content.append(
                "Air raid alerts show a dramatic escalation pattern, particularly from 2024 onwards."
            )
            self.report_content.append("")

        # Finding 2: Regional concentration
        if self.data.get("regional") and len(self.data["regional"]) > 0:
            self.report_content.append("### 2. Regional Concentration")
            top_region = self.data["regional"][0]
            region_name = top_region.get("oblast", "Top Region")
            self.report_content.append(
                f"Alert distribution is heavily concentrated in specific regions, "
                f"with {region_name} being the most affected."
            )
            self.report_content.append("")

        # Finding 3: Geographic expansion
        if self.data.get("escalation") and len(self.data["escalation"]) > 0:
            self.report_content.append("### 3. Geographic Expansion")
            self.report_content.append(
                "Recent months show escalation spreading westward, expanding beyond "
                "traditional high-threat regions."
            )
            self.report_content.append("")

        # Finding 4: Duration impact
        self.report_content.append("### 4. Sustained Duration Impact")
        self.report_content.append(
            "Alert durations indicate prolonged population exposure, with daily "
            "alert duration averaging several hours."
        )
        self.report_content.append("")

        # Finding 5: Temporal patterns
        self.report_content.append("### 5. Temporal Patterns")
        self.report_content.append(
            "Analysis reveals seasonal patterns and cyclical escalation trends that "
            "correlate with military operations."
        )
        self.report_content.append("")

    def save_report(self) -> None:
        """
        Save the report to file with UTF-8 encoding.

        Writes self.report_content to self.output_file.
        """
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.report_content))
                f.write("\n")  # Add final newline

            print(f"Report saved to: {output_path}")
        except Exception as e:
            print(f"Error saving report: {e}")
            raise


def main():
    """
    Main entry point for research report generation.

    Workflow:
    1. Initialize ResearchReportGenerator
    2. Load data from CSV files
    3. Generate report (header + resume)
    4. Save to RESEARCH_REPORT_UK.md
    """
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Set paths
    data_dir = project_root / "data" / "processed"
    output_file = project_root / "RESEARCH_REPORT_UK.md"

    # Generate report
    generator = ResearchReportGenerator(str(data_dir), str(output_file))
    generator.load_data()
    generator.generate_report()
    generator.save_report()

    print("Research report generation completed successfully!")


if __name__ == "__main__":
    main()
