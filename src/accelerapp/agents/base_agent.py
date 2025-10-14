"""
Base agent class for the agentic coding swarm.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Agents are responsible for generating specific types of code.
    """

    def __init__(self, name: str, capabilities: List[str]):
        """
        Initialize the agent.

        Args:
            name: Agent identifier
            capabilities: List of capabilities this agent provides
        """
        self.name = name
        self.capabilities = capabilities
        self.history = []

    @abstractmethod
    def generate(self, spec: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate code based on specification and context.

        Args:
            spec: Hardware or component specification
            context: Additional context for generation

        Returns:
            Generated code as string
        """
        pass

    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a specific task type."""
        return task_type in self.capabilities

    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log an action performed by this agent."""
        self.history.append({"action": action, "details": details})

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the action history for this agent."""
        return self.history.copy()
