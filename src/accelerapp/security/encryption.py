"""
Encryption utilities for sensitive data in air-gapped environments.
"""

from typing import Optional
import hashlib
import os


class Encryption:
    """Provides encryption for sensitive configuration and templates."""

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption.

        Args:
            key: Encryption key (generates random if not provided)
        """
        self.key = key or os.urandom(32)

    def hash_password(self, password: str) -> str:
        """
        Hash a password securely.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if match
        """
        return self.hash_password(password) == hashed
