"""
Database models for AI Business Analyst.

This package contains SQLAlchemy ORM models for:
- User management and authentication
- Data source configurations
- Query history and caching
- Report generation and versioning
- Alert rules and executions
- Audit logging
"""

from app.models.database import Base, get_db, init_db

__all__ = ["Base", "get_db", "init_db"]
