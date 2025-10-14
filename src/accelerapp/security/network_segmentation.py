"""
Micro-segmented device networks for zero-trust architecture.
Provides network isolation and communication policies.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class NetworkZone(Enum):
    """Network security zones."""
    PUBLIC = "public"
    DMZ = "dmz"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CRITICAL = "critical"


class Protocol(Enum):
    """Supported communication protocols."""
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"
    MQTT = "mqtt"
    COAP = "coap"


@dataclass
class CommunicationPolicy:
    """Communication policy between devices."""
    
    policy_id: str
    source_device: str
    destination_device: str
    allowed_protocols: Set[Protocol]
    allowed_ports: Set[int]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def allows_communication(
        self,
        protocol: Protocol,
        port: int
    ) -> bool:
        """
        Check if communication is allowed.
        
        Args:
            protocol: Communication protocol
            port: Communication port
            
        Returns:
            True if allowed
        """
        if not self.enabled:
            return False
        
        return (protocol in self.allowed_protocols and 
                port in self.allowed_ports)


@dataclass
class DeviceSegment:
    """Network segment for device isolation."""
    
    segment_id: str
    zone: NetworkZone
    devices: Set[str] = field(default_factory=set)
    description: str = ""
    
    def add_device(self, device_id: str):
        """Add device to segment."""
        self.devices.add(device_id)
    
    def remove_device(self, device_id: str) -> bool:
        """Remove device from segment."""
        if device_id in self.devices:
            self.devices.remove(device_id)
            return True
        return False


class NetworkSegmentationService:
    """Manages micro-segmented device networks."""
    
    def __init__(self):
        """Initialize network segmentation service."""
        self._segments: Dict[str, DeviceSegment] = {}
        self._policies: Dict[str, CommunicationPolicy] = {}
        self._device_to_segment: Dict[str, str] = {}
        self._default_deny = True
    
    def create_segment(
        self,
        segment_id: str,
        zone: NetworkZone,
        description: str = ""
    ) -> DeviceSegment:
        """
        Create network segment.
        
        Args:
            segment_id: Segment identifier
            zone: Security zone
            description: Segment description
            
        Returns:
            Created segment
        """
        segment = DeviceSegment(
            segment_id=segment_id,
            zone=zone,
            description=description
        )
        self._segments[segment_id] = segment
        return segment
    
    def assign_device_to_segment(
        self,
        device_id: str,
        segment_id: str
    ) -> bool:
        """
        Assign device to network segment.
        
        Args:
            device_id: Device identifier
            segment_id: Segment identifier
            
        Returns:
            True if assigned successfully
        """
        segment = self._segments.get(segment_id)
        if not segment:
            return False
        
        # Remove from old segment if exists
        old_segment_id = self._device_to_segment.get(device_id)
        if old_segment_id and old_segment_id in self._segments:
            self._segments[old_segment_id].remove_device(device_id)
        
        # Add to new segment
        segment.add_device(device_id)
        self._device_to_segment[device_id] = segment_id
        return True
    
    def create_policy(
        self,
        policy_id: str,
        source_device: str,
        destination_device: str,
        allowed_protocols: List[Protocol],
        allowed_ports: List[int],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CommunicationPolicy:
        """
        Create communication policy.
        
        Args:
            policy_id: Policy identifier
            source_device: Source device ID
            destination_device: Destination device ID
            allowed_protocols: List of allowed protocols
            allowed_ports: List of allowed ports
            metadata: Additional policy metadata
            
        Returns:
            Created policy
        """
        policy = CommunicationPolicy(
            policy_id=policy_id,
            source_device=source_device,
            destination_device=destination_device,
            allowed_protocols=set(allowed_protocols),
            allowed_ports=set(allowed_ports),
            metadata=metadata or {}
        )
        self._policies[policy_id] = policy
        return policy
    
    def check_communication_allowed(
        self,
        source_device: str,
        destination_device: str,
        protocol: Protocol,
        port: int
    ) -> bool:
        """
        Check if communication is allowed between devices.
        
        Args:
            source_device: Source device ID
            destination_device: Destination device ID
            protocol: Communication protocol
            port: Communication port
            
        Returns:
            True if communication is allowed
        """
        # Check segment isolation first
        source_segment_id = self._device_to_segment.get(source_device)
        dest_segment_id = self._device_to_segment.get(destination_device)
        
        if not source_segment_id or not dest_segment_id:
            return not self._default_deny
        
        source_segment = self._segments[source_segment_id]
        dest_segment = self._segments[dest_segment_id]
        
        # Same segment communication
        if source_segment_id == dest_segment_id:
            # Check if there's a specific policy
            for policy in self._policies.values():
                if (policy.source_device == source_device and
                    policy.destination_device == destination_device):
                    return policy.allows_communication(protocol, port)
            
            # Allow same-segment communication by default
            return True
        
        # Cross-segment communication - check zone rules
        if not self._is_zone_communication_allowed(
            source_segment.zone,
            dest_segment.zone
        ):
            return False
        
        # Check explicit policies
        for policy in self._policies.values():
            if (policy.source_device == source_device and
                policy.destination_device == destination_device):
                return policy.allows_communication(protocol, port)
        
        # Default deny for cross-segment
        return False
    
    def _is_zone_communication_allowed(
        self,
        source_zone: NetworkZone,
        dest_zone: NetworkZone
    ) -> bool:
        """
        Check if communication between zones is allowed.
        
        Args:
            source_zone: Source security zone
            dest_zone: Destination security zone
            
        Returns:
            True if allowed
        """
        # Define zone communication matrix
        allowed_communications = {
            NetworkZone.PUBLIC: {NetworkZone.DMZ},
            NetworkZone.DMZ: {NetworkZone.INTERNAL},
            NetworkZone.INTERNAL: {NetworkZone.INTERNAL, NetworkZone.RESTRICTED},
            NetworkZone.RESTRICTED: {NetworkZone.RESTRICTED, NetworkZone.CRITICAL},
            NetworkZone.CRITICAL: {NetworkZone.CRITICAL}
        }
        
        return dest_zone in allowed_communications.get(source_zone, set())
    
    def get_segment(self, segment_id: str) -> Optional[DeviceSegment]:
        """
        Get network segment.
        
        Args:
            segment_id: Segment identifier
            
        Returns:
            Segment or None
        """
        return self._segments.get(segment_id)
    
    def get_device_segment(self, device_id: str) -> Optional[DeviceSegment]:
        """
        Get segment for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device segment or None
        """
        segment_id = self._device_to_segment.get(device_id)
        if segment_id:
            return self._segments.get(segment_id)
        return None
    
    def list_segments(self) -> List[DeviceSegment]:
        """
        List all network segments.
        
        Returns:
            List of segments
        """
        return list(self._segments.values())
    
    def list_policies(
        self,
        device_id: Optional[str] = None
    ) -> List[CommunicationPolicy]:
        """
        List communication policies.
        
        Args:
            device_id: Optional device ID to filter policies
            
        Returns:
            List of policies
        """
        if device_id:
            return [
                p for p in self._policies.values()
                if p.source_device == device_id or p.destination_device == device_id
            ]
        return list(self._policies.values())
    
    def enable_policy(self, policy_id: str) -> bool:
        """
        Enable communication policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if enabled successfully
        """
        policy = self._policies.get(policy_id)
        if policy:
            policy.enabled = True
            return True
        return False
    
    def disable_policy(self, policy_id: str) -> bool:
        """
        Disable communication policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if disabled successfully
        """
        policy = self._policies.get(policy_id)
        if policy:
            policy.enabled = False
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get network segmentation statistics.
        
        Returns:
            Statistics dictionary
        """
        total_devices = len(self._device_to_segment)
        devices_by_zone = {}
        
        for segment in self._segments.values():
            zone_name = segment.zone.value
            if zone_name not in devices_by_zone:
                devices_by_zone[zone_name] = 0
            devices_by_zone[zone_name] += len(segment.devices)
        
        active_policies = sum(1 for p in self._policies.values() if p.enabled)
        
        return {
            "total_segments": len(self._segments),
            "total_devices": total_devices,
            "devices_by_zone": devices_by_zone,
            "total_policies": len(self._policies),
            "active_policies": active_policies,
            "default_deny": self._default_deny
        }
    
    def isolate_device(self, device_id: str) -> bool:
        """
        Isolate device by disabling all its policies.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if isolated successfully
        """
        isolated = False
        for policy in self._policies.values():
            if (policy.source_device == device_id or
                policy.destination_device == device_id):
                policy.enabled = False
                isolated = True
        return isolated
