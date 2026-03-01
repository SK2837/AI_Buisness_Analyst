"""
User model for authentication and authorization.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base
from app.models.types import GUID


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and role-based access control.
    
    Attributes:
        id: Unique user identifier
        email: User email (unique, used for login)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role (admin, analyst, viewer)
        is_active: Whether the user account is active
        preferences: User preferences (UI settings, defaults)
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="creator", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
