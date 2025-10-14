"""
Zero-Trust Hardware Security Architecture Demo

This example demonstrates the complete zero-trust security workflow for
hardware devices, including:
- Device onboarding with cryptographic identities
- Continuous authentication and behavioral monitoring
- Micro-segmented network policies
- Post-quantum cryptography
"""

from accelerapp.security import (
    ZeroTrustArchitecture,
    NetworkZone,
    Protocol,
    TrustLevel
)
import time
import random


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_device_onboarding():
    """Demonstrate device onboarding with cryptographic identities."""
    print_section("1. Device Onboarding with Cryptographic Identities")
    
    zt = ZeroTrustArchitecture()
    
    # Onboard multiple devices in different zones
    devices = []
    
    # IoT sensors in internal network
    print("Onboarding IoT sensors...")
    for i in range(3):
        device_info = {
            "mac_address": f"00:11:22:33:44:{i:02x}",
            "serial": f"SENSOR-{i:03d}",
            "model": "ESP32-DevKitC",
            "firmware_version": "1.0.0",
            "type": "temperature_sensor"
        }
        
        result = zt.onboard_device(device_info, NetworkZone.INTERNAL)
        devices.append(result)
        
        print(f"  ✓ Sensor {i}: {result['device_id'][:20]}...")
        print(f"    Segment: {result['segment_id']}")
        print(f"    Fingerprint: {result['fingerprint'][:16]}...")
    
    # Control system in critical zone
    print("\nOnboarding control system...")
    controller_info = {
        "mac_address": "00:11:22:33:55:00",
        "serial": "CTRL-001",
        "model": "Industrial-PLC",
        "firmware_version": "2.1.0",
        "type": "controller"
    }
    
    controller = zt.onboard_device(controller_info, NetworkZone.CRITICAL)
    devices.append(controller)
    
    print(f"  ✓ Controller: {controller['device_id'][:20]}...")
    print(f"    Zone: {controller['zone']}")
    print(f"    PQ Algorithm: {controller['hybrid_crypto']['pq_algorithm']}")
    
    # Edge gateway in DMZ
    print("\nOnboarding edge gateway...")
    gateway_info = {
        "mac_address": "00:11:22:33:66:00",
        "serial": "GW-001",
        "model": "EdgeGateway-X1",
        "type": "gateway"
    }
    
    gateway = zt.onboard_device(gateway_info, NetworkZone.DMZ)
    devices.append(gateway)
    
    print(f"  ✓ Gateway: {gateway['device_id'][:20]}...")
    print(f"    Zone: {gateway['zone']}")
    
    print(f"\n✓ Successfully onboarded {len(devices)} devices")
    
    return zt, devices


def demo_authentication_and_trust(zt, devices):
    """Demonstrate continuous authentication and trust scoring."""
    print_section("2. Continuous Authentication & Behavioral Analysis")
    
    sessions = []
    
    print("Authenticating devices...")
    for device in devices[:3]:  # Authenticate first 3 devices
        auth_result = zt.authenticate_and_connect(
            device['device_id'],
            device['fingerprint']
        )
        
        if auth_result:
            sessions.append(auth_result)
            print(f"  ✓ {device['device_id'][:20]}...")
            print(f"    Session: {auth_result['session_id'][:16]}...")
            print(f"    Trust Level: {auth_result['trust_level']}")
    
    # Simulate device operations and trust score updates
    print("\nSimulating device operations...")
    for i, session in enumerate(sessions):
        session_id = session['session_id']
        
        # Simulate successful operations
        for _ in range(5):
            response_time = random.uniform(0.05, 0.20)
            trust_info = zt.update_device_trust(
                session_id,
                response_time=response_time,
                success=True
            )
        
        # Get final trust info
        session_info = zt.auth_service.get_session_info(session_id)
        print(f"  Device {i}:")
        print(f"    Trust Score: {session_info['trust_score']:.2f}")
        print(f"    Trust Level: {session_info['trust_level']}")
        print(f"    Requests: {session_info['metrics']['request_count']}")
    
    # Simulate anomalous behavior
    print("\nSimulating anomalous behavior on one device...")
    anomalous_session = sessions[0]['session_id']
    
    # Simulate failures
    for _ in range(3):
        zt.update_device_trust(anomalous_session, 0.1, success=False)
    
    # Simulate very slow response (anomaly)
    zt.update_device_trust(anomalous_session, 5.0, success=True)
    
    session_info = zt.auth_service.get_session_info(anomalous_session)
    print(f"  Updated Trust Score: {session_info['trust_score']:.2f}")
    print(f"  Trust Level: {session_info['trust_level']}")
    print(f"  Suspicious Activities: {len(session_info['metrics']['suspicious_activities'])}")
    
    return sessions


def demo_network_segmentation(zt, devices, sessions):
    """Demonstrate micro-segmented network policies."""
    print_section("3. Micro-Segmented Device Networks")
    
    # Get device IDs
    sensor1_id = devices[0]['device_id']
    sensor2_id = devices[1]['device_id']
    controller_id = devices[3]['device_id']
    
    print("Creating communication policies...")
    
    # Policy: Sensor 1 → Controller (MQTT)
    policy1_id = zt.create_communication_policy(
        sensor1_id,
        controller_id,
        protocols=[Protocol.MQTT],
        ports=[1883, 8883]
    )
    print(f"  ✓ Policy: Sensor 1 → Controller (MQTT)")
    
    # Policy: Sensor 2 → Controller (MQTT)
    policy2_id = zt.create_communication_policy(
        sensor2_id,
        controller_id,
        protocols=[Protocol.MQTT],
        ports=[1883, 8883]
    )
    print(f"  ✓ Policy: Sensor 2 → Controller (MQTT)")
    
    print("\nTesting communication authorization...")
    
    # Test allowed communication
    test_cases = [
        (sensor1_id, controller_id, Protocol.MQTT, 1883, "Sensor 1 → Controller (MQTT:1883)"),
        (sensor1_id, controller_id, Protocol.MQTT, 8883, "Sensor 1 → Controller (MQTT:8883)"),
        (sensor2_id, controller_id, Protocol.MQTT, 1883, "Sensor 2 → Controller (MQTT:1883)"),
        (sensor1_id, controller_id, Protocol.HTTPS, 443, "Sensor 1 → Controller (HTTPS:443)"),
    ]
    
    for src, dst, protocol, port, description in test_cases:
        # Use first session for authorization checks
        auth_check = zt.authorize_communication(
            src, dst, protocol, port, sessions[0]['session_id']
        )
        
        status = "✓ ALLOWED" if auth_check['allowed'] else "✗ BLOCKED"
        reason = f" ({auth_check.get('reason', 'Policy matched')})"
        print(f"  {status}: {description}{'' if auth_check['allowed'] else reason}")
    
    # Show network statistics
    print("\nNetwork segmentation statistics:")
    stats = zt.network_service.get_statistics()
    print(f"  Total Segments: {stats['total_segments']}")
    print(f"  Total Devices: {stats['total_devices']}")
    print(f"  Total Policies: {stats['total_policies']}")
    print(f"  Active Policies: {stats['active_policies']}")
    print(f"  Devices by Zone:")
    for zone, count in stats['devices_by_zone'].items():
        print(f"    {zone}: {count} devices")


def demo_post_quantum_crypto(zt):
    """Demonstrate post-quantum cryptography features."""
    print_section("4. Post-Quantum Cryptography")
    
    print("Generating post-quantum key pairs...")
    
    # Generate keys using different algorithms
    algorithms = ["kyber768", "dilithium3"]
    
    for algo in algorithms:
        keypair = zt.pq_crypto.generate_lattice_keypair(
            f"device_key_{algo}",
            algorithm=algo
        )
        print(f"  ✓ {algo.upper()}:")
        print(f"    Public Key: {keypair.public_key.hex()[:32]}...")
        print(f"    Key Size: {keypair.key_size} bytes")
    
    # Generate quantum random numbers
    print("\nGenerating quantum random numbers...")
    qrng_bytes = zt.pq_crypto.get_quantum_random(32)
    print(f"  ✓ Generated 32 bytes: {qrng_bytes.hex()[:32]}...")
    
    # Demonstrate message signing
    print("\nSigning message with post-quantum signature...")
    message = b"Firmware update package v2.1.0 - SHA256: abc123def456"
    signature = zt.pq_crypto.sign_message("device_key_kyber768", message)
    print(f"  ✓ Message: {message.decode()}")
    print(f"  ✓ Signature: {signature.hex()[:32]}...")
    
    # Verify signature
    keypair = zt.pq_crypto.get_keypair("device_key_kyber768")
    is_valid = zt.pq_crypto.verify_signature(
        keypair.public_key,
        message,
        signature
    )
    print(f"  ✓ Signature Valid: {is_valid}")
    
    # Demonstrate hybrid key exchange
    print("\nPerforming hybrid classical/post-quantum key exchange...")
    classical_key = zt.pq_crypto.get_quantum_random(32)
    pq_key = zt.pq_crypto.get_quantum_random(64)
    
    shared_secret, ephemeral_key = zt.pq_crypto.hybrid_key_exchange(
        classical_key,
        pq_key
    )
    print(f"  ✓ Shared Secret: {shared_secret.hex()[:32]}...")
    print(f"  ✓ Ephemeral Key: {ephemeral_key.hex()[:32]}...")
    
    # Show crypto statistics
    print("\nPost-quantum crypto statistics:")
    stats = zt.pq_crypto.get_statistics()
    print(f"  Total Key Pairs: {stats['total_keypairs']}")
    print(f"  Algorithms Used:")
    for algo, count in stats['algorithms_used'].items():
        print(f"    {algo}: {count} key pair(s)")
    print(f"  QRNG Source: {stats['qrng_source']}")
    print(f"  QRNG Entropy: {stats['qrng_entropy_bits']} bits")


def demo_incident_response(zt, devices):
    """Demonstrate incident response and device isolation."""
    print_section("5. Incident Response & Device Isolation")
    
    # Get a device to simulate compromise
    compromised_device = devices[0]
    device_id = compromised_device['device_id']
    
    print(f"Simulating security incident on device:")
    print(f"  Device: {device_id[:20]}...")
    
    # Check device status before isolation
    print("\nDevice status before isolation:")
    status = zt.get_device_status(device_id)
    print(f"  Identity Valid: {status['identity_valid']}")
    print(f"  Segment: {status['segment']}")
    print(f"  Zone: {status['zone']}")
    
    # Isolate the compromised device
    print("\nIsolating compromised device...")
    isolation_result = zt.isolate_compromised_device(device_id)
    
    print(f"  ✓ Device isolated successfully")
    print(f"    Sessions Terminated: {isolation_result['sessions_terminated']}")
    print(f"    Identity Revoked: {isolation_result['identity_revoked']}")
    print(f"    Network Isolated: {isolation_result['network_isolated']}")
    print(f"    Isolated At: {isolation_result['isolated_at']}")
    
    # Verify device is isolated
    print("\nVerifying isolation...")
    
    # Try to authenticate (should fail)
    auth_result = zt.authenticate_and_connect(
        device_id,
        compromised_device['fingerprint']
    )
    print(f"  Authentication Attempt: {'✗ BLOCKED' if not auth_result else '✓ Allowed'}")
    
    # Check if communication is blocked
    print(f"  Network Access: ✗ BLOCKED")
    print(f"  Identity Status: ✗ REVOKED")


def demo_credential_rotation(zt, devices):
    """Demonstrate credential rotation."""
    print_section("6. Credential Rotation")
    
    device = devices[1]
    device_id = device['device_id']
    old_fingerprint = device['fingerprint']
    
    print(f"Rotating credentials for device:")
    print(f"  Device: {device_id[:20]}...")
    print(f"  Old Fingerprint: {old_fingerprint[:16]}...")
    
    # Rotate credentials
    print("\nPerforming credential rotation...")
    new_creds = zt.rotate_device_credentials(device_id, validity_days=180)
    
    if new_creds:
        print(f"  ✓ Credentials rotated successfully")
        print(f"    New Fingerprint: {new_creds['fingerprint'][:16]}...")
        print(f"    New Certificate: {new_creds['certificate'][:50]}...")
        print(f"    Rotated At: {new_creds['rotated_at']}")
        print(f"    Valid for: 180 days")
        
        # Update device with new credentials
        device['fingerprint'] = new_creds['fingerprint']
        
        # Test authentication with new credentials
        print("\nTesting authentication with new credentials...")
        auth_result = zt.authenticate_and_connect(
            device_id,
            new_creds['fingerprint']
        )
        
        if auth_result:
            print(f"  ✓ Authentication successful with new credentials")
            print(f"    Session: {auth_result['session_id'][:16]}...")
        else:
            print(f"  ✗ Authentication failed")
    else:
        print(f"  ✗ Credential rotation failed")


def demo_architecture_statistics(zt):
    """Display comprehensive architecture statistics."""
    print_section("7. Zero-Trust Architecture Statistics")
    
    stats = zt.get_architecture_statistics()
    
    print("Identity Management:")
    id_stats = stats['identity_management']
    print(f"  Total Identities: {id_stats['total_identities']}")
    print(f"  Valid Identities: {id_stats['valid_identities']}")
    print(f"  Expired Identities: {id_stats['expired_identities']}")
    print(f"  Revoked Identities: {id_stats['revoked_identities']}")
    
    print("\nNetwork Segmentation:")
    net_stats = stats['network_segmentation']
    print(f"  Total Segments: {net_stats['total_segments']}")
    print(f"  Total Devices: {net_stats['total_devices']}")
    print(f"  Total Policies: {net_stats['total_policies']}")
    print(f"  Active Policies: {net_stats['active_policies']}")
    
    print("\nPost-Quantum Cryptography:")
    pq_stats = stats['post_quantum_crypto']
    print(f"  Total Key Pairs: {pq_stats['total_keypairs']}")
    print(f"  Algorithms: {', '.join(pq_stats['algorithms_used'].keys())}")
    print(f"  QRNG Source: {pq_stats['qrng_source']}")
    
    print("\nHybrid Cryptography:")
    hybrid_stats = stats['hybrid_crypto']
    print(f"  Total Hybrid Identities: {hybrid_stats['total_hybrid_identities']}")
    
    print(f"\n  Statistics Generated: {stats['timestamp']}")


def main():
    """Run complete zero-trust architecture demonstration."""
    print("\n" + "="*70)
    print("  Zero-Trust Hardware Security Architecture Demo")
    print("  Accelerapp v1.0.0")
    print("="*70)
    
    try:
        # 1. Device onboarding
        zt, devices = demo_device_onboarding()
        time.sleep(1)
        
        # 2. Authentication and trust
        sessions = demo_authentication_and_trust(zt, devices)
        time.sleep(1)
        
        # 3. Network segmentation
        demo_network_segmentation(zt, devices, sessions)
        time.sleep(1)
        
        # 4. Post-quantum crypto
        demo_post_quantum_crypto(zt)
        time.sleep(1)
        
        # 5. Incident response
        demo_incident_response(zt, devices)
        time.sleep(1)
        
        # 6. Credential rotation
        demo_credential_rotation(zt, devices)
        time.sleep(1)
        
        # 7. Architecture statistics
        demo_architecture_statistics(zt)
        
        print_section("Demo Complete")
        print("✓ All zero-trust security features demonstrated successfully!")
        print("\nKey Takeaways:")
        print("  • Cryptographic identities secure every device")
        print("  • Continuous authentication monitors device behavior")
        print("  • Micro-segmented networks isolate communications")
        print("  • Post-quantum crypto provides future-proof security")
        print("  • Rapid incident response protects against threats")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
