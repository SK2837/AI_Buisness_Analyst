"""
Script to re-encrypt the data source credentials with the current encryption key.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/adarshkasula/Documents/New project/ai-business-analyst/backend')

from app.utils.encryption import encrypt_credentials
from sqlalchemy import create_engine, text
from app.core.config import settings
import json

# Database path
db_url = str(settings.DATABASE_URL)
engine = create_engine(db_url)

# Original unencrypted connection config
original_config = {
    "path": "/Users/adarshkasula/Documents/New project/ai-business-analyst/data/demo_analytics.sqlite"
}

# Encrypt with current key
encrypted_text = encrypt_credentials(original_config)

# New connection config
new_config = {
    "encrypted": encrypted_text
}

# Update the data source
data_source_id = "b0d23d4d-9573-432e-b452-d12524c685b8"

with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE data_sources SET connection_config = :config WHERE id = :id"),
        {"config": json.dumps(new_config), "id": data_source_id}
    )
    conn.commit()
    
print(f"Successfully re-encrypted credentials for data source {data_source_id}")
print(f"Rows updated: {result.rowcount}")
