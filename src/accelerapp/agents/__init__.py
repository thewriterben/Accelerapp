"""
Agentic coding swarm module.
Provides AI-powered code generation and coordination.
"""

from .orchestrator import AgentOrchestrator
from .base_agent import BaseAgent
from .ai_agent import AIAgent
from .firmware_agent import FirmwareAgent
from .optimization_agents import (
    PerformanceOptimizationAgent,
    MemoryOptimizationAgent,
    CodeQualityAgent,
    SecurityAnalysisAgent,
    RefactoringAgent,
)
from .predictive_maintenance_agent import PredictiveMaintenanceAgent
from .self_healing_agent import SelfHealingAgent
from .firmware_patch_agent import FirmwarePatchAgent

__all__ = [
    "AgentOrchestrator",
    "BaseAgent",
    "AIAgent",
    "FirmwareAgent",
    "PerformanceOptimizationAgent",
    "MemoryOptimizationAgent",
    "CodeQualityAgent",
    "SecurityAnalysisAgent",
    "RefactoringAgent",
    "PredictiveMaintenanceAgent",
    "SelfHealingAgent",
    "FirmwarePatchAgent",
]
