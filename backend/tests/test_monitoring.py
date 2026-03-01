import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.monitoring.alert_engine import AlertEngine
from app.services.monitoring.notifier import NotificationService
from app.models.alert import Alert, AlertType
from app.models.user import User  # Required for relationship resolution
from app.models.data_source import DataSource  # Required for relationship resolution
from app.models.query import Query
from app.models.report import Report
from app.models.report_version import ReportVersion
from app.models.audit_log import AuditLog
from app.models.insight_cache import InsightCache
import pandas as pd

# --- Notification Service Tests ---

@pytest.mark.asyncio
async def test_send_notification_console():
    """Test sending notification to console."""
    service = NotificationService()
    # Capture stdout/logging? 
    # For simplicity, we just ensure it doesn't raise an error
    await service.send_notification("test@example.com", "Subject", "Message", ["console"])

@pytest.mark.asyncio
async def test_send_notification_email_mock():
    """Test email sending logic (mocked)."""
    service = NotificationService()
    with patch.object(service, "_send_email", new_callable=AsyncMock) as mock_email:
        await service.send_notification("test@example.com", "Subject", "Message", ["email"])
        mock_email.assert_called_once()

# --- Alert Engine Tests ---

class MockAlertEngine(AlertEngine):
    """Subclass to expose protected methods for testing."""
    pass

def test_check_threshold_greater():
    """Test threshold check: value > threshold."""
    engine = MockAlertEngine(MagicMock())
    df = pd.DataFrame({"val": [10, 20, 30]})
    config = {"column": "val", "operator": ">", "threshold": 25}
    
    triggered, val, msg = engine._check_threshold(df, config)
    assert triggered is True
    assert val == 30

def test_check_threshold_less_no_trigger():
    """Test threshold check: value < threshold (not triggered)."""
    engine = MockAlertEngine(MagicMock())
    df = pd.DataFrame({"val": [10, 20, 30]})
    config = {"column": "val", "operator": "<", "threshold": 25}
    
    triggered, val, msg = engine._check_threshold(df, config)
    assert triggered is False
    assert val == 30

def test_check_anomaly_detected():
    """Test anomaly check with mocked StatsEngine."""
    engine = MockAlertEngine(MagicMock())
    engine.stats_engine = MagicMock()
    
    # Mock stats engine to return an anomaly
    engine.stats_engine.detect_anomalies.return_value = [
        {"val": 100, "anomaly_reason": "Too high"}
    ]
    
    df = pd.DataFrame({"val": [10, 10, 100]})
    config = {"column": "val"}
    
    triggered, val, msg = engine._check_anomaly(df, config)
    assert triggered is True
    assert val == 100
    assert "Too high" in msg

@pytest.mark.asyncio
async def test_evaluate_alert_flow():
    """Test full alert evaluation flow with mocks."""
    mock_db = MagicMock()
    mock_alert = MagicMock()
    mock_alert.id = "alert-1"
    mock_alert.is_active = True
    mock_alert.type = AlertType.THRESHOLD
    mock_alert.config = {"column": "val", "operator": ">", "threshold": 50, "sql": "SELECT * FROM data"}
    mock_alert.channels = ["console"]
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_alert
    
    engine = AlertEngine(mock_db)
    engine.query_executor = AsyncMock()
    engine.query_executor.execute_query.return_value = pd.DataFrame({"val": [10, 60]})
    engine.notifier = AsyncMock()
    
    await engine.evaluate_alert("alert-1")
    
    # Verify notification sent
    engine.notifier.send_notification.assert_called_once()
    call_args = engine.notifier.send_notification.call_args
    assert "Alert Triggered" in call_args.kwargs["subject"]
