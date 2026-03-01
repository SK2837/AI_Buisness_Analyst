#!/usr/bin/env python3
"""
Helper script to generate environment variables for .env file.

Run this script to generate encryption keys and other secrets.
"""

from cryptography.fernet import Fernet
import secrets


def generate_env_template():
    """Generate a .env file with all necessary keys."""
    
    # Generate encryption key
    encryption_key = Fernet.generate_key().decode()
    
    # Generate secret key for JWT
    secret_key = secrets.token_urlsafe(32)
    
    print("=" * 60)
    print("Generated Environment Variables")
    print("=" * 60)
    print()
    print("Copy these values to your .env file:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print()
    print("Keep these keys secure and never commit them to version control!")
    print("=" * 60)


if __name__ == "__main__":
    generate_env_template()
