"""Tests for deployment infrastructure and CI/CD configuration."""

import os
import yaml
from pathlib import Path


class TestDockerConfiguration:
    """Test Docker configuration files."""

    def test_dockerignore_exists(self):
        """Test that .dockerignore file exists."""
        dockerignore = Path(__file__).parent.parent / ".dockerignore"
        assert dockerignore.exists(), ".dockerignore file should exist"

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        dockerfile = Path(__file__).parent.parent / "deployment" / "docker" / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist"

    def test_dockerfile_monitoring_exists(self):
        """Test that monitoring Dockerfile exists."""
        dockerfile = (
            Path(__file__).parent.parent
            / "deployment"
            / "docker"
            / "Dockerfile.monitoring"
        )
        assert dockerfile.exists(), "Dockerfile.monitoring should exist"

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists."""
        compose = (
            Path(__file__).parent.parent / "deployment" / "docker" / "docker-compose.yml"
        )
        assert compose.exists(), "docker-compose.yml should exist"

    def test_docker_compose_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML."""
        compose = (
            Path(__file__).parent.parent / "deployment" / "docker" / "docker-compose.yml"
        )
        with open(compose) as f:
            data = yaml.safe_load(f)
        assert "services" in data
        assert "accelerapp" in data["services"]
        assert "ollama" in data["services"]


class TestCICDWorkflows:
    """Test CI/CD workflow configurations."""

    def test_ci_workflow_exists(self):
        """Test that CI workflow exists."""
        workflow = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        assert workflow.exists(), "ci.yml workflow should exist"

    def test_docker_workflow_exists(self):
        """Test that Docker workflow exists."""
        workflow = Path(__file__).parent.parent / ".github" / "workflows" / "docker.yml"
        assert workflow.exists(), "docker.yml workflow should exist"

    def test_security_workflow_exists(self):
        """Test that security workflow exists."""
        workflow = (
            Path(__file__).parent.parent / ".github" / "workflows" / "security.yml"
        )
        assert workflow.exists(), "security.yml workflow should exist"

    def test_release_workflow_exists(self):
        """Test that release workflow exists."""
        workflow = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        assert workflow.exists(), "release.yml workflow should exist"

    def test_docker_workflow_valid_yaml(self):
        """Test that Docker workflow is valid YAML."""
        workflow = Path(__file__).parent.parent / ".github" / "workflows" / "docker.yml"
        with open(workflow) as f:
            data = yaml.safe_load(f)
        assert "name" in data
        # Note: 'on' is parsed as True by YAML parser due to boolean conversion
        assert True in data or "on" in data
        assert "jobs" in data
        assert "build-and-push" in data["jobs"]

    def test_docker_workflow_has_security_scan(self):
        """Test that Docker workflow includes security scanning."""
        workflow = Path(__file__).parent.parent / ".github" / "workflows" / "docker.yml"
        with open(workflow) as f:
            data = yaml.safe_load(f)
        assert "scan-security" in data["jobs"], "Should have security scan job"


class TestHelmChart:
    """Test Helm chart configuration."""

    def test_helm_chart_exists(self):
        """Test that Helm chart exists."""
        chart_dir = Path(__file__).parent.parent / "deployment" / "helm" / "accelerapp"
        assert chart_dir.exists(), "Helm chart directory should exist"

    def test_chart_yaml_exists(self):
        """Test that Chart.yaml exists."""
        chart_yaml = (
            Path(__file__).parent.parent
            / "deployment"
            / "helm"
            / "accelerapp"
            / "Chart.yaml"
        )
        assert chart_yaml.exists(), "Chart.yaml should exist"

    def test_values_yaml_exists(self):
        """Test that values.yaml exists."""
        values_yaml = (
            Path(__file__).parent.parent
            / "deployment"
            / "helm"
            / "accelerapp"
            / "values.yaml"
        )
        assert values_yaml.exists(), "values.yaml should exist"

    def test_chart_yaml_valid(self):
        """Test that Chart.yaml is valid."""
        chart_yaml = (
            Path(__file__).parent.parent
            / "deployment"
            / "helm"
            / "accelerapp"
            / "Chart.yaml"
        )
        with open(chart_yaml) as f:
            data = yaml.safe_load(f)
        assert "apiVersion" in data
        assert "name" in data
        assert data["name"] == "accelerapp"
        assert "version" in data

    def test_helm_templates_exist(self):
        """Test that Helm templates exist."""
        templates_dir = (
            Path(__file__).parent.parent
            / "deployment"
            / "helm"
            / "accelerapp"
            / "templates"
        )
        assert templates_dir.exists(), "templates directory should exist"

        # Check for key template files
        assert (templates_dir / "deployment.yaml").exists()
        assert (templates_dir / "service.yaml").exists()
        assert (templates_dir / "hpa.yaml").exists()


class TestDeploymentDocumentation:
    """Test deployment documentation."""

    def test_deployment_readme_exists(self):
        """Test that main deployment README exists."""
        readme = Path(__file__).parent.parent / "deployment" / "README.md"
        assert readme.exists(), "deployment/README.md should exist"

    def test_deployment_md_exists(self):
        """Test that DEPLOYMENT.md exists."""
        deployment_md = Path(__file__).parent.parent / "DEPLOYMENT.md"
        assert deployment_md.exists(), "DEPLOYMENT.md should exist"

    def test_helm_readme_exists(self):
        """Test that Helm chart README exists."""
        readme = (
            Path(__file__).parent.parent
            / "deployment"
            / "helm"
            / "accelerapp"
            / "README.md"
        )
        assert readme.exists(), "Helm chart README.md should exist"


class TestMonitoringService:
    """Test monitoring service components."""

    def test_health_check_script_exists(self):
        """Test that health check script exists."""
        script = (
            Path(__file__).parent.parent
            / "deployment"
            / "monitoring"
            / "health_check.py"
        )
        assert script.exists(), "health_check.py should exist"

    def test_monitor_script_exists(self):
        """Test that monitor service script exists."""
        script = Path(__file__).parent.parent / "deployment" / "monitoring" / "monitor.py"
        assert script.exists(), "monitor.py should exist"

    def test_health_check_script_executable(self):
        """Test that health check script has proper imports."""
        script = (
            Path(__file__).parent.parent
            / "deployment"
            / "monitoring"
            / "health_check.py"
        )
        with open(script) as f:
            content = f.read()
        assert "def get_system_health()" in content
        assert "def check_python_environment()" in content
        # Check for the function definition (may have parameters)
        assert "def check_llm_service" in content

    def test_monitor_script_has_http_server(self):
        """Test that monitor script has HTTP server."""
        script = Path(__file__).parent.parent / "deployment" / "monitoring" / "monitor.py"
        with open(script) as f:
            content = f.read()
        assert "HTTPServer" in content or "http.server" in content
        assert "/health" in content
        assert "/metrics" in content
