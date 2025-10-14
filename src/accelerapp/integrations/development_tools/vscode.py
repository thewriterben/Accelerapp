"""
VS Code extension support for Accelerapp.
"""

from typing import Dict, Any, List, Optional
import json


class VSCodeExtension:
    """
    VS Code extension configuration and support.
    """

    def __init__(self):
        """Initialize VS Code extension."""
        self.configurations: Dict[str, Any] = {}

    def generate_extension_manifest(
        self, extension_name: str, version: str, description: str
    ) -> Dict[str, Any]:
        """
        Generate VS Code extension package.json.

        Args:
            extension_name: Extension name
            version: Extension version
            description: Extension description

        Returns:
            package.json dictionary
        """
        manifest = {
            "name": extension_name,
            "displayName": "Accelerapp",
            "description": description,
            "version": version,
            "publisher": "accelerapp",
            "engines": {"vscode": "^1.70.0"},
            "categories": ["Programming Languages", "Snippets", "Other"],
            "activationEvents": ["onLanguage:yaml", "onCommand:accelerapp.generate"],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "accelerapp.generate",
                        "title": "Accelerapp: Generate Code",
                    },
                    {
                        "command": "accelerapp.validate",
                        "title": "Accelerapp: Validate Configuration",
                    },
                    {
                        "command": "accelerapp.newProject",
                        "title": "Accelerapp: New Project",
                    },
                ],
                "languages": [
                    {
                        "id": "accelerapp-yaml",
                        "aliases": ["Accelerapp YAML", "accelerapp"],
                        "extensions": [".accelerapp.yaml", ".accelerapp.yml"],
                        "configuration": "./language-configuration.json",
                    }
                ],
                "grammars": [
                    {
                        "language": "accelerapp-yaml",
                        "scopeName": "source.accelerapp.yaml",
                        "path": "./syntaxes/accelerapp.tmLanguage.json",
                    }
                ],
                "snippets": [
                    {
                        "language": "yaml",
                        "path": "./snippets/accelerapp.json",
                    }
                ],
                "configuration": {
                    "title": "Accelerapp",
                    "properties": {
                        "accelerapp.pythonPath": {
                            "type": "string",
                            "default": "python",
                            "description": "Path to Python executable",
                        },
                        "accelerapp.autoGenerate": {
                            "type": "boolean",
                            "default": False,
                            "description": "Automatically generate code on save",
                        },
                    },
                },
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc -watch -p ./",
            },
            "devDependencies": {
                "@types/node": "^16.x",
                "@types/vscode": "^1.70.0",
                "typescript": "^4.9.0",
            },
        }

        return manifest

    def generate_snippets(self) -> Dict[str, Any]:
        """
        Generate VS Code snippets for Accelerapp.

        Returns:
            Snippets dictionary
        """
        snippets = {
            "Accelerapp Device Configuration": {
                "prefix": "accelerapp-device",
                "body": [
                    "device_name: ${1:MyDevice}",
                    "platform: ${2:arduino}",
                    "peripherals:",
                    "  - type: ${3:led}",
                    "    pin: ${4:13}",
                    "    name: ${5:status_led}",
                ],
                "description": "Basic Accelerapp device configuration",
            },
            "Accelerapp LED Peripheral": {
                "prefix": "accelerapp-led",
                "body": [
                    "- type: led",
                    "  pin: ${1:13}",
                    "  name: ${2:led_name}",
                ],
                "description": "LED peripheral configuration",
            },
            "Accelerapp Sensor Peripheral": {
                "prefix": "accelerapp-sensor",
                "body": [
                    "- type: sensor",
                    "  pin: ${1:A0}",
                    "  name: ${2:sensor_name}",
                    "  sensor_type: ${3:temperature}",
                ],
                "description": "Sensor peripheral configuration",
            },
        }

        return snippets

    def generate_launch_config(self, project_path: str) -> Dict[str, Any]:
        """
        Generate VS Code launch.json for debugging.

        Args:
            project_path: Project path

        Returns:
            launch.json dictionary
        """
        config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Accelerapp: Generate Code",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/venv/bin/accelerapp",
                    "args": ["generate", "--config", "config.yaml"],
                    "console": "integratedTerminal",
                },
                {
                    "name": "Accelerapp: Run Tests",
                    "type": "python",
                    "request": "launch",
                    "module": "pytest",
                    "args": ["tests/"],
                    "console": "integratedTerminal",
                },
            ],
        }

        return config

    def generate_tasks_config(self) -> Dict[str, Any]:
        """
        Generate VS Code tasks.json.

        Returns:
            tasks.json dictionary
        """
        config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Generate Firmware",
                    "type": "shell",
                    "command": "accelerapp generate --config config.yaml",
                    "group": {"kind": "build", "isDefault": True},
                    "presentation": {
                        "reveal": "always",
                        "panel": "new",
                    },
                },
                {
                    "label": "Run Tests",
                    "type": "shell",
                    "command": "pytest tests/",
                    "group": "test",
                },
                {
                    "label": "Format Code",
                    "type": "shell",
                    "command": "black src/",
                    "group": "none",
                },
            ],
        }

        return config

    def generate_settings_json(self) -> Dict[str, Any]:
        """
        Generate VS Code workspace settings.

        Returns:
            settings.json dictionary
        """
        settings = {
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "files.associations": {
                "*.accelerapp.yaml": "yaml",
                "*.accelerapp.yml": "yaml",
            },
            "[yaml]": {
                "editor.insertSpaces": True,
                "editor.tabSize": 2,
                "editor.autoIndent": "advanced",
            },
        }

        return settings
