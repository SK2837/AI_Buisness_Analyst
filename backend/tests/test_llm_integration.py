import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.data.sql_validator import SQLValidator
from app.services.analysis.query_processor import QueryProcessor, QueryIntent
from app.services.data.sql_generator import SQLGenerator

# --- SQL Validator Tests ---

def test_sql_validator_safe_queries():
    """Test that safe SELECT queries are allowed."""
    safe_queries = [
        "SELECT * FROM users",
        "SELECT id, name FROM data_sources WHERE is_active = true",
        "SELECT count(*) FROM orders GROUP BY region",
        "SELECT t1.col1, t2.col2 FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id"
    ]
    for sql in safe_queries:
        assert SQLValidator.validate_sql(sql) is True

def test_sql_validator_unsafe_queries():
    """Test that destructive queries are blocked."""
    unsafe_queries = [
        "DROP TABLE users",
        "DELETE FROM data_sources",
        "UPDATE users SET is_active = false",
        "INSERT INTO audit_logs (action) VALUES ('hack')",
        "TRUNCATE TABLE reports",
        "ALTER TABLE users ADD COLUMN hacked boolean",
        "SELECT * FROM users; DROP TABLE users"  # Injection attempt
    ]
    for sql in unsafe_queries:
        assert SQLValidator.validate_sql(sql) is False

def test_sql_validator_empty():
    """Test empty input."""
    assert SQLValidator.validate_sql("") is False
    assert SQLValidator.validate_sql(None) is False

# --- Query Processor Tests ---

@pytest.mark.asyncio
async def test_query_processor_analyze():
    """Test query analysis with mocked LLM."""
    mock_llm = AsyncMock()
    mock_llm.generate_json.return_value = {
        "intent": "DESCRIPTIVE",
        "metrics": ["sales"],
        "dimensions": ["region"],
        "time_range": "last month",
        "filters": {},
        "complexity": "simple"
    }
    
    with patch("app.services.analysis.query_processor.LLMFactory.get_provider", return_value=mock_llm):
        processor = QueryProcessor()
        result = await processor.analyze_query("Show me sales by region last month")
        
        assert isinstance(result, QueryIntent)
        assert result.intent == "DESCRIPTIVE"
        assert "sales" in result.metrics
        assert "region" in result.dimensions
        
        # Verify prompt contained user query
        call_args = mock_llm.generate_json.call_args
        assert "Show me sales by region last month" in call_args.kwargs["prompt"]

# --- SQL Generator Tests ---

@pytest.mark.asyncio
async def test_sql_generator_success():
    """Test successful SQL generation."""
    mock_llm = AsyncMock()
    mock_llm.generate_json.return_value = {
        "sql": "SELECT region, SUM(sales) FROM sales_data GROUP BY region",
        "explanation": "Summing sales by region",
        "can_answer": True
    }
    
    schema = {
        "sales_data": {
            "columns": [
                {"name": "region", "type": "VARCHAR"},
                {"name": "sales", "type": "DECIMAL"}
            ]
        }
    }
    
    with patch("app.services.data.sql_generator.LLMFactory.get_provider", return_value=mock_llm):
        generator = SQLGenerator()
        result = await generator.generate_sql("Sales by region", schema)
        
        assert result["sql"] == "SELECT region, SUM(sales) FROM sales_data GROUP BY region"
        assert result["can_answer"] is True

@pytest.mark.asyncio
async def test_sql_generator_unsafe_output():
    """Test that unsafe SQL from LLM is blocked."""
    mock_llm = AsyncMock()
    # LLM goes rogue and tries to drop a table
    mock_llm.generate_json.return_value = {
        "sql": "DROP TABLE sales_data",
        "explanation": "Deleting data",
        "can_answer": True
    }
    
    schema = {"sales_data": {}}
    
    with patch("app.services.data.sql_generator.LLMFactory.get_provider", return_value=mock_llm):
        generator = SQLGenerator()
        result = await generator.generate_sql("Delete everything", schema)
        
        # Should return empty SQL and can_answer=False
        assert result["sql"] == ""
        assert result["can_answer"] is False
        assert "unsafe" in result["explanation"]
