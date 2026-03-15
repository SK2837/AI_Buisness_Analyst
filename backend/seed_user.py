"""
Creates a default admin user in the database.
Run from the backend/ directory with venv active:
    python seed_user.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models import registry  # noqa: F401 - loads all models
from app.models.database import SessionLocal
from app.models.user import User, UserRole
import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@example.com").first()
if existing:
    print(f"User already exists: {existing.email} (id={existing.id})")
else:
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created admin user:")
    print(f"  Email:    admin@example.com")
    print(f"  Password: admin123")
    print(f"  User ID:  {user.id}")

db.close()
