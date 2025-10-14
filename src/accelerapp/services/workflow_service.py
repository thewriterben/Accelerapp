"""
Workflow orchestration service for Accelerapp.
Provides workflow management and execution.
"""

from typing import Any, Callable, Dict, List, Optional

from ..core.interfaces import BaseService
from ..monitoring import get_logger


class WorkflowStep:
    """Represents a step in a workflow."""

    def __init__(
        self,
        name: str,
        action: Callable[[Dict[str, Any]], Dict[str, Any]],
        description: str = "",
    ):
        """
        Initialize workflow step.

        Args:
            name: Step name
            action: Action function to execute
            description: Step description
        """
        self.name = name
        self.action = action
        self.description = description


class Workflow:
    """Represents a workflow with multiple steps."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize workflow.

        Args:
            name: Workflow name
            description: Workflow description
        """
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []

    def add_step(
        self,
        name: str,
        action: Callable[[Dict[str, Any]], Dict[str, Any]],
        description: str = "",
    ) -> None:
        """
        Add a step to the workflow.

        Args:
            name: Step name
            action: Action function
            description: Step description
        """
        step = WorkflowStep(name, action, description)
        self.steps.append(step)

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the workflow.

        Args:
            context: Initial context

        Returns:
            Workflow execution result
        """
        ctx = context or {}
        results = []

        for step in self.steps:
            try:
                result = step.action(ctx)
                results.append({
                    "step": step.name,
                    "status": "success",
                    "result": result,
                })
                # Update context with step result
                ctx.update(result)
            except Exception as e:
                results.append({
                    "step": step.name,
                    "status": "error",
                    "error": str(e),
                })
                break  # Stop on first error

        return {
            "workflow": self.name,
            "steps_completed": len(results),
            "total_steps": len(self.steps),
            "results": results,
        }


class WorkflowService(BaseService):
    """Service for workflow orchestration."""

    def __init__(self):
        """Initialize workflow service."""
        super().__init__("WorkflowService")
        self.logger = get_logger(__name__)
        self._workflows: Dict[str, Workflow] = {}

    async def initialize(self) -> None:
        """Initialize the workflow service."""
        await super().initialize()
        self.logger.info("Workflow service initialized")

    async def shutdown(self) -> None:
        """Shutdown the workflow service."""
        await super().shutdown()
        self.logger.info("Workflow service shutdown")

    def register_workflow(self, workflow: Workflow) -> None:
        """
        Register a workflow.

        Args:
            workflow: Workflow instance
        """
        self._workflows[workflow.name] = workflow
        self.logger.info(f"Registered workflow: {workflow.name}")

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """
        Get a workflow by name.

        Args:
            name: Workflow name

        Returns:
            Workflow instance or None
        """
        return self._workflows.get(name)

    def list_workflows(self) -> List[str]:
        """
        List all registered workflows.

        Returns:
            List of workflow names
        """
        return list(self._workflows.keys())

    def execute_workflow(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            name: Workflow name
            context: Initial context

        Returns:
            Workflow execution result
        """
        workflow = self.get_workflow(name)
        if not workflow:
            return {"status": "error", "message": f"Workflow {name} not found"}

        try:
            result = workflow.execute(context)
            self.logger.info(f"Executed workflow: {name}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing workflow {name}: {e}")
            return {"status": "error", "message": str(e)}

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        health = super().get_health()
        health.update({
            "registered_workflows": len(self._workflows),
            "workflows": list(self._workflows.keys()),
        })
        return health
