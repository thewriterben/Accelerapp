"""
Azure integration for Accelerapp.
"""

from typing import Dict, Any, List


class AzureIntegration:
    """
    Azure deployment and integration support.
    """

    def __init__(self):
        """Initialize Azure integration."""
        self.configurations: Dict[str, Any] = {}

    def generate_function_app_config(
        self, app_name: str, runtime: str = "python|3.10"
    ) -> Dict[str, Any]:
        """
        Generate Azure Function App configuration.

        Args:
            app_name: Function app name
            runtime: Runtime stack

        Returns:
            ARM template configuration
        """
        schema_url = (
            "https://schema.management.azure.com/schemas/"
            "2019-04-01/deploymentTemplate.json#"
        )
        config = {
            "$schema": schema_url,
            "contentVersion": "1.0.0.0",
            "parameters": {
                "appName": {"type": "string", "defaultValue": app_name},
                "location": {"type": "string", "defaultValue": "[resourceGroup().location]"},
            },
            "resources": [
                {
                    "type": "Microsoft.Web/sites",
                    "apiVersion": "2021-02-01",
                    "name": "[parameters('appName')]",
                    "location": "[parameters('location')]",
                    "kind": "functionapp,linux",
                    "properties": {
                        "reserved": True,
                        "siteConfig": {
                            "linuxFxVersion": runtime,
                            "appSettings": [
                                {
                                    "name": "FUNCTIONS_WORKER_RUNTIME",
                                    "value": "python",
                                },
                                {
                                    "name": "ACCELERAPP_ENV",
                                    "value": "production",
                                },
                            ],
                        },
                    },
                }
            ],
        }

        return config

    def generate_iot_hub_config(self, hub_name: str, platforms: List[str]) -> Dict[str, Any]:
        """
        Generate Azure IoT Hub configuration.

        Args:
            hub_name: IoT Hub name
            platforms: Target hardware platforms

        Returns:
            ARM template configuration
        """
        schema_url = (
            "https://schema.management.azure.com/schemas/"
            "2019-04-01/deploymentTemplate.json#"
        )
        config = {
            "$schema": schema_url,
            "contentVersion": "1.0.0.0",
            "resources": [
                {
                    "type": "Microsoft.Devices/IotHubs",
                    "apiVersion": "2021-07-02",
                    "name": hub_name,
                    "location": "[resourceGroup().location]",
                    "sku": {
                        "name": "S1",
                        "capacity": 1,
                    },
                    "properties": {
                        "eventHubEndpoints": {
                            "events": {
                                "retentionTimeInDays": 1,
                                "partitionCount": 2,
                            }
                        },
                        "routing": {
                            "endpoints": {
                                "serviceBusQueues": [],
                                "serviceBusTopics": [],
                                "eventHubs": [],
                            },
                            "routes": [],
                            "fallbackRoute": {
                                "name": "$fallback",
                                "source": "DeviceMessages",
                                "condition": "true",
                                "endpointNames": ["events"],
                                "isEnabled": True,
                            },
                        },
                    },
                    "tags": {
                        "framework": "accelerapp",
                        "platforms": ",".join(platforms),
                    },
                }
            ],
        }

        return config

    def generate_container_registry_config(self, registry_name: str) -> Dict[str, Any]:
        """
        Generate Azure Container Registry configuration.

        Args:
            registry_name: Registry name

        Returns:
            ARM template configuration
        """
        schema_url = (
            "https://schema.management.azure.com/schemas/"
            "2019-04-01/deploymentTemplate.json#"
        )
        config = {
            "$schema": schema_url,
            "contentVersion": "1.0.0.0",
            "resources": [
                {
                    "type": "Microsoft.ContainerRegistry/registries",
                    "apiVersion": "2021-09-01",
                    "name": registry_name,
                    "location": "[resourceGroup().location]",
                    "sku": {"name": "Basic"},
                    "properties": {
                        "adminUserEnabled": True,
                    },
                }
            ],
        }

        return config

    def generate_devops_pipeline(self, project_name: str, platforms: List[str]) -> str:
        """
        Generate Azure DevOps pipeline YAML.

        Args:
            project_name: Project name
            platforms: Target platforms

        Returns:
            Pipeline YAML content
        """
        pipeline = f"""trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.10'
  projectName: '{project_name}'

stages:
- stage: Build
  jobs:
  - job: Test
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
    
    - script: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
      displayName: 'Install dependencies'
    
    - script: |
        pytest tests/ --junitxml=test-results.xml
        black --check src/
      displayName: 'Run tests'
    
    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'test-results.xml'
        testRunTitle: 'Python $(pythonVersion)'
      condition: succeededOrFailed()

- stage: Generate
  jobs:
"""

        for platform in platforms:
            pipeline += f"""  - job: Generate_{platform}
    steps:
    - script: |
        accelerapp generate --platform {platform} --config examples/config.yaml
      displayName: 'Generate {platform} firmware'
    
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'output/'
        artifactName: '{platform}-artifacts'

"""

        return pipeline
