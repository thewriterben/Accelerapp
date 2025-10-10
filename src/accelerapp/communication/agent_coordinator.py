"""
Central coordination service for agent collaboration.
Manages agent registration, task routing, and collaboration strategies.
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import time


class CoordinationStrategy(Enum):
    """Strategies for coordinating agent collaboration."""
    SEQUENTIAL = "sequential"  # Tasks executed in sequence
    PARALLEL = "parallel"      # Tasks executed simultaneously
    PIPELINE = "pipeline"      # Output of one agent feeds to next
    SWARM = "swarm"           # All agents collaborate on each task


@dataclass
class AgentStatus:
    """Status information for an agent."""
    agent_id: str
    name: str
    capabilities: List[str]
    status: str  # idle, busy, error
    current_task: Optional[str] = None
    tasks_completed: int = 0
    last_activity: Optional[float] = None


class AgentCoordinator:
    """
    Central coordinator for managing agent collaboration.
    Routes tasks, manages dependencies, and ensures consistency.
    """
    
    def __init__(self, message_bus=None):
        """
        Initialize agent coordinator.
        
        Args:
            message_bus: Optional MessageBus instance for communication
        """
        self.agents: Dict[str, AgentStatus] = {}
        self.message_bus = message_bus
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.strategy: CoordinationStrategy = CoordinationStrategy.SEQUENTIAL
        
    def register_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str]
    ) -> None:
        """
        Register an agent with the coordinator.
        
        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            capabilities: List of capabilities
        """
        self.agents[agent_id] = AgentStatus(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            status="idle"
        )
        
        if self.message_bus:
            self.message_bus.publish(
                sender="coordinator",
                topic="agent.registered",
                content={"agent_id": agent_id, "name": name}
            )
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if unregistered, False if not found
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            
            if self.message_bus:
                self.message_bus.publish(
                    sender="coordinator",
                    topic="agent.unregistered",
                    content={"agent_id": agent_id}
                )
            return True
        return False
    
    def find_capable_agent(
        self,
        required_capability: str
    ) -> Optional[AgentStatus]:
        """
        Find an available agent with required capability.
        
        Args:
            required_capability: Required capability
            
        Returns:
            AgentStatus if found, None otherwise
        """
        for agent in self.agents.values():
            if (required_capability in agent.capabilities and 
                agent.status == "idle"):
                return agent
        return None
    
    def assign_task(
        self,
        task_id: str,
        agent_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Assign a task to an agent.
        
        Args:
            task_id: Task identifier
            agent_id: Target agent
            task_data: Task data
            
        Returns:
            True if assigned successfully
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent.status = "busy"
        agent.current_task = task_id
        agent.last_activity = time.time()
        
        if self.message_bus:
            self.message_bus.publish(
                sender="coordinator",
                topic="task.assigned",
                content={
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "task_data": task_data
                }
            )
        
        return True
    
    def complete_task(
        self,
        task_id: str,
        agent_id: str,
        result: Any
    ) -> None:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            agent_id: Agent that completed the task
            result: Task result
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = "idle"
            agent.current_task = None
            agent.tasks_completed += 1
            agent.last_activity = time.time()
            
            self.completed_tasks.append({
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result,
                "completed_at": time.time()
            })
            
            if self.message_bus:
                self.message_bus.publish(
                    sender="coordinator",
                    topic="task.completed",
                    content={
                        "task_id": task_id,
                        "agent_id": agent_id
                    }
                )
    
    def set_strategy(self, strategy: CoordinationStrategy) -> None:
        """
        Set coordination strategy.
        
        Args:
            strategy: Coordination strategy to use
        """
        self.strategy = strategy
    
    def add_dependency(
        self,
        task_id: str,
        depends_on: List[str]
    ) -> None:
        """
        Add task dependencies.
        
        Args:
            task_id: Task identifier
            depends_on: List of task IDs this task depends on
        """
        self.dependencies[task_id] = depends_on
    
    def can_execute(self, task_id: str) -> bool:
        """
        Check if a task can be executed (all dependencies met).
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task can execute
        """
        if task_id not in self.dependencies:
            return True
        
        completed_ids = {t["task_id"] for t in self.completed_tasks}
        return all(dep in completed_ids for dep in self.dependencies[task_id])
    
    def get_agent_status(
        self,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get status of agents.
        
        Args:
            agent_id: Optional specific agent ID
            
        Returns:
            Agent status dictionary
        """
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                return {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "capabilities": agent.capabilities,
                    "status": agent.status,
                    "current_task": agent.current_task,
                    "tasks_completed": agent.tasks_completed
                }
            return {}
        
        return {
            "total_agents": len(self.agents),
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "name": a.name,
                    "status": a.status,
                    "tasks_completed": a.tasks_completed
                }
                for a in self.agents.values()
            ]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get coordinator statistics.
        
        Returns:
            Statistics dictionary
        """
        idle_count = sum(1 for a in self.agents.values() if a.status == "idle")
        busy_count = sum(1 for a in self.agents.values() if a.status == "busy")
        
        return {
            "total_agents": len(self.agents),
            "idle_agents": idle_count,
            "busy_agents": busy_count,
            "completed_tasks": len(self.completed_tasks),
            "strategy": self.strategy.value
        }
