import pytest
import pandas as pd
import numpy as np
from unittest.mock import AsyncMock, patch
from app.services.analysis.stats_engine import StatsEngine
from app.services.analysis.narrative_generator import NarrativeGenerator

# --- Stats Engine Tests ---

def test_calculate_trend_increasing():
    """Test linear trend calculation for increasing data."""
    df = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "value": [10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    })
    
    result = StatsEngine.calculate_trend(df, "date", "value")
    
    assert result["direction"] == "increasing"
    assert result["slope"] > 0
    assert result["r_squared"] > 0.9  # Strong correlation

def test_calculate_trend_decreasing():
    """Test linear trend calculation for decreasing data."""
    df = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "value": [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
    })
    
    result = StatsEngine.calculate_trend(df, "date", "value")
    
    assert result["direction"] == "decreasing"
    assert result["slope"] < 0

def test_detect_anomalies_zscore():
    """Test anomaly detection using Z-score."""
    # Create data with one obvious outlier
    data = [10, 10, 10, 10, 10, 10, 10, 10, 10, 100]
    df = pd.DataFrame({"value": data})
    
    anomalies = StatsEngine.detect_anomalies(df, "value", method="zscore", threshold=2.0)
    
    assert len(anomalies) == 1
    assert anomalies[0]["value"] == 100
    assert "Z-score" in anomalies[0]["anomaly_reason"]

def test_calculate_summary_stats():
    """Test summary statistics calculation."""
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [10, 20, 30, 40, 50],
        "C": ["a", "b", "c", "d", "e"]  # Non-numeric
    })
    
    stats = StatsEngine.calculate_summary_stats(df)
    
    assert "A" in stats
    assert "B" in stats
    assert "C" not in stats
    assert stats["A"]["mean"] == 3.0
    assert stats["B"]["max"] == 50.0

# --- Narrative Generator Tests ---

@pytest.mark.asyncio
async def test_generate_narrative():
    """Test narrative generation with mocked LLM."""
    mock_llm = AsyncMock()
    mock_llm.generate_json.return_value = {
        "summary": "Sales are increasing.",
        "narrative": "Detailed narrative...",
        "key_points": ["Point 1"],
        "recommendation": "Keep selling."
    }
    
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    analysis_results = {"trend": "increasing"}
    
    with patch("app.services.analysis.narrative_generator.LLMFactory.get_provider", return_value=mock_llm):
        generator = NarrativeGenerator()
        result = await generator.generate_narrative("How are sales?", df, analysis_results)
        
        assert result["summary"] == "Sales are increasing."
        
        # Verify prompt contained analysis results
        call_args = mock_llm.generate_json.call_args
        prompt = call_args.kwargs["prompt"]
        assert "increasing" in prompt
        assert "How are sales?" in prompt
