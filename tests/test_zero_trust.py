"""
Tests for zero-trust hardware security architecture.
"""

import pytest
from datetime import datetime, timedelta
from accelerapp.security import (
    ZeroTrustArchitecture,
    DeviceIdentityManager,
    DeviceAuthenticationService,
    NetworkSegmentationService,
    NetworkZone,
    Protocol,
    TrustLevel,
    PostQuantumCrypto,
    HybridCryptoManager
)


class TestDeviceIdentity:
    """Tests for device identity management."""
    
    def test_identity_manager_initialization(self):
        """Test identity manager initialization."""
        manager = DeviceIdentityManager()
        assert manager is not None
        stats = manager.get_statistics()
        assert stats["total_identities"] == 0
    
    def test_generate_device_id(self):
        """Test device ID generation."""
        manager = DeviceIdentityManager()
        device_info = {
            "mac_address": "00:11:22:33:44:55",
            "serial": "ABC123",
            "model": "ESP32"
        }
        device_id = manager.generate_device_id(device_info)
        assert device_id.startswith("device-")
        assert len(device_id) > 10
        
        # Same info should generate same ID
        device_id2 = manager.generate_device_id(device_info)
        assert device_id == device_id2
    
    def test_create_identity(self):
        """Test creating device identity."""
        manager = DeviceIdentityManager()
        device_info = {
            "mac_address": "00:11:22:33:44:55",
            "serial": "ABC123"
        }
        
        identity = manager.create_identity(device_info, validity_days=365)
        
        assert identity.device_id.startswith("device-")
        assert identity.public_key is not None
        assert identity.certificate is not None
        assert identity.fingerprint is not None
        assert identity.is_valid()
    
    def test_verify_identity(self):
        """Test identity verification."""
        manager = DeviceIdentityManager()
        device_info = {"mac": "00:11:22:33:44:55"}
        
        identity = manager.create_identity(device_info)
        
        # Valid identity should verify
        assert manager.verify_identity(identity.device_id, identity.fingerprint)
        
        # Invalid fingerprint should fail
        assert not manager.verify_identity(identity.device_id, "invalid_fingerprint")
    
    def test_revoke_identity(self):
        """Test identity revocation."""
        manager = DeviceIdentityManager()
        device_info = {"mac": "00:11:22:33:44:55"}
        
        identity = manager.create_identity(device_info)
        
        # Initially valid
        assert manager.verify_identity(identity.device_id, identity.fingerprint)
        
        # Revoke identity
        assert manager.revoke_identity(identity.device_id)
        
        # Should no longer verify
        assert not manager.verify_identity(identity.device_id, identity.fingerprint)
    
    def test_rotate_identity(self):
        """Test identity rotation."""
        manager = DeviceIdentityManager()
        device_info = {"mac": "00:11:22:33:44:55"}
        
        old_identity = manager.create_identity(device_info)
        old_fingerprint = old_identity.fingerprint
        
        # Rotate identity
        new_identity = manager.rotate_identity(old_identity.device_id)
        
        assert new_identity is not None
        assert new_identity.fingerprint != old_fingerprint
        
        # Old fingerprint should not verify
        assert not manager.verify_identity(old_identity.device_id, old_fingerprint)


class TestDeviceAuthentication:
    """Tests for device authentication and behavioral analysis."""
    
    def test_authentication_service_initialization(self):
        """Test authentication service initialization."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        assert auth_service is not None
    
    def test_authenticate_device(self):
        """Test device authentication."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        
        device_info = {"mac": "00:11:22:33:44:55"}
        identity = identity_manager.create_identity(device_info)
        
        # Authenticate device
        session_id = auth_service.authenticate_device(
            identity.device_id,
            identity.fingerprint
        )
        
        assert session_id is not None
        assert auth_service.verify_session(session_id)
    
    def test_failed_authentication(self):
        """Test failed authentication attempt."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        
        # Try to authenticate non-existent device
        session_id = auth_service.authenticate_device(
            "invalid_device",
            "invalid_fingerprint"
        )
        
        assert session_id is None
    
    def test_trust_score_updates(self):
        """Test trust score updates."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        
        device_info = {"mac": "00:11:22:33:44:55"}
        identity = identity_manager.create_identity(device_info)
        session_id = auth_service.authenticate_device(
            identity.device_id,
            identity.fingerprint
        )
        
        # Initial trust score should be 100
        session_info = auth_service.get_session_info(session_id)
        assert session_info["trust_score"] == 100.0
        
        # Update with successful operation
        trust_score = auth_service.update_trust_score(session_id, 0.1, success=True)
        assert trust_score >= 99.0  # Should stay high or increase slightly
        
        # Update with failed operation
        trust_score = auth_service.update_trust_score(session_id, 0.1, success=False)
        assert trust_score < 100.0  # Should decrease
    
    def test_trust_levels(self):
        """Test trust level categorization."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        
        device_info = {"mac": "00:11:22:33:44:55"}
        identity = identity_manager.create_identity(device_info)
        session_id = auth_service.authenticate_device(
            identity.device_id,
            identity.fingerprint
        )
        
        # Initial trust level should be FULL
        assert auth_service.get_trust_level(session_id) == TrustLevel.FULL
        
        # Degrade trust score
        for _ in range(10):
            auth_service.update_trust_score(session_id, 0.1, success=False)
        
        # Trust level should decrease
        trust_level = auth_service.get_trust_level(session_id)
        assert trust_level.value < TrustLevel.FULL.value
    
    def test_session_termination(self):
        """Test session termination."""
        identity_manager = DeviceIdentityManager()
        auth_service = DeviceAuthenticationService(identity_manager)
        
        device_info = {"mac": "00:11:22:33:44:55"}
        identity = identity_manager.create_identity(device_info)
        session_id = auth_service.authenticate_device(
            identity.device_id,
            identity.fingerprint
        )
        
        assert auth_service.verify_session(session_id)
        
        # Terminate session
        assert auth_service.terminate_session(session_id)
        
        # Session should no longer be valid
        assert not auth_service.verify_session(session_id)


class TestNetworkSegmentation:
    """Tests for network segmentation."""
    
    def test_network_service_initialization(self):
        """Test network service initialization."""
        service = NetworkSegmentationService()
        assert service is not None
        stats = service.get_statistics()
        assert stats["total_segments"] == 0
    
    def test_create_segment(self):
        """Test creating network segment."""
        service = NetworkSegmentationService()
        
        segment = service.create_segment(
            "segment1",
            NetworkZone.INTERNAL,
            "Test segment"
        )
        
        assert segment.segment_id == "segment1"
        assert segment.zone == NetworkZone.INTERNAL
    
    def test_assign_device_to_segment(self):
        """Test assigning device to segment."""
        service = NetworkSegmentationService()
        
        service.create_segment("segment1", NetworkZone.INTERNAL)
        
        assert service.assign_device_to_segment("device1", "segment1")
        
        # Verify assignment
        segment = service.get_device_segment("device1")
        assert segment.segment_id == "segment1"
    
    def test_communication_policy(self):
        """Test communication policy creation."""
        service = NetworkSegmentationService()
        
        policy = service.create_policy(
            "policy1",
            "device1",
            "device2",
            [Protocol.HTTPS],
            [443]
        )
        
        assert policy.policy_id == "policy1"
        assert Protocol.HTTPS in policy.allowed_protocols
        assert 443 in policy.allowed_ports
    
    def test_same_segment_communication(self):
        """Test communication within same segment."""
        service = NetworkSegmentationService()
        
        # Create segment and assign devices
        service.create_segment("segment1", NetworkZone.INTERNAL)
        service.assign_device_to_segment("device1", "segment1")
        service.assign_device_to_segment("device2", "segment1")
        
        # Same segment communication should be allowed by default
        allowed = service.check_communication_allowed(
            "device1",
            "device2",
            Protocol.HTTPS,
            443
        )
        assert allowed
    
    def test_cross_segment_communication(self):
        """Test communication across segments."""
        service = NetworkSegmentationService()
        
        # Create segments in different zones
        service.create_segment("seg_internal", NetworkZone.INTERNAL)
        service.create_segment("seg_restricted", NetworkZone.RESTRICTED)
        
        service.assign_device_to_segment("device1", "seg_internal")
        service.assign_device_to_segment("device2", "seg_restricted")
        
        # Create explicit policy
        service.create_policy(
            "policy1",
            "device1",
            "device2",
            [Protocol.HTTPS],
            [443]
        )
        
        # Check communication is allowed
        allowed = service.check_communication_allowed(
            "device1",
            "device2",
            Protocol.HTTPS,
            443
        )
        assert allowed
    
    def test_device_isolation(self):
        """Test device isolation."""
        service = NetworkSegmentationService()
        
        service.create_segment("segment1", NetworkZone.INTERNAL)
        service.assign_device_to_segment("device1", "segment1")
        service.assign_device_to_segment("device2", "segment1")
        
        # Create policy
        service.create_policy(
            "policy1",
            "device1",
            "device2",
            [Protocol.HTTPS],
            [443]
        )
        
        # Isolate device
        assert service.isolate_device("device1")
        
        # Communication should now be blocked
        allowed = service.check_communication_allowed(
            "device1",
            "device2",
            Protocol.HTTPS,
            443
        )
        assert not allowed


class TestPostQuantumCrypto:
    """Tests for post-quantum cryptography."""
    
    def test_pq_crypto_initialization(self):
        """Test post-quantum crypto initialization."""
        pq_crypto = PostQuantumCrypto()
        assert pq_crypto is not None
        stats = pq_crypto.get_statistics()
        assert stats["total_keypairs"] == 0
    
    def test_generate_lattice_keypair(self):
        """Test lattice-based key pair generation."""
        pq_crypto = PostQuantumCrypto()
        
        keypair = pq_crypto.generate_lattice_keypair("key1", "kyber768")
        
        assert keypair.public_key is not None
        assert keypair.private_key is not None
        assert keypair.algorithm == "kyber768"
        assert keypair.key_size == 1184
    
    def test_quantum_random_generation(self):
        """Test quantum random number generation."""
        pq_crypto = PostQuantumCrypto()
        
        random_bytes = pq_crypto.get_quantum_random(32)
        
        assert len(random_bytes) == 32
        
        # Generate another set - should be different
        random_bytes2 = pq_crypto.get_quantum_random(32)
        assert random_bytes != random_bytes2
    
    def test_hybrid_key_exchange(self):
        """Test hybrid classical/post-quantum key exchange."""
        pq_crypto = PostQuantumCrypto()
        
        # Generate keys for two parties
        alice_classical = pq_crypto.get_quantum_random(32)
        alice_pq = pq_crypto.get_quantum_random(64)
        
        # Perform key exchange
        shared_secret, ephemeral_key = pq_crypto.hybrid_key_exchange(
            alice_classical,
            alice_pq
        )
        
        assert len(shared_secret) == 32  # SHA3-256 output
        assert len(ephemeral_key) == 96  # 32 + 64
    
    def test_message_signing(self):
        """Test post-quantum message signing."""
        pq_crypto = PostQuantumCrypto()
        
        keypair = pq_crypto.generate_lattice_keypair("key1")
        message = b"Test message"
        
        signature = pq_crypto.sign_message("key1", message)
        
        assert signature is not None
        assert len(signature) == 64  # SHA3-512 output
        
        # Verify signature
        assert pq_crypto.verify_signature(
            keypair.public_key,
            message,
            signature
        )
    
    def test_hybrid_crypto_manager(self):
        """Test hybrid crypto manager."""
        manager = HybridCryptoManager()
        
        identity = manager.create_hybrid_identity("identity1")
        
        assert identity["identity_id"] == "identity1"
        assert "classical_public_key" in identity
        assert "pq_public_key" in identity
        assert identity["pq_algorithm"] == "kyber768"


class TestZeroTrustArchitecture:
    """Tests for integrated zero-trust architecture."""
    
    def test_zero_trust_initialization(self):
        """Test zero-trust architecture initialization."""
        zt = ZeroTrustArchitecture()
        assert zt.identity_manager is not None
        assert zt.auth_service is not None
        assert zt.network_service is not None
        assert zt.pq_crypto is not None
    
    def test_device_onboarding(self):
        """Test device onboarding process."""
        zt = ZeroTrustArchitecture()
        
        device_info = {
            "mac_address": "00:11:22:33:44:55",
            "serial": "ABC123",
            "model": "ESP32"
        }
        
        result = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        assert "device_id" in result
        assert "fingerprint" in result
        assert "certificate" in result
        assert "segment_id" in result
        assert result["zone"] == "internal"
        assert "hybrid_crypto" in result
    
    def test_authenticate_and_connect(self):
        """Test device authentication and connection."""
        zt = ZeroTrustArchitecture()
        
        device_info = {"mac": "00:11:22:33:44:55"}
        onboard_result = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        # Authenticate device
        auth_result = zt.authenticate_and_connect(
            onboard_result["device_id"],
            onboard_result["fingerprint"]
        )
        
        assert auth_result is not None
        assert "session_id" in auth_result
        assert auth_result["trust_level"] == "FULL"
    
    def test_authorize_communication(self):
        """Test communication authorization."""
        zt = ZeroTrustArchitecture()
        
        # Onboard two devices in same segment
        device1_info = {"mac": "00:11:22:33:44:55"}
        device2_info = {"mac": "00:11:22:33:44:66"}
        
        # Use a specific segment ID to ensure devices are in same segment
        segment_id = "test_segment"
        zt.network_service.create_segment(segment_id, NetworkZone.INTERNAL)
        
        device1 = zt.onboard_device(device1_info, NetworkZone.INTERNAL, segment_id)
        device2 = zt.onboard_device(device2_info, NetworkZone.INTERNAL, segment_id)
        
        # Authenticate device 1
        auth1 = zt.authenticate_and_connect(
            device1["device_id"],
            device1["fingerprint"]
        )
        
        # Try to communicate (should be allowed in same segment)
        result = zt.authorize_communication(
            device1["device_id"],
            device2["device_id"],
            Protocol.HTTPS,
            443,
            auth1["session_id"]
        )
        
        assert result["allowed"]
    
    def test_isolate_compromised_device(self):
        """Test isolating compromised device."""
        zt = ZeroTrustArchitecture()
        
        device_info = {"mac": "00:11:22:33:44:55"}
        device = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        # Authenticate device
        zt.authenticate_and_connect(
            device["device_id"],
            device["fingerprint"]
        )
        
        # Isolate device
        result = zt.isolate_compromised_device(device["device_id"])
        
        assert result["isolated"]
        assert result["identity_revoked"]
        assert result["network_isolated"]
    
    def test_device_status(self):
        """Test getting device status."""
        zt = ZeroTrustArchitecture()
        
        device_info = {"mac": "00:11:22:33:44:55"}
        device = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        status = zt.get_device_status(device["device_id"])
        
        assert status["device_id"] == device["device_id"]
        assert status["identity_valid"]
        assert status["segment"] is not None
        assert status["zone"] == "internal"
    
    def test_architecture_statistics(self):
        """Test getting architecture statistics."""
        zt = ZeroTrustArchitecture()
        
        # Onboard a device
        device_info = {"mac": "00:11:22:33:44:55"}
        zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        stats = zt.get_architecture_statistics()
        
        assert "identity_management" in stats
        assert "network_segmentation" in stats
        assert "post_quantum_crypto" in stats
        assert stats["identity_management"]["total_identities"] >= 1
    
    def test_credential_rotation(self):
        """Test rotating device credentials."""
        zt = ZeroTrustArchitecture()
        
        device_info = {"mac": "00:11:22:33:44:55"}
        device = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        
        old_fingerprint = device["fingerprint"]
        
        # Rotate credentials
        new_creds = zt.rotate_device_credentials(device["device_id"])
        
        assert new_creds is not None
        assert new_creds["fingerprint"] != old_fingerprint
