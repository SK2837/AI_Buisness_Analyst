"""
Encryption utilities for securing sensitive data like data source credentials.

Uses Fernet symmetric encryption from the cryptography library.
"""

from cryptography.fernet import Fernet
from app.core.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        """Initialize encryption service with key from settings."""
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string
            
        Example:
            >>> enc = EncryptionService()
            >>> encrypted = enc.encrypt("my_password")
            >>> print(encrypted)
            'gAAAAABh...'
        """
        if not plaintext:
            return ""
        
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
            
        Example:
            >>> enc = EncryptionService()
            >>> decrypted = enc.decrypt('gAAAAABh...')
            >>> print(decrypted)
            'my_password'
        """
        if not encrypted_text:
            return ""
        
        decrypted_bytes = self.cipher.decrypt(encrypted_text.encode())
        return decrypted_bytes.decode()

    # Backward-compatible helper used by data executor
    def decrypt_credentials(self, encrypted_text: str) -> str:
        """Decrypt stored credentials payload."""
        return self.decrypt(encrypted_text)


# Global encryption service instance
encryption_service = EncryptionService()


def encrypt_credentials(credentials: dict) -> str:
    """
    Encrypt a credentials dictionary to store in database.
    
    Args:
        credentials: Dict with connection details (host, port, user, password, etc.)
        
    Returns:
        Encrypted JSON string
        
    Example:
        >>> creds = {"host": "db.example.com", "password": "secret"}
        >>> encrypted = encrypt_credentials(creds)
    """
    import json
    plaintext = json.dumps(credentials)
    return encryption_service.encrypt(plaintext)


def decrypt_credentials(encrypted_text: str) -> dict:
    """
    Decrypt credentials from database storage.
    
    Args:
        encrypted_text: Encrypted JSON string
        
    Returns:
        Dict with decrypted connection details
        
    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
        json.JSONDecodeError: If decrypted text is not valid JSON
        
    Example:
        >>> creds = decrypt_credentials(encrypted)
        >>> print(creds["password"])
        'secret'
    """
    import json
    plaintext = encryption_service.decrypt(encrypted_text)
    return json.loads(plaintext)


def generate_encryption_key() -> str:
    """
    Generate a new encryption key for use in .env file.
    
    Returns:
        Base64-encoded Fernet key
        
    Example:
        >>> key = generate_encryption_key()
        >>> print(f"ENCRYPTION_KEY={key}")
        ENCRYPTION_KEY=abcd1234...
    """
    return Fernet.generate_key().decode()
