"""
Query model for tracking user query history.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base
from app.models.types import GUID


class QueryStatus(str, enum.Enum):
    """Query execution status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class Query(Base):
    """
    Query model for tracking user query history and results.
    
    Stores natural language queries, LLM-generated SQL, execution results,
    and supports conversation threading via parent-child relationships.
    
    Attributes:
        id: Unique query identifier
        user_id: User who submitted the query
        natural_language_query: Original user question
        intent: Parsed query intent (descriptive, diagnostic, etc.)
        entities: Extracted entities (metrics, dimensions, time ranges)
        data_sources_used: Array of data source IDs used
        generated_sql: LLM-generated SQL query
        results: Query execution results (for caching)
        execution_time_ms: Query execution time in milliseconds
        status: Query status (pending, completed, failed, cached)
        error_message: Error message if query failed
        parent_query_id: Parent query for follow-up questions
        created_at: Query submission timestamp
    """
    __tablename__ = "queries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    natural_language_query = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    entities = Column(JSON, nullable=True, default=dict)
    data_sources_used = Column(JSON, nullable=True, default=list)
    generated_sql = Column(Text, nullable=True)
    results = Column(JSON, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    status = Column(SQLEnum(QueryStatus), nullable=False, default=QueryStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)
    parent_query_id = Column(GUID(), ForeignKey("queries.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    reports = relationship("Report", back_populates="query")
    
    # Self-referential for follow-up queries
    follow_ups = relationship("Query", backref="parent_query", remote_side=[id])
    
    def __repr__(self):
        return f"<Query(id={self.id}, status={self.status}, user_id={self.user_id})>"
