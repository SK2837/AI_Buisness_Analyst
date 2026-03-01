import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.models.database import get_db
from app.models.user import User, UserRole
from app.models.data_source import DataSource, SourceType
from app.models.alert import Alert
from app.models.query import Query
from app.models.report import Report
from app.models.report_version import ReportVersion
from app.models.audit_log import AuditLog
from app.models.alert_execution import AlertExecution
from app.models.insight_cache import InsightCache

# Mock DB Session
mock_session = MagicMock()

def refresh_side_effect(instance):
    """Simulate DB refresh by setting ID and timestamps."""
    if not instance.id:
        instance.id = "mock-id-123"
    if not hasattr(instance, "created_at") or not instance.created_at:
        instance.created_at = "2023-01-01T00:00:00"
    if not hasattr(instance, "updated_at") or not instance.updated_at:
        instance.updated_at = "2023-01-01T00:00:00"
    if hasattr(instance, "last_connected_at") and not instance.last_connected_at:
        instance.last_connected_at = None
    if hasattr(instance, "last_refreshed_at") and not instance.last_refreshed_at:
        instance.last_refreshed_at = None
    if hasattr(instance, "is_active") and instance.is_active is None:
        instance.is_active = True

mock_session.refresh.side_effect = refresh_side_effect

def override_get_db():
    try:
        yield mock_session
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_login(client):
    # Setup mock user
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.email = "test@example.com"
    # Hash for "password" using passlib default (bcrypt)
    # We can just mock verify_password in the auth endpoint if we want, 
    # but since we are importing verify_password in auth.py, we might need to mock that too 
    # OR we can just use a known hash.
    # Let's mock the query to return a user.
    # And we need to ensure verify_password works.
    # Actually, let's mock the verify_password function in app.api.v1.endpoints.auth
    
    # But wait, we can't easily mock a function imported inside the module unless we patch it.
    # Let's use a real hash.
    from app.core.security import get_password_hash
    mock_user.hashed_password = get_password_hash("password")
    mock_user.is_active = True
    mock_user.role = UserRole.VIEWER
    
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_create_data_source(client):
    # Reset mock
    mock_session.reset_mock()
    
    # Mock existing check (return None)
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    response = client.post(
        "/api/v1/data_sources/",
        json={
            "name": "Test DB",
            "source_type": "postgresql",
            "connection_config": {
                "host": "localhost",
                "port": 5432,
                "user": "postgres",
                "password": "password",
                "database": "test_db"
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test DB"
    
    # Verify DB add was called
    assert mock_session.add.called
    assert mock_session.commit.called

def test_list_data_sources(client):
    # Setup mock return
    mock_ds = MagicMock()
    mock_ds.id = "ds-123"
    mock_ds.name = "Test DB"
    mock_ds.description = None
    mock_ds.source_type = SourceType.POSTGRESQL
    mock_ds.is_active = True
    mock_ds.last_connected_at = None
    mock_ds.last_refreshed_at = None
    mock_ds.created_at = "2023-01-01T00:00:00"
    
    mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [mock_ds]
    
    response = client.get("/api/v1/data_sources/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test DB"
