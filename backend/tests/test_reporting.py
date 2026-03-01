import pytest
import pandas as pd
import json
from app.services.visualization.chart_generator import ChartGenerator
from app.services.reporting.report_generator import ReportGenerator

# --- Chart Generator Tests ---

def test_generate_chart_line():
    """Test generating a line chart."""
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "value": [10, 20]
    })
    
    chart_json = ChartGenerator.generate_chart(df, "line", "date", "value", "Test Chart")
    
    assert "data" in chart_json
    assert "layout" in chart_json
    assert chart_json["layout"]["title"]["text"] == "Test Chart"
    # Plotly Express creates a scatter plot with mode='lines' for line charts
    assert chart_json["data"][0]["type"] == "scatter" 

def test_generate_chart_bar():
    """Test generating a bar chart."""
    df = pd.DataFrame({
        "category": ["A", "B"],
        "value": [10, 20]
    })
    
    chart_json = ChartGenerator.generate_chart(df, "bar", "category", "value")
    
    assert chart_json["data"][0]["type"] == "bar"

def test_recommend_chart_type():
    """Test chart type recommendation heuristic."""
    # Date x-axis -> Line
    df_date = pd.DataFrame({"date": pd.to_datetime(["2023-01-01", "2023-01-02"]), "val": [1, 2]})
    assert ChartGenerator.recommend_chart_type(df_date, "date", "val") == "line"
    
    # Categorical x-axis -> Bar
    df_cat = pd.DataFrame({"cat": ["A", "B", "C"], "val": [1, 2, 3]})
    assert ChartGenerator.recommend_chart_type(df_cat, "cat", "val") == "bar"

# --- Report Generator Tests ---

def test_generate_html_report():
    """Test HTML report rendering."""
    generator = ReportGenerator()
    
    sections = [
        {
            "title": "Section 1",
            "narrative": "<p>This is a test.</p>",
            "key_points": ["Point A", "Point B"],
            "chart_id": "chart1",
            "chart_json": {"data": [], "layout": {}}
        }
    ]
    
    html = generator.generate_html_report("Test Report", sections)
    
    assert "<!DOCTYPE html>" in html
    assert "Test Report" in html
    assert "Section 1" in html
    assert "Point A" in html
    assert "Plotly.newPlot('chart1'" in html
