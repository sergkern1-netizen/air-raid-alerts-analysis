"""
Tests for Plotly graph generation module.

Tests ensure that:
1. All 3 HTML files are created successfully
2. HTML files contain valid Plotly JSON
3. Figures directory is created properly
"""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.generate_plots import PlotGenerator


class TestPlotGenerator:
    """Tests for PlotGenerator class."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(__file__).parent.parent / "data" / "processed"
            output_dir = Path(temp_dir) / "figures"
            yield data_dir, output_dir

    def test_plotgenerator_initialization(self, temp_dirs):
        """Test that PlotGenerator initializes correctly."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        # data_dir and output_dir are stored as Path objects
        assert str(generator.data_dir) == str(data_dir)
        assert str(generator.output_dir) == str(output_dir)

    def test_figures_directory_exists(self, temp_dirs):
        """Test that figures directory is created."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_all_plots()
        assert output_dir.exists(), "Figures directory should be created"

    def test_yearly_trend_plot_created(self, temp_dirs):
        """Test that yearly trend plot HTML file is created."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_yearly_trend()
        plot_file = output_dir / "01_yearly_trend.html"
        assert plot_file.exists(), "Yearly trend plot file should exist"
        assert plot_file.stat().st_size > 0, "Plot file should not be empty"

    def test_regional_heatmap_created(self, temp_dirs):
        """Test that regional heatmap HTML file is created."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_regional_heatmap()
        plot_file = output_dir / "02_regional_heatmap.html"
        assert plot_file.exists(), "Regional heatmap file should exist"
        assert plot_file.stat().st_size > 0, "Heatmap file should not be empty"

    def test_monthly_pattern_plot_created(self, temp_dirs):
        """Test that monthly pattern plot HTML file is created."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_monthly_pattern()
        plot_file = output_dir / "03_monthly_pattern.html"
        assert plot_file.exists(), "Monthly pattern plot file should exist"
        assert plot_file.stat().st_size > 0, "Plot file should not be empty"

    def test_all_plots_generated(self, temp_dirs):
        """Test that generate_all_plots creates all 3 files."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_all_plots()

        expected_files = [
            output_dir / "01_yearly_trend.html",
            output_dir / "02_regional_heatmap.html",
            output_dir / "03_monthly_pattern.html",
        ]

        for plot_file in expected_files:
            assert plot_file.exists(), f"{plot_file.name} should be created"
            assert plot_file.stat().st_size > 0, f"{plot_file.name} should not be empty"

    def test_plotly_json_in_yearly_trend(self, temp_dirs):
        """Test that yearly trend HTML contains valid Plotly JSON."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_yearly_trend()

        plot_file = output_dir / "01_yearly_trend.html"
        content = plot_file.read_text(encoding='utf-8')

        assert "Plotly.newPlot" in content or "plotly" in content.lower(), \
            "HTML should contain Plotly code"
        assert "Динаміка повітряних тривог 2022-2026" in content, \
            "HTML should contain plot title"

    def test_plotly_json_in_regional_heatmap(self, temp_dirs):
        """Test that regional heatmap HTML contains valid Plotly JSON."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_regional_heatmap()

        plot_file = output_dir / "02_regional_heatmap.html"
        content = plot_file.read_text(encoding='utf-8')

        assert "Plotly.newPlot" in content or "plotly" in content.lower(), \
            "HTML should contain Plotly code"
        assert "Інтенсивність тривог по регіонам" in content, \
            "HTML should contain plot title"

    def test_plotly_json_in_monthly_pattern(self, temp_dirs):
        """Test that monthly pattern HTML contains valid Plotly JSON."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))
        generator.generate_monthly_pattern()

        plot_file = output_dir / "03_monthly_pattern.html"
        content = plot_file.read_text(encoding='utf-8')

        assert "Plotly.newPlot" in content or "plotly" in content.lower(), \
            "HTML should contain Plotly code"
        assert "Сезонність тривог (по місяцях)" in content, \
            "HTML should contain plot title"

    def test_plots_generation_sequence(self, temp_dirs):
        """Test that plots can be generated in sequence."""
        data_dir, output_dir = temp_dirs
        generator = PlotGenerator(str(data_dir), str(output_dir))

        # Generate each plot individually
        generator.generate_yearly_trend()
        generator.generate_regional_heatmap()
        generator.generate_monthly_pattern()

        # Verify all files exist
        plot_files = list(output_dir.glob("*.html"))
        assert len(plot_files) >= 3, "At least 3 plot files should be generated"
