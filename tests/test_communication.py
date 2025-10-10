"""
Tests for communication module.
"""

import pytest
import time
from threading import Thread


def test_message_bus_import():
    """Test message bus import."""
    from accelerapp.communication import MessageBus, Message, MessagePriority
    assert MessageBus is not None
    assert Message is not None
    assert MessagePriority is not None


def test_agent_coordinator_import():
    """Test agent coordinator import."""
    from accelerapp.communication import AgentCoordinator, CoordinationStrategy
    assert AgentCoordinator is not None
    assert CoordinationStrategy is not None


def test_shared_context_import():
    """Test shared context import."""
    from accelerapp.communication import SharedContext, ContextScope
    assert SharedContext is not None
    assert ContextScope is not None


def test_collaboration_protocols_import():
    """Test collaboration protocols import."""
    from accelerapp.communication import CollaborationProtocol, ProtocolType
    assert CollaborationProtocol is not None
    assert ProtocolType is not None


def test_message_creation():
    """Test message creation."""
    from accelerapp.communication import Message, MessagePriority
    
    msg = Message(
        sender="test-agent",
        topic="test.topic",
        content="test content",
        priority=MessagePriority.HIGH
    )
    
    assert msg.sender == "test-agent"
    assert msg.topic == "test.topic"
    assert msg.content == "test content"
    assert msg.priority == MessagePriority.HIGH
    assert msg.message_id is not None


def test_message_bus_initialization():
    """Test message bus initialization."""
    from accelerapp.communication import MessageBus
    
    bus = MessageBus()
    assert bus is not None
    assert bus.subscribers == {}
    assert not bus._running


def test_message_bus_subscribe():
    """Test subscribing to topics."""
    from accelerapp.communication import MessageBus
    
    bus = MessageBus()
    received = []
    
    def handler(msg):
        received.append(msg)
    
    bus.subscribe("test.topic", handler)
    assert "test.topic" in bus.subscribers
    assert len(bus.subscribers["test.topic"]) == 1


def test_message_bus_publish_and_receive():
    """Test publishing and receiving messages."""
    from accelerapp.communication import MessageBus
    
    bus = MessageBus()
    received = []
    
    def handler(msg):
        received.append(msg)
    
    bus.subscribe("test.topic", handler)
    bus.start()
    
    msg_id = bus.publish(
        sender="test-agent",
        topic="test.topic",
        content="test message"
    )
    
    # Give worker thread time to process
    time.sleep(0.2)
    
    assert len(received) == 1
    assert received[0].content == "test message"
    
    bus.stop()


def test_message_bus_unsubscribe():
    """Test unsubscribing from topics."""
    from accelerapp.communication import MessageBus
    
    bus = MessageBus()
    
    def handler(msg):
        pass
    
    bus.subscribe("test.topic", handler)
    assert "test.topic" in bus.subscribers
    
    result = bus.unsubscribe("test.topic", handler)
    assert result is True
    assert "test.topic" not in bus.subscribers


def test_message_bus_history():
    """Test message history."""
    from accelerapp.communication import MessageBus
    
    bus = MessageBus()
    
    bus.publish("agent1", "topic1", "msg1")
    bus.publish("agent2", "topic2", "msg2")
    
    history = bus.get_history()
    assert len(history) == 2
    
    # Filter by topic
    topic1_history = bus.get_history(topic="topic1")
    assert len(topic1_history) == 1
    assert topic1_history[0].content == "msg1"


def test_agent_coordinator_initialization():
    """Test agent coordinator initialization."""
    from accelerapp.communication import AgentCoordinator
    
    coordinator = AgentCoordinator()
    assert coordinator is not None
    assert coordinator.agents == {}


def test_agent_coordinator_register():
    """Test agent registration."""
    from accelerapp.communication import AgentCoordinator
    
    coordinator = AgentCoordinator()
    coordinator.register_agent(
        agent_id="agent1",
        name="Test Agent",
        capabilities=["firmware", "software"]
    )
    
    assert "agent1" in coordinator.agents
    assert coordinator.agents["agent1"].name == "Test Agent"
    assert coordinator.agents["agent1"].status == "idle"


def test_agent_coordinator_find_capable():
    """Test finding capable agents."""
    from accelerapp.communication import AgentCoordinator
    
    coordinator = AgentCoordinator()
    coordinator.register_agent("agent1", "Agent 1", ["firmware"])
    coordinator.register_agent("agent2", "Agent 2", ["software"])
    
    firmware_agent = coordinator.find_capable_agent("firmware")
    assert firmware_agent is not None
    assert firmware_agent.agent_id == "agent1"
    
    ui_agent = coordinator.find_capable_agent("ui")
    assert ui_agent is None


def test_agent_coordinator_task_assignment():
    """Test task assignment."""
    from accelerapp.communication import AgentCoordinator
    
    coordinator = AgentCoordinator()
    coordinator.register_agent("agent1", "Agent 1", ["firmware"])
    
    result = coordinator.assign_task(
        task_id="task1",
        agent_id="agent1",
        task_data={"type": "firmware"}
    )
    
    assert result is True
    assert coordinator.agents["agent1"].status == "busy"
    assert coordinator.agents["agent1"].current_task == "task1"


def test_agent_coordinator_complete_task():
    """Test task completion."""
    from accelerapp.communication import AgentCoordinator
    
    coordinator = AgentCoordinator()
    coordinator.register_agent("agent1", "Agent 1", ["firmware"])
    coordinator.assign_task("task1", "agent1", {})
    
    coordinator.complete_task("task1", "agent1", {"status": "success"})
    
    assert coordinator.agents["agent1"].status == "idle"
    assert coordinator.agents["agent1"].tasks_completed == 1
    assert len(coordinator.completed_tasks) == 1


def test_shared_context_initialization():
    """Test shared context initialization."""
    from accelerapp.communication import SharedContext
    
    context = SharedContext()
    assert context is not None


def test_shared_context_set_get():
    """Test setting and getting context values."""
    from accelerapp.communication import SharedContext, ContextScope
    
    context = SharedContext()
    context.set("key1", "value1", ContextScope.GLOBAL)
    
    value = context.get("key1", ContextScope.GLOBAL)
    assert value == "value1"


def test_shared_context_scopes():
    """Test different context scopes."""
    from accelerapp.communication import SharedContext, ContextScope
    
    context = SharedContext()
    
    context.set("global_key", "global_value", ContextScope.GLOBAL)
    context.set("task_key", "task_value", ContextScope.TASK, "task1")
    context.set("agent_key", "agent_value", ContextScope.AGENT, "agent1")
    
    assert context.get("global_key", ContextScope.GLOBAL) == "global_value"
    assert context.get("task_key", ContextScope.TASK, "task1") == "task_value"
    assert context.get("agent_key", ContextScope.AGENT, "agent1") == "agent_value"


def test_shared_context_update():
    """Test updating multiple values."""
    from accelerapp.communication import SharedContext, ContextScope
    
    context = SharedContext()
    context.update({
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }, ContextScope.GLOBAL)
    
    assert context.get("key1", ContextScope.GLOBAL) == "value1"
    assert context.get("key2", ContextScope.GLOBAL) == "value2"
    assert context.get("key3", ContextScope.GLOBAL) == "value3"


def test_shared_context_delete():
    """Test deleting context values."""
    from accelerapp.communication import SharedContext, ContextScope
    
    context = SharedContext()
    context.set("key1", "value1", ContextScope.GLOBAL)
    
    result = context.delete("key1", ContextScope.GLOBAL)
    assert result is True
    
    value = context.get("key1", ContextScope.GLOBAL)
    assert value is None


def test_collaboration_protocol_creation():
    """Test collaboration protocol creation."""
    from accelerapp.communication import CollaborationProtocol, ProtocolType
    
    protocol = CollaborationProtocol(ProtocolType.REQUEST_RESPONSE)
    assert protocol is not None
    assert protocol.protocol_type == ProtocolType.REQUEST_RESPONSE


def test_request_response_protocol():
    """Test request-response protocol."""
    from accelerapp.communication.collaboration_protocols import RequestResponseProtocol
    
    protocol = RequestResponseProtocol()
    result = protocol.execute({
        "requester": "agent1",
        "request_type": "firmware",
        "data": {}
    })
    
    assert result is not None
    assert result["status"] == "received"


def test_consensus_protocol():
    """Test consensus protocol."""
    from accelerapp.communication.collaboration_protocols import ConsensusProtocol
    
    protocol = ConsensusProtocol(threshold=0.66)
    
    # 2/3 agree = consensus reached
    assert protocol.calculate_consensus([True, True, False]) is True
    
    # 1/3 agree = no consensus
    assert protocol.calculate_consensus([True, False, False]) is False


def test_protocol_factory():
    """Test protocol factory."""
    from accelerapp.communication.collaboration_protocols import create_protocol, ProtocolType
    from accelerapp.communication.collaboration_protocols import RequestResponseProtocol
    
    protocol = create_protocol(ProtocolType.REQUEST_RESPONSE)
    assert isinstance(protocol, RequestResponseProtocol)
