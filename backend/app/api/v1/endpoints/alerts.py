from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.alert import Alert, AlertType
from app.models.alert_execution import ExecutionStatus
from pydantic import BaseModel, Field

router = APIRouter()

# Pydantic schemas
class AlertCreate(BaseModel):
    user_id: str = Field(..., description="User ID owning the alert")
    data_source_id: str = Field(..., description="Data source ID to monitor")
    type: AlertType = Field(..., description="Alert type (threshold, anomaly, etc.)")
    config: dict = Field(..., description="Alert configuration JSON")
    channels: List[str] = Field(default_factory=lambda: ["console"], description="Notification channels")
    is_active: bool = Field(default=True, description="Whether the alert is active")

class AlertResponse(BaseModel):
    id: str
    user_id: str
    data_source_id: str
    type: AlertType
    config: dict
    channels: List[str]
    is_active: bool
    created_at: str
    updated_at: str

# CRUD endpoints
@router.post("/", response_model=AlertResponse)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(
        user_id=alert_in.user_id,
        data_source_id=alert_in.data_source_id,
        type=alert_in.type,
        config=alert_in.config,
        channels=alert_in.channels,
        is_active=alert_in.is_active,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[AlertResponse])
def list_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: str, alert_in: AlertCreate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in alert_in.dict().items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"detail": "Alert deleted"}
