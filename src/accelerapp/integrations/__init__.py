"""
Integrations module for Accelerapp.
Provides integrations with CI/CD platforms, cloud providers, and development tools.
"""

from .ci_cd.github_actions import GitHubActionsIntegration
from .ci_cd.jenkins import JenkinsIntegration
from .cloud_platforms.aws import AWSIntegration
from .cloud_platforms.azure import AzureIntegration
from .hardware_vendors.arduino import ArduinoIDEIntegration
from .development_tools.vscode import VSCodeExtension

__all__ = [
    "GitHubActionsIntegration",
    "JenkinsIntegration",
    "AWSIntegration",
    "AzureIntegration",
    "ArduinoIDEIntegration",
    "VSCodeExtension",
]
