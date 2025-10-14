"""
Agent Swarm Orchestration System.
Coordinates multiple AI agents for complex tasks.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio


class AgentRole(Enum):
    """Defines roles for agents in a swarm."""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"


@dataclass
class AgentConfig:
    """Configuration for an agent in the swarm."""
    agent_id: str
    role: AgentRole
    capabilities: List[str]
    priority: int = 1
    max_concurrent_tasks: int = 1


@dataclass
class Task:
    """Represents a task in the swarm."""
    task_id: str
    task_type: str
    data: Dict[str, Any]
    required_capabilities: List[str]
    status: str = "pending"  # pending, assigned, in_progress, completed, failed
    assigned_to: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class AgentSwarmOrchestrator:
    """
    Orchestrates multiple AI agents to work together on complex tasks.
    Manages task distribution, agent coordination, and result aggregation.
    """
    
    def __init__(self):
        """Initialize swarm orchestrator."""
        self.agents: Dict[str, AgentConfig] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.agent_callbacks: Dict[str, Callable] = {}
    
    def register_agent(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[str],
        callback: Callable,
        priority: int = 1,
        max_concurrent_tasks: int = 1
    ) -> None:
        """
        Register an agent in the swarm.
        
        Args:
            agent_id: Unique agent identifier
            role: Agent role in the swarm
            capabilities: List of agent capabilities
            callback: Function to call when assigning tasks
            priority: Agent priority (higher = more preferred)
            max_concurrent_tasks: Maximum concurrent tasks
        """
        self.agents[agent_id] = AgentConfig(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            priority=priority,
            max_concurrent_tasks=max_concurrent_tasks
        )
        self.agent_callbacks[agent_id] = callback
    
    def submit_task(
        self,
        task_id: str,
        task_type: str,
        data: Dict[str, Any],
        required_capabilities: List[str]
    ) -> Task:
        """
        Submit a task to the swarm.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            data: Task data
            required_capabilities: Required agent capabilities
            
        Returns:
            Created Task instance
        """
        task = Task(
            task_id=task_id,
            task_type=task_type,
            data=data,
            required_capabilities=required_capabilities
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Try to assign immediately
        self._assign_tasks()
        
        return task
    
    def _find_suitable_agent(self, task: Task) -> Optional[str]:
        """
        Find a suitable agent for a task.
        
        Args:
            task: Task to assign
            
        Returns:
            Agent ID or None
        """
        suitable_agents = []
        
        for agent_id, agent in self.agents.items():
            # Check if agent has required capabilities
            has_capabilities = all(
                cap in agent.capabilities
                for cap in task.required_capabilities
            )
            
            if has_capabilities:
                # Count current tasks assigned to this agent
                assigned_tasks = sum(
                    1 for t in self.tasks.values()
                    if t.assigned_to == agent_id and t.status in ["assigned", "in_progress"]
                )
                
                if assigned_tasks < agent.max_concurrent_tasks:
                    suitable_agents.append((agent_id, agent.priority))
        
        if suitable_agents:
            # Sort by priority (higher first)
            suitable_agents.sort(key=lambda x: x[1], reverse=True)
            return suitable_agents[0][0]
        
        return None
    
    def _assign_tasks(self) -> None:
        """Assign pending tasks to available agents."""
        pending_tasks = [
            task_id for task_id in self.task_queue
            if self.tasks[task_id].status == "pending"
        ]
        
        for task_id in pending_tasks:
            task = self.tasks[task_id]
            agent_id = self._find_suitable_agent(task)
            
            if agent_id:
                task.assigned_to = agent_id
                task.status = "assigned"
                self.task_queue.remove(task_id)
                
                # Call agent callback
                if agent_id in self.agent_callbacks:
                    try:
                        self.agent_callbacks[agent_id](task)
                        task.status = "in_progress"
                    except Exception:
                        task.status = "failed"
    
    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        success: bool = True
    ) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            result: Task result
            success: Whether task completed successfully
            
        Returns:
            True if successful, False otherwise
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.result = result
        task.status = "completed" if success else "failed"
        
        # Try to assign more tasks
        self._assign_tasks()
        
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dictionary with task status
        """
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "result": task.result
        }
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Get overall swarm status.
        
        Returns:
            Dictionary with swarm statistics
        """
        total_tasks = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        in_progress = sum(1 for t in self.tasks.values() if t.status in ["assigned", "in_progress"])
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            assigned = sum(
                1 for t in self.tasks.values()
                if t.assigned_to == agent_id and t.status in ["assigned", "in_progress"]
            )
            completed_count = sum(
                1 for t in self.tasks.values()
                if t.assigned_to == agent_id and t.status == "completed"
            )
            
            agent_stats[agent_id] = {
                "role": agent.role.value,
                "active_tasks": assigned,
                "completed_tasks": completed_count,
                "capabilities": agent.capabilities
            }
        
        return {
            "total_agents": len(self.agents),
            "total_tasks": total_tasks,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "agents": agent_stats
        }
    
    def coordinate_complex_task(
        self,
        task_description: str,
        subtasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Coordinate a complex task by breaking it into subtasks.
        
        Args:
            task_description: Description of the complex task
            subtasks: List of subtask specifications
            
        Returns:
            Dictionary with coordination results
        """
        coordination_id = f"coord_{len(self.tasks)}"
        submitted_tasks = []
        
        for i, subtask_spec in enumerate(subtasks):
            task_id = f"{coordination_id}_subtask_{i}"
            task = self.submit_task(
                task_id=task_id,
                task_type=subtask_spec.get("type", "generic"),
                data=subtask_spec.get("data", {}),
                required_capabilities=subtask_spec.get("capabilities", [])
            )
            submitted_tasks.append(task_id)
        
        return {
            "coordination_id": coordination_id,
            "description": task_description,
            "subtasks": submitted_tasks,
            "status": "coordinating"
        }
    
    async def execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of task specifications
            
        Returns:
            List of task results
        """
        task_ids = []
        
        # Submit all tasks
        for i, task_spec in enumerate(tasks):
            task_id = f"parallel_{i}"
            self.submit_task(
                task_id=task_id,
                task_type=task_spec.get("type", "generic"),
                data=task_spec.get("data", {}),
                required_capabilities=task_spec.get("capabilities", [])
            )
            task_ids.append(task_id)
        
        # Wait for all tasks to complete (simplified version)
        results = []
        for task_id in task_ids:
            status = self.get_task_status(task_id)
            if status:
                results.append(status)
        
        return results
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agents:
            return False
        
        # Reassign tasks from this agent
        for task in self.tasks.values():
            if task.assigned_to == agent_id and task.status in ["assigned", "in_progress"]:
                task.status = "pending"
                task.assigned_to = None
                self.task_queue.append(task.task_id)
        
        del self.agents[agent_id]
        if agent_id in self.agent_callbacks:
            del self.agent_callbacks[agent_id]
        
        # Try to reassign tasks
        self._assign_tasks()
        
        return True
