"""
InsightCache model for caching expensive analysis results.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy import Index

from app.models.database import Base
from app.models.types import GUID


class InsightCache(Base):
    """
    InsightCache model for caching expensive query and analysis results.
    
    Improves performance by storing results of expensive operations
    with time-based expiration.
    
    Attributes:
        id: Unique cache entry identifier
        cache_key: Unique hash of query + parameters
        query_hash: Hash of the natural language query
        data_source_ids: Array of data source IDs used
        result_data: Cached analysis results
        computation_time_ms: Original computation time
        hit_count: Number of cache hits
        expires_at: Cache expiration timestamp
        created_at: Cache entry creation timestamp
        updated_at: Last access timestamp
    """
    __tablename__ = "insight_cache"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    query_hash = Column(String(255), nullable=False, index=True)
    data_source_ids = Column(JSON, nullable=False, default=list)
    result_data = Column(JSON, nullable=False)
    computation_time_ms = Column(Integer, nullable=False)
    hit_count = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InsightCache(id={self.id}, cache_key={self.cache_key[:16]}..., hits={self.hit_count})>"
    
    # Additional index for cleanup queries
    __table_args__ = (
        Index('ix_insight_cache_expires_at_created_at', 'expires_at', 'created_at'),
    )
