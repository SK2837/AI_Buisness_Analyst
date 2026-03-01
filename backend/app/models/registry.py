"""
Ensure all ORM models are imported so SQLAlchemy can resolve relationships.
"""

# Import order doesn't matter; we just need them loaded.
from app.models.user import User  # noqa: F401
from app.models.data_source import DataSource  # noqa: F401
from app.models.query import Query  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.report_version import ReportVersion  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.alert_execution import AlertExecution  # noqa: F401
from app.models.insight_cache import InsightCache  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
