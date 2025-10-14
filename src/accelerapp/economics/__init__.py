"""
Economics module for cost optimization and analysis.
Integrates WildCAM_ESP32 cost optimization framework.
"""

from .analyzer import CostAnalyzer, CostAnalysis, DeploymentRegion

__all__ = [
    "CostAnalyzer",
    "CostAnalysis",
    "DeploymentRegion",
]
