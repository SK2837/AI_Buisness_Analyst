"""
DataSource model for managing connected data sources.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base
from app.models.types import GUID


class SourceType(str, enum.Enum):
    """Data source type enumeration."""
    CSV = "csv"
    EXCEL = "excel"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"
    API = "api"
    S3 = "s3"
    GOOGLE_SHEETS = "google_sheets"


class DataSource(Base):
    """
    DataSource model for managing connected data sources.
    
    Stores connection configurations (encrypted) and schema metadata
    for various data source types including databases, files, and APIs.
    
    Attributes:
        id: Unique data source identifier
        name: Human-readable name for the data source
        description: Optional description
        source_type: Type of data source (csv, postgresql, api, etc.)
        connection_config: Encrypted connection details (credentials, host, etc.)
        schema_metadata: Table/column information, data types
        is_active: Whether this data source is currently active
        last_connected_at: Last successful connection timestamp
        last_refreshed_at: Last data refresh timestamp
        refresh_schedule: Cron expression for scheduled refreshes
        created_by: User who created this data source
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "data_sources"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_type = Column(SQLEnum(SourceType), nullable=False, index=True)
    connection_config = Column(JSON, nullable=False)  # Encrypted credentials stored here
    schema_metadata = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_connected_at = Column(DateTime, nullable=True)
    last_refreshed_at = Column(DateTime, nullable=True)
    refresh_schedule = Column(String(100), nullable=True)  # Cron expression
    
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="data_sources")
    alerts = relationship("Alert", back_populates="data_source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name}, type={self.source_type})>"
