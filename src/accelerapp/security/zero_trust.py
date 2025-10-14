"""
Zero-trust hardware security architecture orchestrator.
Integrates device identity, authentication, network segmentation, and post-quantum crypto.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .device_identity import DeviceIdentityManager, DeviceIdentity
from .device_authentication import DeviceAuthenticationService, TrustLevel
from .network_segmentation import (
    NetworkSegmentationService,
    NetworkZone,
    Protocol
)
from .post_quantum_crypto import PostQuantumCrypto, HybridCryptoManager


class ZeroTrustArchitecture:
    """
    Zero-trust hardware security architecture.
    
    Implements:
    - Cryptographic device identities
    - Continuous authentication and behavioral analysis
    - Micro-segmented device networks
    - Post-quantum cryptography
    """
    
    def __init__(self):
        """Initialize zero-trust architecture."""
        self.identity_manager = DeviceIdentityManager()
        self.auth_service = DeviceAuthenticationService(self.identity_manager)
        self.network_service = NetworkSegmentationService()
        self.pq_crypto = PostQuantumCrypto()
        self.hybrid_crypto = HybridCryptoManager()
    
    def onboard_device(
        self,
        device_info: Dict[str, Any],
        zone: NetworkZone,
        segment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Onboard new device with zero-trust security.
        
        Args:
            device_info: Device hardware information
            zone: Network security zone
            segment_id: Optional segment ID (created if not provided)
            
        Returns:
            Onboarding result with identity and credentials
        """
        # Create device identity with cryptographic credentials
        identity = self.identity_manager.create_identity(
            device_info,
            validity_days=365,
            metadata=device_info
        )
        
        # Generate post-quantum keys for device
        hybrid_identity = self.hybrid_crypto.create_hybrid_identity(
            identity.device_id
        )
        
        # Create network segment if needed
        if not segment_id:
            segment_id = f"segment_{zone.value}_{identity.device_id[:8]}"
            self.network_service.create_segment(
                segment_id,
                zone,
                f"Auto-created segment for {identity.device_id}"
            )
        
        # Assign device to segment
        self.network_service.assign_device_to_segment(
            identity.device_id,
            segment_id
        )
        
        return {
            "device_id": identity.device_id,
            "fingerprint": identity.fingerprint,
            "certificate": identity.certificate,
            "segment_id": segment_id,
            "zone": zone.value,
            "hybrid_crypto": hybrid_identity,
            "onboarded_at": datetime.now().isoformat()
        }
    
    def authenticate_and_connect(
        self,
        device_id: str,
        fingerprint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate device and establish secure session.
        
        Args:
            device_id: Device identifier
            fingerprint: Device fingerprint
            metadata: Additional authentication metadata
            
        Returns:
            Session information or None if authentication fails
        """
        # Authenticate device
        session_id = self.auth_service.authenticate_device(
            device_id,
            fingerprint,
            metadata
        )
        
        if not session_id:
            return None
        
        # Get device segment information
        segment = self.network_service.get_device_segment(device_id)
        
        return {
            "session_id": session_id,
            "device_id": device_id,
            "segment": segment.segment_id if segment else None,
            "zone": segment.zone.value if segment else None,
            "trust_level": self.auth_service.get_trust_level(session_id).name,
            "authenticated_at": datetime.now().isoformat()
        }
    
    def authorize_communication(
        self,
        source_device: str,
        destination_device: str,
        protocol: Protocol,
        port: int,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Authorize communication between devices with zero-trust checks.
        
        Args:
            source_device: Source device ID
            destination_device: Destination device ID
            protocol: Communication protocol
            port: Communication port
            session_id: Active session ID for source device
            
        Returns:
            Authorization result
        """
        # Verify active session
        if not self.auth_service.verify_session(session_id):
            return {
                "allowed": False,
                "reason": "Invalid or expired session"
            }
        
        # Check trust level
        trust_level = self.auth_service.get_trust_level(session_id)
        if trust_level == TrustLevel.UNTRUSTED:
            return {
                "allowed": False,
                "reason": "Device trust level too low"
            }
        
        # Check network segmentation policies
        allowed = self.network_service.check_communication_allowed(
            source_device,
            destination_device,
            protocol,
            port
        )
        
        if not allowed:
            return {
                "allowed": False,
                "reason": "Network policy violation"
            }
        
        return {
            "allowed": True,
            "trust_level": trust_level.name,
            "authorized_at": datetime.now().isoformat()
        }
    
    def update_device_trust(
        self,
        session_id: str,
        response_time: float,
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Update device trust score based on behavior.
        
        Args:
            session_id: Active session ID
            response_time: Operation response time
            success: Whether operation succeeded
            
        Returns:
            Updated trust information
        """
        trust_score = self.auth_service.update_trust_score(
            session_id,
            response_time,
            success
        )
        
        trust_level = self.auth_service.get_trust_level(session_id)
        
        return {
            "trust_score": trust_score,
            "trust_level": trust_level.name,
            "updated_at": datetime.now().isoformat()
        }
    
    def create_communication_policy(
        self,
        source_device: str,
        destination_device: str,
        protocols: List[Protocol],
        ports: List[int]
    ) -> str:
        """
        Create communication policy between devices.
        
        Args:
            source_device: Source device ID
            destination_device: Destination device ID
            protocols: Allowed protocols
            ports: Allowed ports
            
        Returns:
            Policy ID
        """
        policy_id = f"policy_{source_device[:8]}_{destination_device[:8]}"
        
        self.network_service.create_policy(
            policy_id,
            source_device,
            destination_device,
            protocols,
            ports
        )
        
        return policy_id
    
    def isolate_compromised_device(self, device_id: str) -> Dict[str, Any]:
        """
        Isolate potentially compromised device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Isolation result
        """
        # Terminate all active sessions - collect session IDs first to avoid dict size change
        sessions_to_terminate = [
            session.session_id 
            for session in self.auth_service._sessions.values()
            if session.device_id == device_id
        ]
        
        for session_id in sessions_to_terminate:
            self.auth_service.terminate_session(session_id)
        
        # Revoke device identity
        self.identity_manager.revoke_identity(device_id)
        
        # Isolate from network
        self.network_service.isolate_device(device_id)
        
        return {
            "device_id": device_id,
            "isolated": True,
            "sessions_terminated": len(sessions_to_terminate),
            "identity_revoked": True,
            "network_isolated": True,
            "isolated_at": datetime.now().isoformat()
        }
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get comprehensive device security status.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device status information
        """
        # Get identity
        identity = self.identity_manager.get_identity(device_id)
        
        # Get segment
        segment = self.network_service.get_device_segment(device_id)
        
        # Get behavioral statistics
        behavior_stats = self.auth_service.get_device_statistics(device_id)
        
        return {
            "device_id": device_id,
            "identity_valid": identity.is_valid() if identity else False,
            "segment": segment.segment_id if segment else None,
            "zone": segment.zone.value if segment else None,
            "behavioral_stats": behavior_stats,
            "checked_at": datetime.now().isoformat()
        }
    
    def get_architecture_statistics(self) -> Dict[str, Any]:
        """
        Get zero-trust architecture statistics.
        
        Returns:
            Comprehensive statistics
        """
        return {
            "identity_management": self.identity_manager.get_statistics(),
            "network_segmentation": self.network_service.get_statistics(),
            "post_quantum_crypto": self.pq_crypto.get_statistics(),
            "hybrid_crypto": self.hybrid_crypto.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def rotate_device_credentials(
        self,
        device_id: str,
        validity_days: int = 365
    ) -> Optional[Dict[str, Any]]:
        """
        Rotate device cryptographic credentials.
        
        Args:
            device_id: Device identifier
            validity_days: New credential validity period
            
        Returns:
            New credentials or None
        """
        # Rotate identity
        new_identity = self.identity_manager.rotate_identity(
            device_id,
            validity_days
        )
        
        if not new_identity:
            return None
        
        # Generate new hybrid keys
        hybrid_identity = self.hybrid_crypto.create_hybrid_identity(
            new_identity.device_id
        )
        
        return {
            "device_id": new_identity.device_id,
            "fingerprint": new_identity.fingerprint,
            "certificate": new_identity.certificate,
            "hybrid_crypto": hybrid_identity,
            "rotated_at": datetime.now().isoformat()
        }
