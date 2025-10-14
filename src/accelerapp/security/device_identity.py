"""
Device identity management for zero-trust architecture.
Provides cryptographic identities for hardware devices.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import secrets
import json


@dataclass
class DeviceIdentity:
    """Cryptographic identity for a hardware device."""
    
    device_id: str
    public_key: str
    certificate: str
    created_at: datetime
    expires_at: datetime
    fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if identity is still valid."""
        return datetime.now() < self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "device_id": self.device_id,
            "public_key": self.public_key,
            "certificate": self.certificate,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "fingerprint": self.fingerprint,
            "metadata": self.metadata
        }


class DeviceIdentityManager:
    """Manages cryptographic identities for hardware devices."""
    
    def __init__(self):
        """Initialize device identity manager."""
        self._identities: Dict[str, DeviceIdentity] = {}
        self._revoked_identities: set = set()
    
    def generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """
        Generate unique device identifier based on hardware characteristics.
        
        Args:
            device_info: Hardware characteristics (MAC, serial, etc.)
            
        Returns:
            Unique device identifier
        """
        # Create deterministic ID from hardware characteristics
        characteristics = []
        for key in sorted(device_info.keys()):
            characteristics.append(f"{key}:{device_info[key]}")
        
        combined = "|".join(characteristics)
        device_hash = hashlib.sha256(combined.encode()).hexdigest()
        return f"device-{device_hash[:16]}"
    
    def generate_fingerprint(self, device_id: str, public_key: str) -> str:
        """
        Generate device fingerprint for quick verification.
        
        Args:
            device_id: Device identifier
            public_key: Device public key
            
        Returns:
            Device fingerprint
        """
        combined = f"{device_id}:{public_key}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def create_identity(
        self,
        device_info: Dict[str, Any],
        validity_days: int = 365,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeviceIdentity:
        """
        Create cryptographic identity for a device.
        
        Args:
            device_info: Hardware device information
            validity_days: Certificate validity period
            metadata: Additional device metadata
            
        Returns:
            Device identity
        """
        device_id = self.generate_device_id(device_info)
        
        # Generate key pair (simplified - in production use proper crypto library)
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        # Generate certificate
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=validity_days)
        
        cert_data = {
            "device_id": device_id,
            "public_key": public_key,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "issuer": "Accelerapp-CA",
            "version": "1.0"
        }
        certificate = json.dumps(cert_data)
        
        # Generate fingerprint
        fingerprint = self.generate_fingerprint(device_id, public_key)
        
        identity = DeviceIdentity(
            device_id=device_id,
            public_key=public_key,
            certificate=certificate,
            created_at=created_at,
            expires_at=expires_at,
            fingerprint=fingerprint,
            metadata=metadata or {}
        )
        
        self._identities[device_id] = identity
        return identity
    
    def get_identity(self, device_id: str) -> Optional[DeviceIdentity]:
        """
        Get device identity by ID.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device identity or None
        """
        return self._identities.get(device_id)
    
    def verify_identity(self, device_id: str, fingerprint: str) -> bool:
        """
        Verify device identity.
        
        Args:
            device_id: Device identifier
            fingerprint: Device fingerprint to verify
            
        Returns:
            True if identity is valid
        """
        identity = self._identities.get(device_id)
        if not identity:
            return False
        
        if device_id in self._revoked_identities:
            return False
        
        if not identity.is_valid():
            return False
        
        return identity.fingerprint == fingerprint
    
    def revoke_identity(self, device_id: str) -> bool:
        """
        Revoke device identity.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if revoked successfully
        """
        if device_id in self._identities:
            self._revoked_identities.add(device_id)
            return True
        return False
    
    def rotate_identity(
        self,
        device_id: str,
        validity_days: int = 365
    ) -> Optional[DeviceIdentity]:
        """
        Rotate device identity (certificate renewal).
        
        Args:
            device_id: Device identifier
            validity_days: New certificate validity period
            
        Returns:
            New device identity or None
        """
        old_identity = self._identities.get(device_id)
        if not old_identity:
            return None
        
        # Create new identity with same device info
        device_info = old_identity.metadata
        new_identity = self.create_identity(
            device_info,
            validity_days,
            old_identity.metadata
        )
        
        # Revoke old identity
        self._revoked_identities.add(device_id)
        
        return new_identity
    
    def list_identities(self, include_expired: bool = False) -> List[DeviceIdentity]:
        """
        List all device identities.
        
        Args:
            include_expired: Include expired identities
            
        Returns:
            List of device identities
        """
        identities = []
        for identity in self._identities.values():
            if include_expired or identity.is_valid():
                if identity.device_id not in self._revoked_identities:
                    identities.append(identity)
        return identities
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get identity management statistics.
        
        Returns:
            Statistics dictionary
        """
        total = len(self._identities)
        valid = sum(1 for i in self._identities.values() if i.is_valid())
        expired = total - valid
        revoked = len(self._revoked_identities)
        
        return {
            "total_identities": total,
            "valid_identities": valid,
            "expired_identities": expired,
            "revoked_identities": revoked
        }
