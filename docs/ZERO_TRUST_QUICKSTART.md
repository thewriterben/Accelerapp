# Zero-Trust Hardware Security - Quick Start Guide

**5-Minute Guide to Getting Started**

## What is Zero-Trust Hardware Security?

Zero-trust security assumes no device is trusted by default. Every device must:
1. **Prove its identity** continuously
2. **Earn trust** through good behavior
3. **Be isolated** from other devices by default
4. **Use quantum-resistant crypto** for future-proofing

## Quick Example

```python
from accelerapp.security import ZeroTrustArchitecture, NetworkZone, Protocol

# 1. Initialize
zt = ZeroTrustArchitecture()

# 2. Onboard a device
device = zt.onboard_device(
    device_info={"mac": "00:11:22:33:44:55", "serial": "ESP32-001"},
    zone=NetworkZone.INTERNAL
)
# Device gets: cryptographic identity, certificate, fingerprint, PQ keys

# 3. Authenticate
session = zt.authenticate_and_connect(
    device['device_id'],
    device['fingerprint']
)
# Session starts with FULL trust (score: 100)

# 4. Monitor behavior
trust_info = zt.update_device_trust(
    session['session_id'],
    response_time=0.15,
    success=True
)
# Trust score adjusts based on behavior

# 5. Control communication
auth = zt.authorize_communication(
    source_device=device['device_id'],
    destination_device="other_device_id",
    protocol=Protocol.MQTT,
    port=1883,
    session_id=session['session_id']
)
# Only allowed if: trust level sufficient + network policy permits

# 6. Respond to incidents
if suspicious:
    zt.isolate_compromised_device(device['device_id'])
    # Terminates sessions, revokes identity, blocks network
```

## Core Concepts

### 1. Device Identity
Every device has a unique cryptographic identity:
- **Device ID**: Generated from hardware characteristics (MAC, serial, etc.)
- **Certificate**: PKI certificate for authentication
- **Fingerprint**: Quick identity verification
- **Post-Quantum Keys**: Kyber-768 for encryption, Dilithium-3 for signatures

### 2. Trust Scoring
Devices earn trust through behavior:
- **Start**: 100 (FULL trust)
- **Good behavior**: +0.1 per operation
- **Failed operation**: -5.0
- **Anomalous behavior**: -2.0
- **High failure rate**: -10.0

Trust Levels: UNTRUSTED (0-24) → LOW (25-49) → MEDIUM (50-69) → HIGH (70-89) → FULL (90-100)

### 3. Network Zones
Five security zones with strict communication rules:

```
PUBLIC (exposed)
   ↓ allowed
DMZ (controlled access)
   ↓ allowed
INTERNAL (standard devices)
   ↓ allowed
RESTRICTED (sensitive ops)
   ↓ allowed
CRITICAL (mission-critical)
```

Cross-zone communication requires explicit policies.

### 4. Post-Quantum Crypto
Protection against quantum computers:
- **Kyber-768**: Key encapsulation (1184-byte keys)
- **Dilithium-3**: Digital signatures
- **Quantum RNG**: High-entropy random numbers
- **Hybrid Mode**: Classical + PQ for defense-in-depth

## Common Patterns

### Pattern 1: IoT Sensor Network

```python
zt = ZeroTrustArchitecture()

# Onboard sensors
sensors = []
for i in range(10):
    sensor = zt.onboard_device(
        {"mac": f"00:11:22:33:44:{i:02x}", "type": "sensor"},
        NetworkZone.INTERNAL
    )
    sensors.append(sensor)

# Onboard controller
controller = zt.onboard_device(
    {"mac": "00:11:22:33:55:00", "type": "controller"},
    NetworkZone.CRITICAL
)

# Create policies: sensors can send data to controller
for sensor in sensors:
    zt.create_communication_policy(
        sensor['device_id'],
        controller['device_id'],
        protocols=[Protocol.MQTT],
        ports=[1883]
    )
```

### Pattern 2: Edge Computing

```python
# Edge node in DMZ
edge = zt.onboard_device(
    {"mac": "00:11:22:00:01", "role": "edge"},
    NetworkZone.DMZ
)

# Processing nodes in internal network
processors = []
for i in range(5):
    proc = zt.onboard_device(
        {"mac": f"00:11:22:00:{i+10:02x}", "role": "processor"},
        NetworkZone.INTERNAL
    )
    processors.append(proc)
    
    # Allow edge → processor communication
    zt.create_communication_policy(
        edge['device_id'],
        proc['device_id'],
        [Protocol.HTTPS],
        [443]
    )
```

### Pattern 3: Incident Response

```python
# Monitor device behavior
session_info = zt.auth_service.get_session_info(session_id)

if session_info['trust_score'] < 50:
    # Low trust - investigate
    stats = zt.auth_service.get_device_statistics(device_id)
    print(f"Failure rate: {stats['failure_rate']:.2%}")
    print(f"Suspicious activities: {stats['suspicious_activities']}")
    
    if stats['failure_rate'] > 0.3:
        # High failure rate - isolate device
        zt.isolate_compromised_device(device_id)
```

### Pattern 4: Credential Management

```python
# Regular rotation (recommended: every 90-365 days)
new_creds = zt.rotate_device_credentials(
    device_id,
    validity_days=180
)

# Update device with new credentials
device.update_credentials(
    new_creds['device_id'],
    new_creds['fingerprint']
)

# Old credentials are automatically revoked
```

## Performance Tips

1. **Session Reuse**: Keep sessions active for multiple operations
2. **Batch Policies**: Create policies during setup, not per-request
3. **Trust Monitoring**: Update trust scores periodically, not per operation
4. **Segment Planning**: Group devices logically to minimize policies

## Troubleshooting

### Device Won't Authenticate
```python
# Check identity
identity = zt.identity_manager.get_identity(device_id)
if not identity.is_valid():
    # Expired - rotate
    zt.rotate_device_credentials(device_id)

# Check revocation
if device_id in zt.identity_manager._revoked_identities:
    # Revoked - re-onboard
    new_device = zt.onboard_device(device_info, zone)
```

### Communication Blocked
```python
# Check segment
segment = zt.network_service.get_device_segment(device_id)
print(f"Device in: {segment.segment_id}, zone: {segment.zone.value}")

# Check policies
policies = zt.network_service.list_policies(device_id)
active = [p for p in policies if p.enabled]
print(f"Active policies: {len(active)}")

# Check trust
trust = zt.auth_service.get_trust_level(session_id)
if trust.value < TrustLevel.MEDIUM.value:
    print("Trust too low - investigate device behavior")
```

### Low Trust Score
```python
# Review behavior
stats = zt.auth_service.get_device_statistics(device_id)
print(f"Total requests: {stats['total_requests']}")
print(f"Failures: {stats['total_failures']}")
print(f"Failure rate: {stats['failure_rate']:.2%}")

# Review anomalies
session = zt.auth_service.get_session_info(session_id)
for activity in session['metrics']['suspicious_activities']:
    print(activity)
```

## Next Steps

1. **Read Full Documentation**: [ZERO_TRUST_ARCHITECTURE.md](ZERO_TRUST_ARCHITECTURE.md)
2. **Run Demo**: `python examples/zero_trust_demo.py`
3. **Review Tests**: `tests/test_zero_trust.py`
4. **Plan Deployment**: Consider your device zones and policies

## Best Practices

✅ **DO**:
- Start devices in lower trust zones and promote as needed
- Use micro-segmentation for critical systems
- Rotate credentials regularly (90-365 days)
- Monitor trust scores and respond to anomalies
- Use hybrid crypto for maximum protection

❌ **DON'T**:
- Place all devices in CRITICAL zone
- Allow broad communication policies
- Ignore trust score degradation
- Skip credential rotation
- Disable anomaly detection

## Support

- Documentation: `docs/ZERO_TRUST_ARCHITECTURE.md`
- Examples: `examples/zero_trust_demo.py`
- Tests: `tests/test_zero_trust.py`
- Issues: https://github.com/thewriterben/Accelerapp/issues
- Email: thewriterben@protonmail.com
