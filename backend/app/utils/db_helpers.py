"""
Database utility functions and helpers.
"""

import hashlib
import json
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.models.database import SessionLocal


def get_db():
    """
    FastAPI dependency for database sessions.
    Use this in route handlers.
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    from app.models.database import get_db as _get_db
    return _get_db()


def generate_cache_key(query: str, data_source_ids: list, params: Dict[str, Any] = None) -> str:
    """
    Generate a consistent cache key for query results.
    
    Args:
        query: Natural language query or SQL query
        data_source_ids: List of data source UUIDs
        params: Optional additional parameters (filters, date ranges, etc.)
        
    Returns:
        SHA256 hash of the input as cache key
        
    Example:
        >>> key = generate_cache_key("sales last month", [uuid1, uuid2], {"region": "west"})
        >>> print(key)
        'a3b5c8d...'
    """
    # Sort data source IDs for consistent ordering
    sorted_sources = sorted([str(ds_id) for ds_id in data_source_ids])
    
    # Create deterministic string representation
    cache_input = {
        "query": query.lower().strip(),
        "data_sources": sorted_sources,
        "params": params or {}
    }
    
    # Generate hash
    cache_str = json.dumps(cache_input, sort_keys=True)
    return hashlib.sha256(cache_str.encode()).hexdigest()


def generate_query_hash(query: str) -> str:
    """
    Generate a hash for a natural language query.
    
    Used for grouping similar queries and analytics.
    
    Args:
        query: Natural language query text
        
    Returns:
        SHA256 hash of normalized query
    """
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()
