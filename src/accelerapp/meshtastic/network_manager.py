"""
Mesh network management for Meshtastic devices.
Handles network topology, node monitoring, and routing.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum


class NodeStatus(Enum):
    """Status of a mesh node."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass
class MeshNode:
    """Represents a node in the mesh network."""
    
    node_id: str
    short_name: str
    long_name: str
    hardware_model: str
    firmware_version: str
    status: NodeStatus = NodeStatus.UNKNOWN
    last_heard: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    snr: Optional[float] = None
    hop_count: int = 0
    neighbors: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "short_name": self.short_name,
            "long_name": self.long_name,
            "hardware_model": self.hardware_model,
            "firmware_version": self.firmware_version,
            "status": self.status.value,
            "last_heard": self.last_heard.isoformat() if self.last_heard else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "snr": self.snr,
            "hop_count": self.hop_count,
            "neighbors": list(self.neighbors),
        }


@dataclass
class NetworkTopology:
    """Represents the mesh network topology."""
    
    nodes: Dict[str, MeshNode] = field(default_factory=dict)
    edges: List[tuple[str, str]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    
    def add_node(self, node: MeshNode) -> None:
        """Add a node to the topology."""
        self.nodes[node.node_id] = node
        self.last_update = datetime.now()
    
    def add_edge(self, node1_id: str, node2_id: str) -> None:
        """Add a connection between two nodes."""
        edge = (node1_id, node2_id)
        if edge not in self.edges:
            self.edges.append(edge)
        
        # Update neighbor lists
        if node1_id in self.nodes:
            self.nodes[node1_id].neighbors.add(node2_id)
        if node2_id in self.nodes:
            self.nodes[node2_id].neighbors.add(node1_id)
        
        self.last_update = datetime.now()
    
    def get_node(self, node_id: str) -> Optional[MeshNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_online_nodes(self) -> List[MeshNode]:
        """Get all online nodes."""
        return [node for node in self.nodes.values() if node.status == NodeStatus.ONLINE]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": self.edges,
            "last_update": self.last_update.isoformat(),
            "total_nodes": len(self.nodes),
            "online_nodes": len(self.get_online_nodes()),
        }


class MeshNetworkManager:
    """
    Manages Meshtastic mesh network operations.
    Monitors topology, routes messages, and provides analytics.
    """
    
    def __init__(self):
        """Initialize mesh network manager."""
        self.topology = NetworkTopology()
        self.message_history: List[Dict[str, Any]] = []
        self.routing_table: Dict[str, List[str]] = {}
    
    def update_node(self, node: MeshNode) -> None:
        """
        Update or add a node to the network.
        
        Args:
            node: Node information
        """
        self.topology.add_node(node)
        self._update_routing_table()
    
    def update_connection(self, node1_id: str, node2_id: str) -> None:
        """
        Update connection between two nodes.
        
        Args:
            node1_id: First node ID
            node2_id: Second node ID
        """
        self.topology.add_edge(node1_id, node2_id)
        self._update_routing_table()
    
    def get_topology(self) -> NetworkTopology:
        """
        Get current network topology.
        
        Returns:
            Network topology
        """
        return self.topology
    
    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node information dictionary or None
        """
        node = self.topology.get_node(node_id)
        return node.to_dict() if node else None
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get network statistics.
        
        Returns:
            Dictionary with network statistics
        """
        online_nodes = self.topology.get_online_nodes()
        
        # Calculate average signal strength
        signal_strengths = [
            node.signal_strength 
            for node in online_nodes 
            if node.signal_strength is not None
        ]
        avg_signal = sum(signal_strengths) / len(signal_strengths) if signal_strengths else 0
        
        # Calculate network density
        total_possible_edges = len(self.topology.nodes) * (len(self.topology.nodes) - 1) / 2
        network_density = len(self.topology.edges) / total_possible_edges if total_possible_edges > 0 else 0
        
        return {
            "total_nodes": len(self.topology.nodes),
            "online_nodes": len(online_nodes),
            "total_edges": len(self.topology.edges),
            "network_density": network_density,
            "average_signal_strength": avg_signal,
            "messages_sent": len(self.message_history),
            "last_update": self.topology.last_update.isoformat(),
        }
    
    def find_route(self, source_id: str, dest_id: str) -> Optional[List[str]]:
        """
        Find route between two nodes.
        
        Args:
            source_id: Source node ID
            dest_id: Destination node ID
            
        Returns:
            List of node IDs in route or None if no route found
        """
        # Simple BFS implementation for route finding
        if source_id not in self.topology.nodes or dest_id not in self.topology.nodes:
            return None
        
        if source_id == dest_id:
            return [source_id]
        
        visited = {source_id}
        queue = [(source_id, [source_id])]
        
        while queue:
            current, path = queue.pop(0)
            node = self.topology.nodes[current]
            
            for neighbor_id in node.neighbors:
                if neighbor_id == dest_id:
                    return path + [neighbor_id]
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def _update_routing_table(self) -> None:
        """Update internal routing table based on topology."""
        # Calculate shortest paths between all nodes
        self.routing_table = {}
        
        for source_id in self.topology.nodes:
            self.routing_table[source_id] = {}
            for dest_id in self.topology.nodes:
                if source_id != dest_id:
                    route = self.find_route(source_id, dest_id)
                    if route:
                        self.routing_table[source_id][dest_id] = route
    
    def send_message(
        self,
        source_id: str,
        dest_id: str,
        message: str,
        encrypted: bool = True
    ) -> Dict[str, Any]:
        """
        Send message through mesh network.
        
        Args:
            source_id: Source node ID
            dest_id: Destination node ID
            message: Message content
            encrypted: Whether to encrypt message
            
        Returns:
            Dictionary with send status
        """
        route = self.find_route(source_id, dest_id)
        
        if not route:
            return {
                "status": "failed",
                "reason": "No route found",
                "source": source_id,
                "destination": dest_id,
            }
        
        message_record = {
            "timestamp": datetime.now().isoformat(),
            "source": source_id,
            "destination": dest_id,
            "route": route,
            "hop_count": len(route) - 1,
            "encrypted": encrypted,
            "status": "sent",
        }
        
        self.message_history.append(message_record)
        
        return {
            "status": "sent",
            "route": route,
            "hop_count": len(route) - 1,
            "message_id": len(self.message_history) - 1,
        }
    
    def get_message_history(
        self,
        node_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get message history.
        
        Args:
            node_id: Filter by node ID (source or destination)
            limit: Maximum number of messages to return
            
        Returns:
            List of message records
        """
        messages = self.message_history
        
        if node_id:
            messages = [
                m for m in messages
                if m["source"] == node_id or m["destination"] == node_id
            ]
        
        return messages[-limit:]
    
    def export_topology(self, output_file: str) -> None:
        """
        Export network topology to file.
        
        Args:
            output_file: Output file path (JSON format)
        """
        import json
        
        with open(output_file, "w") as f:
            json.dump(self.topology.to_dict(), f, indent=2)
