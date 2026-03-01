"""
AuditLog model for security and compliance tracking.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from app.models.database import Base
from app.models.types import GUID


class AuditLog(Base):
    """
    AuditLog model for tracking user actions for security and compliance.
    
    Records all significant user actions including logins, queries,
    data access, and administrative operations.
    
    Attributes:
        id: Unique log entry identifier
        user_id: User who performed the action
        action: Action type (login, query, report_generate, etc.)
        resource_type: Type of resource accessed (user, query, report, etc.)
        resource_id: ID of the specific resource
        details: Additional context (parameters, results, etc.)
        ip_address: Client IP address
        user_agent: Client user agent string
        created_at: Action timestamp
    """
    __tablename__ = "audit_logs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(GUID(), nullable=True)
    details = Column(JSON, nullable=True, default=dict)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_audit_logs_user_created', 'user_id', 'created_at'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )
