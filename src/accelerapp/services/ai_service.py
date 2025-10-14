"""
AI agent management service for Accelerapp.
Provides unified interface for AI agent operations.
"""

from typing import Any, Dict, List, Optional

from ..core.interfaces import BaseService, IAgent
from ..monitoring import get_logger


class AIService(BaseService):
    """Service for AI agent management."""

    def __init__(self):
        """Initialize AI service."""
        super().__init__("AIService")
        self.logger = get_logger(__name__)
        self._agents: Dict[str, IAgent] = {}

    async def initialize(self) -> None:
        """Initialize the AI service."""
        await super().initialize()
        self.logger.info("AI service initialized")

    async def shutdown(self) -> None:
        """Shutdown the AI service."""
        await super().shutdown()
        self.logger.info("AI service shutdown")

    def register_agent(self, agent_id: str, agent: IAgent) -> None:
        """
        Register an AI agent.

        Args:
            agent_id: Agent identifier
            agent: Agent instance
        """
        self._agents[agent_id] = agent
        self.logger.info(f"Registered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[IAgent]:
        """
        Get an AI agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance or None
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> List[str]:
        """
        List all registered agents.

        Returns:
            List of agent IDs
        """
        return list(self._agents.keys())

    def find_agent_for_task(self, task: str) -> Optional[IAgent]:
        """
        Find an agent capable of handling a task.

        Args:
            task: Task description

        Returns:
            Agent instance or None
        """
        for agent in self._agents.values():
            if agent.can_handle(task):
                return agent
        return None

    def generate(
        self,
        agent_id: str,
        spec: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate output using a specific agent.

        Args:
            agent_id: Agent identifier
            spec: Generation specification
            context: Optional context

        Returns:
            Generation result
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        try:
            result = agent.generate(spec, context)
            self.logger.info(f"Generated output with agent: {agent_id}")
            return result
        except Exception as e:
            self.logger.error(f"Error generating with agent {agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        health = super().get_health()
        health.update({
            "registered_agents": len(self._agents),
            "agents": list(self._agents.keys()),
        })
        return health
