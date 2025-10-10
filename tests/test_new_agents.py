"""
Tests for new specialized agents (AI and Firmware agents).
"""

import pytest


def test_ai_agent_import():
    """Test AI agent can be imported."""
    from accelerapp.agents import AIAgent
    assert AIAgent is not None


def test_ai_agent_initialization():
    """Test AI agent initialization."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    assert agent.name == "AI Agent"
    assert len(agent.capabilities) > 0
    assert 'code_optimization' in agent.capabilities


def test_ai_agent_can_handle():
    """Test AI agent task handling."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    
    assert agent.can_handle('code_optimization')
    assert agent.can_handle('architecture_analysis')
    assert not agent.can_handle('unrelated_task')


def test_ai_agent_code_optimization():
    """Test AI agent code optimization."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    
    spec = {
        'task_type': 'optimize',
        'code': 'void loop() { delay(1000); Serial.println("test"); }',
        'platform': 'arduino',
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'optimizations' in result
    assert result['count'] >= 0


def test_ai_agent_architecture_analysis():
    """Test AI agent architecture analysis."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    
    spec = {
        'task_type': 'analyze',
        'peripherals': [
            {'type': 'led', 'pin': 13},
            {'type': 'button', 'pin': 2},
            {'type': 'sensor', 'pin': 'A0'},
        ],
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    assert 'complexity' in result['analysis']


def test_ai_agent_code_review():
    """Test AI agent code review."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    
    spec = {
        'task_type': 'review',
        'code': 'void setup() { } void loop() { }',
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'issues' in result
    assert 'suggestions' in result


def test_ai_agent_pattern_suggestions():
    """Test AI agent design pattern suggestions."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    
    spec = {
        'task_type': 'suggest_patterns',
        'peripherals': [
            {'type': 'sensor'},
            {'type': 'sensor'},
            {'type': 'led'},
            {'type': 'button'},
        ],
        'platform': 'arduino',
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'patterns' in result
    assert result['count'] >= 0


def test_ai_agent_get_info():
    """Test AI agent info."""
    from accelerapp.agents import AIAgent
    
    agent = AIAgent()
    info = agent.get_info()
    
    assert info['name'] == "AI Agent"
    assert info['type'] == 'ai_agent'
    assert len(info['capabilities']) > 0


def test_firmware_agent_import():
    """Test firmware agent can be imported."""
    from accelerapp.agents import FirmwareAgent
    assert FirmwareAgent is not None


def test_firmware_agent_initialization():
    """Test firmware agent initialization."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    assert agent.name == "Firmware Agent"
    assert len(agent.capabilities) > 0
    assert 'firmware_generation' in agent.capabilities


def test_firmware_agent_can_handle():
    """Test firmware agent task handling."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    
    assert agent.can_handle('firmware generation')
    assert agent.can_handle('embedded systems')
    assert agent.can_handle('microcontroller programming')
    assert not agent.can_handle('web development')


def test_firmware_agent_platform_support():
    """Test firmware agent platform support."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    support = agent.get_platform_support()
    
    assert 'arduino' in support
    assert 'esp32' in support
    assert 'stm32' in support


def test_firmware_agent_optimization():
    """Test firmware agent optimization."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    
    spec = {
        'task_type': 'optimize',
        'code': 'String msg = "hello"; delay(1000);',
        'platform': 'arduino',
        'peripherals': [{'type': 'button'}],
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'optimizations' in result
    assert result['agent'] == 'Firmware Agent'


def test_firmware_agent_analysis():
    """Test firmware agent analysis."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    
    spec = {
        'task_type': 'analyze',
        'platform': 'esp32',
        'peripherals': [
            {'type': 'led'},
            {'type': 'sensor'},
        ],
    }
    
    result = agent.generate(spec)
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    assert result['analysis']['platform'] == 'esp32'


def test_firmware_agent_get_info():
    """Test firmware agent info."""
    from accelerapp.agents import FirmwareAgent
    
    agent = FirmwareAgent()
    info = agent.get_info()
    
    assert info['name'] == "Firmware Agent"
    assert info['type'] == 'firmware_agent'
    assert 'platform_expertise' in info


def test_agents_integration():
    """Test that new agents work with existing agent system."""
    from accelerapp.agents import AgentOrchestrator, AIAgent, FirmwareAgent
    
    orchestrator = AgentOrchestrator()
    
    ai_agent = AIAgent()
    firmware_agent = FirmwareAgent()
    
    orchestrator.register_agent(ai_agent)
    orchestrator.register_agent(firmware_agent)
    
    # Find agent for code optimization
    agent = orchestrator.find_agent('code_optimization')
    assert agent is not None
    
    # Find agent for firmware generation
    agent = orchestrator.find_agent('firmware_generation')
    assert agent is not None
