"""
Database connection and session management.

Provides SQLAlchemy engine, session factory, and base class for ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create SQLAlchemy engine with connection pooling
# Pool settings only apply to PostgreSQL, not SQLite
engine_args = {
    "pool_pre_ping": True,  # Verify connections before using
    "echo": settings.ENVIRONMENT == "development",  # Log SQL in dev mode
}

# Add pool settings only for PostgreSQL
if settings.DATABASE_URL.startswith("postgresql"):
    engine_args.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
    })

engine = create_engine(settings.DATABASE_URL, **engine_args)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI endpoints to get a database session.
    
    Yields:
        Database session that will be automatically closed after use.
        
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called on application startup if tables don't exist.
    For production, use Alembic migrations instead.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import user  # noqa: F401
    from app.models import data_source  # noqa: F401
    from app.models import query  # noqa: F401
    from app.models import report  # noqa: F401
    from app.models import report_version  # noqa: F401
    from app.models import alert  # noqa: F401
    from app.models import alert_execution  # noqa: F401
    from app.models import insight_cache  # noqa: F401
    from app.models import audit_log  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
