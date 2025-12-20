"""
Tests for Meshtastic agent and mesh networking functionality.
"""

import pytest
from pathlib import Path
from accelerapp.agents import MeshtasticAgent


class TestMeshtasticAgent:
    """Test suite for MeshtasticAgent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MeshtasticAgent()
        assert agent.name == "Meshtastic Agent"
        assert "meshtastic_generation" in agent.capabilities

    def test_agent_can_handle_meshtastic_task(self):
        """Test that agent can handle meshtastic-related tasks."""
        agent = MeshtasticAgent()
        assert agent.can_handle("meshtastic node setup")
        assert agent.can_handle("mesh network configuration")
        assert agent.can_handle("lora communication")
        assert not agent.can_handle("web development")

    def test_agent_generate_project(self):
        """Test project generation."""
        agent = MeshtasticAgent()
        spec = {
            "task_type": "generate",
            "device_name": "TestNode",
            "platform": "esp32",
            "region": "US",
            "features": ["wifi", "gps"],
        }

        result = agent.generate(spec)

        assert result["status"] == "success"
        assert result["device_name"] == "TestNode"
        assert "files" in result
        assert "config.yaml" in result["files"]
        assert "platformio.ini" in result["files"]

    def test_agent_configure_node(self):
        """Test node configuration."""
        agent = MeshtasticAgent()
        spec = {
            "task_type": "configure",
            "node_id": "!12345678",
            "channel": "LongFast",
            "region": "EU",
        }

        result = agent.generate(spec)

        assert result["status"] == "success"
        assert "configuration" in result
        assert result["configuration"]["region"] == "EU"

    def test_agent_analyze_network(self):
        """Test network analysis."""
        agent = MeshtasticAgent()
        spec = {
            "task_type": "analyze",
            "nodes": [
                {"id": "!11111111"},
                {"id": "!22222222"},
                {"id": "!33333333"},
            ],
        }

        result = agent.generate(spec)

        assert result["status"] == "success"
        assert "analysis" in result
        assert result["analysis"]["node_count"] == 3

    def test_agent_get_info(self):
        """Test agent info retrieval."""
        agent = MeshtasticAgent()
        info = agent.get_info()

        assert info["name"] == "Meshtastic Agent"
        assert "supported_hardware" in info
        assert "regions" in info
        assert "US" in info["regions"]

    def test_agent_supported_regions(self):
        """Test supported regional configurations."""
        agent = MeshtasticAgent()
        assert "US" in agent.regions
        assert "EU" in agent.regions
        assert agent.regions["US"]["frequency"] == 915.0
        assert agent.regions["EU"]["frequency"] == 868.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
