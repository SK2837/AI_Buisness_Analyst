"""
Report model for generated reports.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base
from app.models.types import GUID


class ReportType(str, enum.Enum):
    """Report type enumeration."""
    QUICK_INSIGHT = "quick_insight"
    EXECUTIVE_SUMMARY = "executive_summary"
    DEEP_DIVE = "deep_dive"
    ALERT_REPORT = "alert_report"


class ReportFormat(str, enum.Enum):
    """Report format enumeration."""
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"
    PPTX = "pptx"

class ReportStatus(str, enum.Enum):
    """Report status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """
    Report model for storing generated reports.
    
    Stores report content, visualizations, and metadata.
    Supports scheduled reports and version history.
    
    Attributes:
        id: Unique report identifier
        user_id: User who generated the report
        query_id: Optional query that generated this report
        title: Report title
        report_type: Type of report (quick_insight, executive_summary, etc.)
        content: Structured report content (summary, narrative, recommendations)
        visualizations: Array of chart configurations
        format: Output format (html, pdf, markdown, pptx)
        report_metadata: Tags, categories, custom fields
        is_scheduled: Whether this is a scheduled recurring report
        schedule_config: Cron expression and recipients for scheduled reports
        shared_with: Array of user IDs or team IDs with access
        created_at: Report generation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "reports"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    query_id = Column(GUID(), ForeignKey("queries.id"), nullable=True)
    title = Column(String(500), nullable=False)
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    visualizations = Column(JSON, nullable=True, default=list)
    format = Column(SQLEnum(ReportFormat), nullable=False, default=ReportFormat.HTML)
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    report_metadata = Column(JSON, nullable=True, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    is_scheduled = Column(Boolean, default=False, nullable=False, index=True)
    schedule_config = Column(JSON, nullable=True)
    shared_with = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    query = relationship("Query", back_populates="reports")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Report(id={self.id}, title={self.title}, type={self.report_type})>"
