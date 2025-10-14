"""
Visual specification data structures.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Component:
    """
    Represents a hardware or software component in the visual specification.
    """

    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=dict)  # x, y coordinates

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": self.properties,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Connection:
    """
    Represents a connection between components.
    """

    id: str
    source_id: str
    target_id: str
    source_port: str
    target_port: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "source_port": self.source_port,
            "target_port": self.target_port,
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Connection":
        """Create from dictionary."""
        return cls(**data)


class VisualSpecification:
    """
    Manages a visual hardware specification with components and connections.
    """

    def __init__(self, name: str = "New Specification", description: str = ""):
        """
        Initialize visual specification.

        Args:
            name: Specification name
            description: Specification description
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.components: Dict[str, Component] = {}
        self.connections: Dict[str, Connection] = {}
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": "1.0",
        }

    def add_component(
        self,
        component_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Add a component to the specification.

        Args:
            component_type: Type of component (e.g., 'led', 'button', 'sensor')
            name: Component name
            properties: Component properties
            position: Visual position (x, y)

        Returns:
            Component ID
        """
        component_id = str(uuid.uuid4())

        component = Component(
            id=component_id,
            type=component_type,
            name=name,
            properties=properties or {},
            position=position or {"x": 0, "y": 0},
        )

        self.components[component_id] = component
        self._update_timestamp()

        return component_id

    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component and its connections.

        Args:
            component_id: Component identifier

        Returns:
            True if removed successfully
        """
        if component_id not in self.components:
            return False

        # Remove component
        del self.components[component_id]

        # Remove associated connections
        connections_to_remove = [
            conn_id
            for conn_id, conn in self.connections.items()
            if conn.source_id == component_id or conn.target_id == component_id
        ]

        for conn_id in connections_to_remove:
            del self.connections[conn_id]

        self._update_timestamp()
        return True

    def update_component(
        self,
        component_id: str,
        properties: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Update component properties or position.

        Args:
            component_id: Component identifier
            properties: Updated properties
            position: Updated position

        Returns:
            True if updated successfully
        """
        if component_id not in self.components:
            return False

        component = self.components[component_id]

        if properties is not None:
            component.properties.update(properties)

        if position is not None:
            component.position.update(position)

        self._update_timestamp()
        return True

    def add_connection(
        self,
        source_id: str,
        target_id: str,
        source_port: str = "output",
        target_port: str = "input",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Add a connection between components.

        Args:
            source_id: Source component ID
            target_id: Target component ID
            source_port: Source port name
            target_port: Target port name
            properties: Connection properties

        Returns:
            Connection ID or None if invalid
        """
        if source_id not in self.components or target_id not in self.components:
            return None

        connection_id = str(uuid.uuid4())

        connection = Connection(
            id=connection_id,
            source_id=source_id,
            target_id=target_id,
            source_port=source_port,
            target_port=target_port,
            properties=properties or {},
        )

        self.connections[connection_id] = connection
        self._update_timestamp()

        return connection_id

    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection.

        Args:
            connection_id: Connection identifier

        Returns:
            True if removed successfully
        """
        if connection_id not in self.connections:
            return False

        del self.connections[connection_id]
        self._update_timestamp()
        return True

    def validate(self) -> List[str]:
        """
        Validate the specification.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for orphaned connections
        for conn_id, conn in self.connections.items():
            if conn.source_id not in self.components:
                errors.append(f"Connection {conn_id}: source component not found")
            if conn.target_id not in self.components:
                errors.append(f"Connection {conn_id}: target component not found")

        # Check for duplicate component names
        names = [c.name for c in self.components.values()]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate component names: {', '.join(set(duplicates))}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert specification to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "components": {cid: comp.to_dict() for cid, comp in self.components.items()},
            "connections": {cid: conn.to_dict() for cid, conn in self.connections.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualSpecification":
        """
        Create specification from dictionary.

        Args:
            data: Dictionary data

        Returns:
            VisualSpecification instance
        """
        spec = cls(name=data.get("name", "Unnamed"), description=data.get("description", ""))

        spec.id = data.get("id", spec.id)
        spec.metadata = data.get("metadata", spec.metadata)

        # Load components
        for comp_id, comp_data in data.get("components", {}).items():
            spec.components[comp_id] = Component.from_dict(comp_data)

        # Load connections
        for conn_id, conn_data in data.get("connections", {}).items():
            spec.connections[conn_id] = Connection.from_dict(conn_data)

        return spec

    def _update_timestamp(self):
        """Update the updated_at timestamp."""
        self.metadata["updated_at"] = datetime.utcnow().isoformat()
