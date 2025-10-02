"""
Agent orchestrator for coordinating multiple agents in the swarm.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_agent import BaseAgent


class AgentOrchestrator:
    """
    Orchestrates multiple agents to work together on code generation tasks.
    Implements the "swarm intelligence" pattern for collaborative coding.
    """

    def __init__(self):
        """Initialize the orchestrator with an empty agent pool."""
        self.agents: List[BaseAgent] = []
        self.task_queue: List[Dict[str, Any]] = []

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance to register
        """
        self.agents.append(agent)
        print(f"Registered agent: {agent.name} with capabilities: {agent.capabilities}")

    def find_agent(self, task_type: str) -> Optional[BaseAgent]:
        """
        Find an appropriate agent for a given task type.
        
        Args:
            task_type: Type of task to find agent for
            
        Returns:
            Agent capable of handling the task, or None if not found
        """
        for agent in self.agents:
            if agent.can_handle(task_type):
                return agent
        return None

    def coordinate_generation(
        self, 
        tasks: List[Dict[str, Any]], 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to complete a set of tasks.
        
        Args:
            tasks: List of task specifications
            output_dir: Directory for generated output
            
        Returns:
            Dictionary containing results from all agents
        """
        results = {}
        
        for task in tasks:
            task_type = task.get('type')
            agent = self.find_agent(task_type)
            
            if agent:
                print(f"Assigning {task_type} task to agent: {agent.name}")
                try:
                    result = agent.generate(
                        spec=task.get('spec', {}),
                        context=task.get('context', {})
                    )
                    results[task_type] = {
                        'status': 'success',
                        'output': result,
                        'agent': agent.name
                    }
                    agent.log_action('generate', {'task_type': task_type})
                except Exception as e:
                    results[task_type] = {
                        'status': 'error',
                        'error': str(e),
                        'agent': agent.name
                    }
            else:
                results[task_type] = {
                    'status': 'error',
                    'error': f'No agent found for task type: {task_type}'
                }
        
        return results

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all registered agents.
        
        Returns:
            Dictionary with agent statuses
        """
        return {
            'total_agents': len(self.agents),
            'agents': [
                {
                    'name': agent.name,
                    'capabilities': agent.capabilities,
                    'actions_performed': len(agent.get_history())
                }
                for agent in self.agents
            ]
        }
