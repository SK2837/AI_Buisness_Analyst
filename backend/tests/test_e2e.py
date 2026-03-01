import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.models.database import get_db
from app.models.user import User, UserRole
from app.models.query import Query, QueryStatus
from app.models.report import Report
from app.models.data_source import DataSource
from app.models.report import Report

# Mock DB Session
mock_session = MagicMock()

def override_get_db():
    try:
        yield mock_session
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_full_query_flow(client):
    """
    Scenario 1: Full Query Flow
    User logs in -> Submits Query -> SQL Generated -> Executed -> Narrative Created -> Result Returned.
    """
    # 1. Mock Login (skip actual auth call, assume we have token or endpoint is open/mocked)
    # For this test, we'll hit the analyze endpoint directly.
    
    # Mock dependencies
    with patch("app.services.analysis.query_processor.QueryProcessor.analyze_query") as mock_analyze, \
         patch("app.services.data.sql_generator.SQLGenerator.generate_sql") as mock_gen_sql, \
         patch("app.services.data.executor.QueryExecutor.execute_query") as mock_exec, \
         patch("app.services.analysis.stats_engine.StatsEngine.calculate_summary_stats") as mock_stats, \
         patch("app.services.analysis.narrative_generator.NarrativeGenerator.generate_narrative") as mock_narrative:
        
        # Setup Mocks
        mock_analyze.return_value = MagicMock(
            intent="DIAGNOSTIC",
            metrics=["sales"],
            dimensions=["region"],
            filters={}
        )
        
        mock_gen_sql.return_value = {
            "sql": "SELECT region, SUM(sales) FROM sales GROUP BY region",
            "can_answer": True
        }
        
        import pandas as pd
        mock_df = pd.DataFrame({"region": ["East", "West"], "sales": [100, 200]})
        mock_exec.return_value = mock_df
        
        mock_stats.return_value = {"mean": 150}
        
        mock_narrative.return_value = {
            "summary": "Sales are higher in the West.",
            "detailed_analysis": "West has 200 sales vs East 100.",
            "recommendations": ["Focus on West."]
        }
        
        # Mock DB Query creation
        mock_query = MagicMock()
        mock_query.id = "query-123"
        mock_query.status = QueryStatus.COMPLETED
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Mock DataSource retrieval
        mock_data_source = MagicMock()
        mock_data_source.id = "datasource-123"
        mock_data_source.schema_metadata = {}
        mock_session.query.return_value.filter.return_value.first.side_effect = lambda *args, **kwargs: mock_data_source if args and isinstance(args[0], type) and args[0].__name__ == "DataSource" else None
        
        # Execute Request
        response = client.post(
            "/api/v1/queries/analyze",
            json={"natural_language_query": "Compare sales by region", "data_source_id": "datasource-123"}
        )
        # Verify Response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["narrative"]["summary"] == "Sales are higher in the West."
        # Ensure results contain expected keys
        assert "data" in data["results"]

def test_report_generation_flow(client):
    """
    Scenario 2: Report Generation
    User requests report -> Data fetched -> Charts generated -> HTML rendered.
    """
    with patch("app.services.reporting.report_generator.ReportGenerator.generate_report") as mock_gen_report:
        mock_gen_report.return_value = "<html>Report Content</html>"
        
        # Mock DB Report creation
        mock_report = MagicMock()
        mock_report.id = "report-123"
        # mock_report.status = ReportStatus.COMPLETED # Report model doesn't have status field currently
        mock_session.query.return_value.filter.return_value.first.return_value = mock_report
        
        # 1. Trigger Generation
        response = client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Monthly Sales",
                "query_ids": ["query-123"],
                "format": "html"
            }
        )
        assert response.status_code == 202 # Accepted/Processing
        
        # 2. Render Report
        response = client.get("/api/v1/reports/report-123/render")
        assert response.status_code == 200
        # Note: In a real async flow, we'd check status first, but here we mocked the generator to return immediately or we are testing the render endpoint which might just return the stored HTML. 
        # The mock implementation in reports.py might be simple.
