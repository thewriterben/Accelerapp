"""
Tests for agent system.
"""

import pytest
from pathlib import Path


def test_base_agent_import():
    """Test base agent import."""
    from accelerapp.agents.base_agent import BaseAgent
    assert BaseAgent is not None


def test_agent_orchestrator_import():
    """Test orchestrator import."""
    from accelerapp.agents.orchestrator import AgentOrchestrator
    assert AgentOrchestrator is not None


def test_orchestrator_registration():
    """Test agent registration."""
    from accelerapp.agents.orchestrator import AgentOrchestrator
    from accelerapp.agents.base_agent import BaseAgent
    
    class TestAgent(BaseAgent):
        def generate(self, spec, context):
            return "test output"
    
    orchestrator = AgentOrchestrator()
    agent = TestAgent("test-agent", ["test"])
    
    orchestrator.register_agent(agent)
    assert len(orchestrator.agents) == 1
    assert orchestrator.agents[0].name == "test-agent"


def test_orchestrator_find_agent():
    """Test finding appropriate agent."""
    from accelerapp.agents.orchestrator import AgentOrchestrator
    from accelerapp.agents.base_agent import BaseAgent
    
    class TestAgent(BaseAgent):
        def generate(self, spec, context):
            return "test output"
    
    orchestrator = AgentOrchestrator()
    agent = TestAgent("test-agent", ["firmware", "software"])
    orchestrator.register_agent(agent)
    
    found_agent = orchestrator.find_agent("firmware")
    assert found_agent is not None
    assert found_agent.name == "test-agent"
    
    not_found = orchestrator.find_agent("unknown")
    assert not_found is None
