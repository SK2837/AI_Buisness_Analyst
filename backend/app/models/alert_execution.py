"""
AlertExecution model for alert execution history.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Text, Boolean, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base
from app.models.types import GUID


class ExecutionStatus(str, enum.Enum):
    """Alert execution status."""
    TRIGGERED = "triggered"
    NOT_TRIGGERED = "not_triggered"
    ERROR = "error"


class AlertExecution(Base):
    """
    AlertExecution model for tracking alert check results.
    
    Records each time an alert is evaluated, whether it triggered,
    and the actual data values at execution time.
    
    Attributes:
        id: Unique execution identifier
        alert_id: Alert that was executed
        executed_at: Execution timestamp
        status: Execution result (triggered, not_triggered, error)
        result_data: Actual metric values at execution time
        notification_sent: Whether notification was successfully sent
        error_message: Error message if execution failed
    """
    __tablename__ = "alert_executions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    alert_id = Column(GUID(), ForeignKey("alerts.id"), nullable=False, index=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), nullable=False)
    result_data = Column(JSON, nullable=True)
    notification_sent = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    alert = relationship("Alert", back_populates="executions")
    
    def __repr__(self):
        return f"<AlertExecution(id={self.id}, alert_id={self.alert_id}, status={self.status})>"
