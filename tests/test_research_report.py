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
