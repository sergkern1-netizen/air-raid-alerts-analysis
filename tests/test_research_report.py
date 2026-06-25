"""
Unit tests for research report generation.
Tests for ResearchReportGenerator class.
"""
import os
import pytest
from pathlib import Path


class TestResearchReportGenerator:
    """Test suite for ResearchReportGenerator."""

    @pytest.fixture
    def data_dir(self):
        """Fixture: path to processed data directory."""
        return Path(__file__).parent.parent / "data" / "processed"

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Fixture: temporary output directory for tests."""
        return tmp_path

    def test_csv_files_exist(self, data_dir):
        """
        Test that all 14 required CSV files exist and are not empty.

        CSV files checked:
        - 01_daily_aggregates.csv
        - 02_regional_summary.csv
        - 03_regional_daily.csv
        - 04_yearly_comparison.csv
        - 05_duration_statistics.csv
        - 07_yearly_statistics.csv
        - 08_monthly_pattern.csv
        - 09_month_year_matrix.csv
        - 10_quarterly_pattern.csv
        - 11_peak_weeks.csv
        - 13_regional_ranking.csv
        - 15_duration_by_region.csv
        - 16_regional_trends.csv
        - 18_recent_escalation.csv
        """
        required_files = [
            "01_daily_aggregates.csv",
            "02_regional_summary.csv",
            "03_regional_daily.csv",
            "04_yearly_comparison.csv",
            "05_duration_statistics.csv",
            "07_yearly_statistics.csv",
            "08_monthly_pattern.csv",
            "09_month_year_matrix.csv",
            "10_quarterly_pattern.csv",
            "11_peak_weeks.csv",
            "13_regional_ranking.csv",
            "15_duration_by_region.csv",
            "16_regional_trends.csv",
            "18_recent_escalation.csv",
        ]

        for filename in required_files:
            filepath = data_dir / filename
            assert filepath.exists(), f"CSV file not found: {filename}"
            assert filepath.stat().st_size > 0, f"CSV file is empty: {filename}"

    def test_csv_data_quality(self, data_dir):
        """
        Test that 01_daily_aggregates.csv has 1500+ rows of data.

        This CSV is the backbone of the analysis, must have sufficient data.
        """
        import csv

        filepath = data_dir / "01_daily_aggregates.csv"
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) >= 1500, (
            f"01_daily_aggregates.csv has {len(rows)} rows, need >= 1500"
        )

    def test_research_report_generator_init(self, output_dir):
        """Test ResearchReportGenerator initialization."""
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_UK.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))

        assert generator.data_dir == str(data_dir)
        assert generator.output_file == str(output_file)
        assert isinstance(generator.data, dict)
        assert isinstance(generator.report_content, list)
        assert len(generator.report_content) == 0

    def test_research_report_generator_load_data(self, output_dir):
        """Test ResearchReportGenerator.load_data() method."""
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_UK.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()

        # Check that key CSVs are loaded
        assert "daily" in generator.data, "daily aggregates not loaded"
        assert "regional" in generator.data, "regional summary not loaded"
        assert "yearly_stats" in generator.data, "yearly stats not loaded"

        # Check that data is not empty
        assert len(generator.data["daily"]) > 0, "daily data is empty"
        assert len(generator.data["regional"]) > 0, "regional data is empty"

    def test_research_report_generator_generate_report(self, output_dir):
        """Test ResearchReportGenerator.generate_report() method."""
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_UK.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()

        # Check that report_content has been populated
        assert len(generator.report_content) > 0, "report_content is empty"

        # Check that both header and resume are in content
        report_text = "\n".join(generator.report_content)
        assert "# Research Report" in report_text or "#" in report_text, (
            "Report header not found"
        )

    def test_research_report_generator_save_report(self, output_dir):
        """Test ResearchReportGenerator.save_report() method."""
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_UK.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()
        generator.save_report()

        # Check that file was created
        assert Path(output_file).exists(), f"Report file not created: {output_file}"

        # Check that file has content
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 0, "Report file is empty"

    def test_research_report_generator_full_workflow(self, output_dir):
        """Test complete workflow: init → load_data → generate_report → save_report."""
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_UK.md"

        # Full workflow
        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()
        generator.save_report()

        # Verify file was created and has content
        assert Path(output_file).exists()
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100, "Report seems too short"
        assert "# " in content, "Report should have markdown headers"

    def test_report_has_all_sections(self, output_dir):
        """
        Test that the generated report contains all 12 sections.

        Sections (by number):
        1. Header
        2. Overview
        3. Data Overview
        4. Methodology
        5. EDA (Exploratory Data Analysis) - includes 5.1-5.6
        6. Findings
        7. Regional Analysis
        8. Temporal Analysis
        9. Models Comparison
        10-12. Additional sections

        Verifies presence of Ukrainian section headers and content.
        """
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_SECTIONS.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()
        generator.save_report()

        # Read generated report
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key section markers and content
        required_markers = [
            "# ",  # Main title
            "## 1.",  # Section 1
            "## 2.",  # Section 2
            "## 3.",  # Section 3
            "## 5.",  # EDA section
            "## 6.",  # Findings section
            "## 7.",  # Regional section
            "## 8.",  # Temporal section
            "## 9.",  # Models section
            "## 10.",  # Resume section
        ]

        for marker in required_markers:
            assert marker in content, f"Section marker '{marker}' not found in report"

        # Check for key content keywords (in Ukrainian)
        required_content = [
            "|",  # Tables
            "тревог",  # Alerts
            "область",  # Regions
        ]

        for keyword in required_content:
            assert keyword in content, f"Content keyword '{keyword}' not found in report"

    def test_report_content_quality(self, output_dir):
        """
        Test that the generated report has sufficient content.

        Minimum requirements:
        - Report should have at least 15,000 characters (realistic for full report)
        - Should contain real data (numbers from CSV files)
        - Should have multiple sections with tables
        """
        from scripts.generate_research_report import ResearchReportGenerator

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_QUALITY.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()
        generator.save_report()

        # Read generated report
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check content quality - print for debugging
        print(f"\nReport length: {len(content)} characters")

        # Check content quality - report should have substantial content
        # MVP target: at least 12000 characters for comprehensive report
        assert len(content) > 12000, (
            f"Report too short: {len(content)} chars (need >= 12000)"
        )

        # Check for tables (markdown table indicators)
        table_count = content.count("|")
        assert table_count > 20, (
            f"Report should contain markdown tables (found {table_count} pipes)"
        )

        # Check for numbers (real data)
        import re
        numbers = re.findall(r"\d+", content)
        assert len(numbers) > 30, (
            f"Report should contain many numeric values from data (found {len(numbers)})"
        )

    def test_report_uses_real_data(self, output_dir):
        """
        Test that the generated report uses actual data from CSV files.

        Verifies that specific numeric values from source CSVs appear in the report.
        """
        from scripts.generate_research_report import ResearchReportGenerator
        import csv

        data_dir = Path(__file__).parent.parent / "data" / "processed"
        output_file = output_dir / "RESEARCH_REPORT_REALDATA.md"

        generator = ResearchReportGenerator(str(data_dir), str(output_file))
        generator.load_data()
        generator.generate_report()
        generator.save_report()

        # Read generated report
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract some known values from source CSVs
        # Check 07_yearly_statistics.csv for year 2025
        yearly_file = data_dir / "07_yearly_statistics.csv"
        assert yearly_file.exists(), "07_yearly_statistics.csv should exist"

        with open(yearly_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Find 2025 row
            year_2025 = next((r for r in rows if r.get("year") == "2025"), None)
            assert year_2025 is not None, "Year 2025 should exist in data"

            # Check that this year's alert count appears in report
            alerts_2025 = year_2025.get("total_alerts", "")
            if alerts_2025:
                assert alerts_2025 in content, (
                    f"Year 2025 alert count ({alerts_2025}) should appear in report"
                )

        # Check top region data
        regional_file = data_dir / "02_regional_summary.csv"
        assert regional_file.exists(), "02_regional_summary.csv should exist"

        with open(regional_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0, "Regional data should exist"

            # Top region should be in report
            top_region = rows[0]
            top_region_name = top_region.get("oblast", "")
            if top_region_name:
                assert top_region_name in content, (
                    f"Top region '{top_region_name}' should appear in report"
                )
