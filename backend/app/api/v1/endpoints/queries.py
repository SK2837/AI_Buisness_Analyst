from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import pandas as pd
import json
import uuid

from app.models.database import get_db
from app.models.query import Query, QueryStatus
from app.models.data_source import DataSource
from app.services.analysis.query_processor import QueryProcessor
from app.services.data.sql_generator import SQLGenerator
from app.services.data.executor import QueryExecutor
from app.services.analysis.stats_engine import StatsEngine
from app.services.analysis.narrative_generator import NarrativeGenerator

router = APIRouter()

# Services
query_processor = QueryProcessor()
sql_generator = SQLGenerator()
query_executor = QueryExecutor()
stats_engine = StatsEngine()
narrative_generator = NarrativeGenerator()

# Pydantic Schemas
class QueryRequest(BaseModel):
    natural_language_query: str
    data_source_id: str
    user_id: str = "3800df94-9c78-4bbc-b4a1-e8abae649bec"  # Admin user

class QueryResponse(BaseModel):
    query_id: str
    natural_language_query: str
    generated_sql: Optional[str]
    results: Optional[List[Dict[str, Any]]]
    narrative: Optional[Dict[str, Any]]
    status: str
    execution_time_ms: Optional[int]
    error_message: Optional[str]

# Endpoints

@router.post("/analyze", response_model=QueryResponse)
async def analyze_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a natural language query:
    1. Analyze intent
    2. Generate SQL
    3. Execute SQL
    4. Generate Statistics
    5. Generate Narrative
    """
    # 1. Fetch Data Source
    data_source = db.query(DataSource).filter(DataSource.id == request.data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Create Query Record
    db_query = Query(
        user_id=request.user_id,
        natural_language_query=request.natural_language_query,
        data_sources_used=[str(data_source.id)],
        status=QueryStatus.PENDING
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    try:
        # 2. Analyze Intent
        intent_result = await query_processor.analyze_query(request.natural_language_query)
        db_query.intent = intent_result.intent
        db_query.entities = {
            "metrics": intent_result.metrics,
            "dimensions": intent_result.dimensions,
            "time_range": intent_result.time_range,
            "filters": intent_result.filters
        }

        # 3. Generate SQL
        # We need schema context. For now, let's assume we can get it from the data source.
        # In a real app, we might cache this or fetch it dynamically.
        # For this implementation, we'll assume the data source has a 'schema_metadata' field 
        # or we fetch it. Since DataSource model doesn't strictly enforce schema storage,
        # we might need to fetch it or use a placeholder if not present.
        
        schema_context = data_source.schema_metadata if data_source.schema_metadata else {}
        if not schema_context:
            # Introspect schema from the data source if not stored
            schema_context = query_executor.get_schema_metadata(data_source)

        sql_result = await sql_generator.generate_sql(
            request.natural_language_query,
            schema_context,
            dialect=data_source.source_type.value
        )
        
        if not sql_result.get("can_answer"):
            db_query.status = QueryStatus.FAILED
            db_query.error_message = sql_result.get("explanation", "Cannot answer query with available schema")
            db.commit()
            return _format_response(db_query)

        generated_sql = sql_result["sql"]
        db_query.generated_sql = generated_sql

        # 4. Execute SQL
        df = await query_executor.execute_query(generated_sql, data_source)
        
        # Convert DF to dict for JSON storage
        results_dict = df.to_dict(orient="records")
        db_query.results = results_dict
        
        # 5. Generate Stats & Narrative
        # We need to determine the value column for stats. 
        # Heuristic: use the first numeric column or the first column.
        numeric_cols = df.select_dtypes(include=['number']).columns
        value_col = numeric_cols[0] if not numeric_cols.empty else df.columns[0]
        
        stats = stats_engine.calculate_summary_stats(df)
        # Add specific analysis based on intent if needed
        
        narrative = await narrative_generator.generate_narrative(
            user_query=request.natural_language_query,
            df=df,
            analysis_results=stats
        )
        
        # Store narrative in results or a separate field? 
        # The Query model doesn't have a specific 'narrative' column, but 'results' is JSONB.
        # We can wrap results.
        # Actually, let's look at the Query model again. It has 'results'.
        # We can store the narrative in the response but maybe not persist it structurally 
        # unless we add a column or put it in results.
        # Let's put it in a 'narrative' key within the results JSON for now, or just return it.
        # Wait, the QueryResponse has a 'narrative' field.
        # Let's update the DB results to include metadata.
        
        final_results = {
            "data": results_dict,
            "stats": stats,
            "narrative": narrative
        }
        db_query.results = final_results
        db_query.status = QueryStatus.COMPLETED
        db.commit()

        return _format_response(db_query, narrative)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in analyze_query: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        
        db_query.status = QueryStatus.FAILED
        db_query.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[QueryResponse])
def list_queries(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    queries = db.query(Query).order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    return [_format_response(q) for q in queries]

@router.get("/{query_id}", response_model=QueryResponse)
def get_query(query_id: str, db: Session = Depends(get_db)):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return _format_response(query)

def _format_response(query: Query, narrative: Optional[Dict] = None) -> QueryResponse:
    # Extract narrative from results if stored there
    narrative_data = narrative
    results_data = []
    
    if query.results:
        if isinstance(query.results, dict) and "data" in query.results:
            results_data = query.results["data"]
            if not narrative_data:
                narrative_data = query.results.get("narrative")
        elif isinstance(query.results, list):
            results_data = query.results

    return QueryResponse(
        query_id=str(query.id),
        natural_language_query=query.natural_language_query,
        generated_sql=query.generated_sql,
        results=results_data,
        narrative=narrative_data,
        status=query.status.value,
        execution_time_ms=query.execution_time_ms,
        error_message=query.error_message
    )
