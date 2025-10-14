"""
GitHub Actions integration for Accelerapp.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class WorkflowConfig:
    """GitHub Actions workflow configuration."""

    name: str
    triggers: List[str]
    jobs: List[Dict[str, Any]]


class GitHubActionsIntegration:
    """
    Generates GitHub Actions workflows for Accelerapp projects.
    """

    def __init__(self):
        """Initialize GitHub Actions integration."""
        self.workflows: Dict[str, WorkflowConfig] = {}

    def generate_ci_workflow(
        self, project_name: str, platforms: List[str], test_commands: Optional[List[str]] = None
    ) -> str:
        """
        Generate a CI workflow YAML file.

        Args:
            project_name: Project name
            platforms: Target platforms (arduino, esp32, etc.)
            test_commands: Optional custom test commands

        Returns:
            Workflow YAML content
        """
        test_commands = test_commands or ["pytest tests/", "black --check src/", "flake8 src/"]

        workflow = f"""name: {project_name} CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
"""
        for cmd in test_commands:
            workflow += f"        {cmd}\n"

        workflow += """
  build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Generate firmware
      run: |
        pip install -e .
        accelerapp generate --config examples/config.yaml
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: generated-code
        path: output/
"""

        return workflow

    def generate_release_workflow(self, project_name: str) -> str:
        """
        Generate a release workflow YAML file.

        Args:
            project_name: Project name

        Returns:
            Workflow YAML content
        """
        workflow = f"""name: {project_name} Release

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{{{ secrets.PYPI_TOKEN }}}}
      run: twine upload dist/*
    
    - name: Create GitHub Release Assets
      uses: actions/upload-release-asset@v1
      with:
        upload_url: ${{{{ github.event.release.upload_url }}}}
        asset_path: ./dist
"""

        return workflow

    def generate_hardware_test_workflow(self, platforms: List[str]) -> str:
        """
        Generate hardware testing workflow.

        Args:
            platforms: Target hardware platforms

        Returns:
            Workflow YAML content
        """
        workflow = """name: Hardware Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  hardware-test:
    runs-on: self-hosted
    strategy:
      matrix:
        platform:
"""
        for platform in platforms:
            workflow += f"          - {platform}\n"

        workflow += """
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -e .[dev]
    
    - name: Generate firmware
      run: |
        accelerapp generate \\
          --platform ${{ matrix.platform }} \\
          --config examples/config.yaml
    
    - name: Upload to hardware
      run: |
        # Custom hardware upload script
        python scripts/upload_firmware.py \\
          --platform ${{ matrix.platform }} \\
          --firmware output/firmware/
    
    - name: Run HIL tests
      run: pytest tests/hil/ --platform ${{ matrix.platform }}
"""

        return workflow

    def get_workflow_template(self, workflow_type: str) -> Optional[str]:
        """
        Get a workflow template by type.

        Args:
            workflow_type: Type of workflow (ci, release, hardware-test)

        Returns:
            Workflow YAML content or None
        """
        if workflow_type == "ci":
            return self.generate_ci_workflow("Accelerapp Project", ["arduino", "esp32"])
        elif workflow_type == "release":
            return self.generate_release_workflow("Accelerapp Project")
        elif workflow_type == "hardware-test":
            return self.generate_hardware_test_workflow(["arduino", "esp32", "stm32"])
        return None
