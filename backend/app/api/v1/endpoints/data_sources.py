from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json

from app.models.database import get_db
from app.models.data_source import DataSource, SourceType
from app.utils.encryption import encrypt_credentials
from app.models.user import User

router = APIRouter()

# Pydantic Schemas
class DataSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: SourceType
    connection_config: Dict[str, Any]  # Plaintext credentials from client
    refresh_schedule: Optional[str] = None
    user_id: str = "00000000-0000-0000-0000-000000000000"  # Placeholder until auth

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    refresh_schedule: Optional[str] = None

class DataSourceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    source_type: SourceType
    is_active: bool
    last_connected_at: Optional[str]
    last_refreshed_at: Optional[str]
    created_at: str
    
    # We deliberately exclude connection_config for security

# Endpoints

@router.post("/", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source(ds_in: DataSourceCreate, db: Session = Depends(get_db)):
    """
    Create a new data source.
    Connection credentials will be encrypted before storage.
    """
    # Check if name exists
    existing = db.query(DataSource).filter(DataSource.name == ds_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Data source with this name already exists")

    # Encrypt configuration
    # We wrap the config in a structure that indicates it's encrypted
    # The model expects JSONB. We'll store: {"encrypted": "base64_string"}
    encrypted_config_str = encrypt_credentials(ds_in.connection_config)
    stored_config = {"encrypted": encrypted_config_str}

    db_ds = DataSource(
        name=ds_in.name,
        description=ds_in.description,
        source_type=ds_in.source_type,
        connection_config=stored_config,
        refresh_schedule=ds_in.refresh_schedule,
        created_by=ds_in.user_id
    )
    
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    
    return _format_response(db_ds)

@router.get("/", response_model=List[DataSourceResponse])
def list_data_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all data sources."""
    data_sources = db.query(DataSource).offset(skip).limit(limit).all()
    return [_format_response(ds) for ds in data_sources]

@router.get("/{ds_id}", response_model=DataSourceResponse)
def get_data_source(ds_id: str, db: Session = Depends(get_db)):
    """Get a specific data source."""
    ds = db.query(DataSource).filter(DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")
    return _format_response(ds)

@router.put("/{ds_id}", response_model=DataSourceResponse)
def update_data_source(ds_id: str, ds_in: DataSourceUpdate, db: Session = Depends(get_db)):
    """Update a data source."""
    ds = db.query(DataSource).filter(DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    if ds_in.name:
        # Check uniqueness if name changing
        if ds_in.name != ds.name:
            existing = db.query(DataSource).filter(DataSource.name == ds_in.name).first()
            if existing:
                raise HTTPException(status_code=400, detail="Data source with this name already exists")
        ds.name = ds_in.name
        
    if ds_in.description is not None:
        ds.description = ds_in.description
        
    if ds_in.is_active is not None:
        ds.is_active = ds_in.is_active
        
    if ds_in.refresh_schedule is not None:
        ds.refresh_schedule = ds_in.refresh_schedule
        
    if ds_in.connection_config:
        encrypted_config_str = encrypt_credentials(ds_in.connection_config)
        ds.connection_config = {"encrypted": encrypted_config_str}
        
    db.commit()
    db.refresh(ds)
    return _format_response(ds)

@router.delete("/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_source(ds_id: str, db: Session = Depends(get_db)):
    """Delete a data source."""
    ds = db.query(DataSource).filter(DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    db.delete(ds)
    db.commit()
    return None

def _format_response(ds: DataSource) -> DataSourceResponse:
    return DataSourceResponse(
        id=str(ds.id),
        name=ds.name,
        description=ds.description,
        source_type=ds.source_type,
        is_active=ds.is_active,
        last_connected_at=str(ds.last_connected_at) if ds.last_connected_at else None,
        last_refreshed_at=str(ds.last_refreshed_at) if ds.last_refreshed_at else None,
        created_at=str(ds.created_at)
    )
