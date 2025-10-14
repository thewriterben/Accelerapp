"""
Tests for Phase 2 service layer.
"""

import pytest
from accelerapp.services import (
    HardwareService,
    AIService,
    WorkflowService,
    MonitoringService,
)
from accelerapp.services.workflow_service import Workflow


class MockAgent:
    """Mock AI agent for testing."""

    def can_handle(self, task):
        return "test" in task.lower()

    def generate(self, spec, context=None):
        return {"status": "success", "result": "generated"}

    def get_info(self):
        return {"name": "MockAgent", "version": "1.0"}


class TestHardwareService:
    """Test hardware service."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and shutdown."""
        service = HardwareService()

        await service.initialize()
        assert service.is_initialized

        await service.shutdown()
        assert not service.is_initialized

    @pytest.mark.asyncio
    async def test_register_device(self):
        """Test device registration."""
        service = HardwareService()
        await service.initialize()

        device_info = {"type": "sensor", "model": "BME280"}
        service.register_device("device1", device_info)

        retrieved = service.get_device("device1")
        assert retrieved == device_info

    @pytest.mark.asyncio
    async def test_list_devices(self):
        """Test listing devices."""
        service = HardwareService()
        await service.initialize()

        service.register_device("device1", {"type": "sensor"})
        service.register_device("device2", {"type": "actuator"})

        devices = service.list_devices()
        assert len(devices) == 2
        assert "device1" in devices
        assert "device2" in devices

    @pytest.mark.asyncio
    async def test_remove_device(self):
        """Test removing device."""
        service = HardwareService()
        await service.initialize()

        service.register_device("device1", {"type": "sensor"})
        assert service.remove_device("device1") is True
        assert service.get_device("device1") is None

    @pytest.mark.asyncio
    async def test_health_status(self):
        """Test service health status."""
        service = HardwareService()
        await service.initialize()

        service.register_device("device1", {"type": "sensor"})

        health = service.get_health()
        assert health["status"] == "healthy"
        assert health["registered_devices"] == 1


class TestAIService:
    """Test AI service."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and shutdown."""
        service = AIService()

        await service.initialize()
        assert service.is_initialized

        await service.shutdown()
        assert not service.is_initialized

    @pytest.mark.asyncio
    async def test_register_agent(self):
        """Test agent registration."""
        service = AIService()
        await service.initialize()

        agent = MockAgent()
        service.register_agent("agent1", agent)

        retrieved = service.get_agent("agent1")
        assert retrieved is agent

    @pytest.mark.asyncio
    async def test_list_agents(self):
        """Test listing agents."""
        service = AIService()
        await service.initialize()

        service.register_agent("agent1", MockAgent())
        service.register_agent("agent2", MockAgent())

        agents = service.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents

    @pytest.mark.asyncio
    async def test_find_agent_for_task(self):
        """Test finding agent for task."""
        service = AIService()
        await service.initialize()

        agent = MockAgent()
        service.register_agent("agent1", agent)

        found = service.find_agent_for_task("test task")
        assert found is agent

        not_found = service.find_agent_for_task("other task")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test generating with agent."""
        service = AIService()
        await service.initialize()

        agent = MockAgent()
        service.register_agent("agent1", agent)

        result = service.generate("agent1", {"input": "test"})
        assert result["status"] == "success"


class TestWorkflowService:
    """Test workflow service."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and shutdown."""
        service = WorkflowService()

        await service.initialize()
        assert service.is_initialized

        await service.shutdown()
        assert not service.is_initialized

    @pytest.mark.asyncio
    async def test_register_workflow(self):
        """Test workflow registration."""
        service = WorkflowService()
        await service.initialize()

        workflow = Workflow("test_workflow", "Test workflow")
        service.register_workflow(workflow)

        retrieved = service.get_workflow("test_workflow")
        assert retrieved is workflow

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test workflow execution."""
        service = WorkflowService()
        await service.initialize()

        workflow = Workflow("test_workflow")
        workflow.add_step("step1", lambda ctx: {"value": 10})
        workflow.add_step("step2", lambda ctx: {"value": ctx.get("value", 0) * 2})

        service.register_workflow(workflow)

        result = service.execute_workflow("test_workflow")
        assert result["workflow"] == "test_workflow"
        assert result["steps_completed"] == 2

    @pytest.mark.asyncio
    async def test_list_workflows(self):
        """Test listing workflows."""
        service = WorkflowService()
        await service.initialize()

        workflow1 = Workflow("workflow1")
        workflow2 = Workflow("workflow2")

        service.register_workflow(workflow1)
        service.register_workflow(workflow2)

        workflows = service.list_workflows()
        assert len(workflows) == 2
        assert "workflow1" in workflows
        assert "workflow2" in workflows


class TestMonitoringService:
    """Test monitoring service."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and shutdown."""
        service = MonitoringService()

        await service.initialize()
        assert service.is_initialized

        await service.shutdown()
        assert not service.is_initialized

    @pytest.mark.asyncio
    async def test_get_all_metrics(self):
        """Test getting all metrics."""
        service = MonitoringService()
        await service.initialize()

        metrics = service.get_all_metrics()
        assert "uptime_seconds" in metrics
        assert "counters" in metrics
        assert "gauges" in metrics

    @pytest.mark.asyncio
    async def test_get_health_status(self):
        """Test getting health status."""
        service = MonitoringService()
        await service.initialize()

        health = service.get_health_status()
        assert "status" in health
        assert "checks" in health

    @pytest.mark.asyncio
    async def test_register_health_check(self):
        """Test registering health check."""
        service = MonitoringService()
        await service.initialize()

        service.register_health_check("test_check", lambda: True, critical=True)

        health = service.get_health_status()
        check_names = [check["name"] for check in health["checks"]]
        assert "test_check" in check_names

    @pytest.mark.asyncio
    async def test_record_metric(self):
        """Test recording metrics."""
        service = MonitoringService()
        await service.initialize()

        service.record_metric("counter", "test_counter", 1)
        service.record_metric("gauge", "test_gauge", 42.0)
        service.record_metric("histogram", "test_histogram", 1.5)

        metrics = service.get_all_metrics()
        assert metrics["counters"]["test_counter"] == 1
        assert metrics["gauges"]["test_gauge"] == 42.0
