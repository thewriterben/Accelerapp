"""
Tests for AI enhancement module.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from accelerapp.ai import (
    AIModelVersionManager,
    ABTestingFramework,
    AdvancedPromptEngine,
    ModelPerformanceAnalyzer,
    AgentSwarmOrchestrator,
)
from accelerapp.ai.swarm_orchestrator import AgentRole


class TestAIModelVersionManager:
    """Test AI model version management."""
    
    def test_register_version(self):
        """Test registering a new model version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            version = manager.register_version(
                name="test_model",
                version="1.0.0",
                performance_metrics={"accuracy": 0.95},
                metadata={"type": "classification"}
            )
            
            assert version.name == "test_model"
            assert version.version == "1.0.0"
            assert version.performance_metrics["accuracy"] == 0.95
    
    def test_set_active_version(self):
        """Test setting active version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            manager.register_version("model", "1.0.0")
            manager.register_version("model", "2.0.0")
            
            assert manager.set_active_version("model", "2.0.0")
            active = manager.get_active_version("model")
            assert active.version == "2.0.0"
    
    def test_rollback(self):
        """Test rolling back to previous version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            manager.register_version("model", "1.0.0")
            manager.register_version("model", "2.0.0")
            manager.set_active_version("model", "2.0.0")
            
            assert manager.rollback("model")
            active = manager.get_active_version("model")
            assert active.version == "1.0.0"
    
    def test_list_versions(self):
        """Test listing model versions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            manager.register_version("model", "1.0.0")
            manager.register_version("model", "2.0.0")
            
            versions = manager.list_versions("model")
            assert len(versions) == 2
    
    def test_update_performance_metrics(self):
        """Test updating performance metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            manager.register_version("model", "1.0.0", {"accuracy": 0.9})
            assert manager.update_performance_metrics("model", "1.0.0", {"accuracy": 0.95})
            
            version = manager.get_active_version("model")
            assert version.performance_metrics["accuracy"] == 0.95
    
    def test_deprecate_version(self):
        """Test deprecating a version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AIModelVersionManager(Path(tmpdir))
            
            manager.register_version("model", "1.0.0")
            assert manager.deprecate_version("model", "1.0.0")
            
            versions = manager.list_versions("model")
            assert versions[0].status == "deprecated"


class TestABTestingFramework:
    """Test A/B testing framework."""
    
    def test_create_test(self):
        """Test creating an A/B test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestingFramework(Path(tmpdir))
            
            test = framework.create_test(
                test_id="test1",
                name="Agent Config Test",
                description="Test different agent configurations",
                variants=[
                    {"name": "variant_a", "config": {"param": 1}},
                    {"name": "variant_b", "config": {"param": 2}}
                ]
            )
            
            assert test.test_id == "test1"
            assert len(test.variants) == 2
    
    def test_select_variant(self):
        """Test variant selection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestingFramework(Path(tmpdir))
            
            framework.create_test(
                test_id="test1",
                name="Test",
                description="Test",
                variants=[
                    {"name": "a", "config": {}},
                    {"name": "b", "config": {}}
                ]
            )
            
            variant = framework.select_variant("test1")
            assert variant is not None
            assert variant.name in ["a", "b"]
    
    def test_record_metric(self):
        """Test recording metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestingFramework(Path(tmpdir))
            
            framework.create_test(
                test_id="test1",
                name="Test",
                description="Test",
                variants=[{"name": "a", "config": {}}]
            )
            
            assert framework.record_metric("test1", "a", "latency", 0.5)
            
            results = framework.get_results("test1")
            assert results is not None
            assert results["total_samples"] == 1
    
    def test_get_results(self):
        """Test getting test results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestingFramework(Path(tmpdir))
            
            framework.create_test(
                test_id="test1",
                name="Test",
                description="Test",
                variants=[
                    {"name": "a", "config": {}},
                    {"name": "b", "config": {}}
                ]
            )
            
            framework.record_metric("test1", "a", "accuracy", 0.9)
            framework.record_metric("test1", "b", "accuracy", 0.85)
            
            results = framework.get_results("test1")
            assert len(results["variants"]) == 2
    
    def test_statistical_significance(self):
        """Test statistical significance calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestingFramework(Path(tmpdir))
            
            framework.create_test(
                test_id="test1",
                name="Test",
                description="Test",
                variants=[
                    {"name": "a", "config": {}},
                    {"name": "b", "config": {}}
                ]
            )
            
            framework.record_metric("test1", "a", "score", 0.9)
            framework.record_metric("test1", "b", "score", 0.7)
            
            significance = framework.calculate_statistical_significance("test1", "score")
            assert significance is not None


class TestAdvancedPromptEngine:
    """Test advanced prompt engine."""
    
    def test_get_template(self):
        """Test getting a template."""
        engine = AdvancedPromptEngine()
        
        template = engine.get_template("code_generation")
        assert template is not None
        assert template.name == "code_generation"
    
    def test_render_prompt(self):
        """Test rendering a prompt."""
        engine = AdvancedPromptEngine()
        
        prompt = engine.render_prompt(
            "code_generation",
            {
                "language": "Python",
                "purpose": "data processing",
                "requirements": "Fast and efficient",
                "platform": "Linux",
                "constraints": "Low memory"
            }
        )
        
        assert prompt is not None
        assert "Python" in prompt
        assert "data processing" in prompt
    
    def test_list_templates(self):
        """Test listing templates."""
        engine = AdvancedPromptEngine()
        
        templates = engine.list_templates()
        assert len(templates) > 0
        
        gen_templates = engine.list_templates(category="generation")
        assert all(t.category == "generation" for t in gen_templates)
    
    def test_optimize_prompt(self):
        """Test prompt optimization."""
        engine = AdvancedPromptEngine()
        
        prompt = engine.optimize_prompt(
            "code_generation",
            {
                "language": "C++",
                "purpose": "real-time control",
                "requirements": "Low latency",
                "platform": "ARM",
                "constraints": "Limited CPU"
            },
            optimization_goal="clarity"
        )
        
        assert prompt is not None
        assert "clear" in prompt.lower()
    
    def test_validate_variables(self):
        """Test variable validation."""
        engine = AdvancedPromptEngine()
        
        result = engine.validate_variables(
            "code_generation",
            {"language": "Python", "purpose": "test"}
        )
        
        assert not result["valid"]
        assert len(result["missing_variables"]) > 0


class TestModelPerformanceAnalyzer:
    """Test model performance analyzer."""
    
    def test_record_performance(self):
        """Test recording performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ModelPerformanceAnalyzer(Path(tmpdir))
            
            analyzer.record_performance(
                "test_agent",
                "generation",
                {"latency": 0.5, "accuracy": 0.9}
            )
            
            stats = analyzer.get_agent_performance("test_agent")
            assert stats["total_measurements"] == 1
    
    def test_get_agent_performance(self):
        """Test getting agent performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ModelPerformanceAnalyzer(Path(tmpdir))
            
            analyzer.record_performance("agent", "task", {"score": 0.8})
            analyzer.record_performance("agent", "task", {"score": 0.9})
            
            stats = analyzer.get_agent_performance("agent")
            assert stats["metrics"]["score"]["count"] == 2
            assert abs(stats["metrics"]["score"]["mean"] - 0.85) < 0.01
    
    def test_compare_agents(self):
        """Test comparing agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ModelPerformanceAnalyzer(Path(tmpdir))
            
            analyzer.record_performance("agent1", "task", {"speed": 1.0})
            analyzer.record_performance("agent2", "task", {"speed": 2.0})
            
            comparison = analyzer.compare_agents(["agent1", "agent2"], "speed")
            assert comparison["best_agent"] in ["agent1", "agent2"]
    
    def test_get_trend(self):
        """Test getting performance trend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ModelPerformanceAnalyzer(Path(tmpdir))
            
            analyzer.record_performance("agent", "task", {"metric": 0.8})
            analyzer.record_performance("agent", "task", {"metric": 0.9})
            
            trend = analyzer.get_trend("agent", "metric")
            assert trend["trend"] in ["improving", "degrading", "stable"]


class TestAgentSwarmOrchestrator:
    """Test agent swarm orchestrator."""
    
    def test_register_agent(self):
        """Test registering an agent."""
        orchestrator = AgentSwarmOrchestrator()
        
        def callback(task):
            pass
        
        orchestrator.register_agent(
            "agent1",
            AgentRole.WORKER,
            ["code_generation"],
            callback
        )
        
        assert "agent1" in orchestrator.agents
    
    def test_submit_task(self):
        """Test submitting a task."""
        orchestrator = AgentSwarmOrchestrator()
        
        def callback(task):
            pass
        
        orchestrator.register_agent(
            "agent1",
            AgentRole.WORKER,
            ["coding"],
            callback
        )
        
        task = orchestrator.submit_task(
            "task1",
            "generation",
            {"code": "test"},
            ["coding"]
        )
        
        assert task.task_id == "task1"
    
    def test_complete_task(self):
        """Test completing a task."""
        orchestrator = AgentSwarmOrchestrator()
        
        def callback(task):
            pass
        
        orchestrator.register_agent(
            "agent1",
            AgentRole.WORKER,
            ["test"],
            callback
        )
        
        orchestrator.submit_task(
            "task1",
            "test",
            {},
            ["test"]
        )
        
        assert orchestrator.complete_task("task1", {"result": "success"})
        
        status = orchestrator.get_task_status("task1")
        assert status["status"] == "completed"
    
    def test_get_swarm_status(self):
        """Test getting swarm status."""
        orchestrator = AgentSwarmOrchestrator()
        
        def callback(task):
            pass
        
        orchestrator.register_agent(
            "agent1",
            AgentRole.WORKER,
            ["test"],
            callback
        )
        
        status = orchestrator.get_swarm_status()
        assert status["total_agents"] == 1
    
    def test_coordinate_complex_task(self):
        """Test coordinating complex task."""
        orchestrator = AgentSwarmOrchestrator()
        
        def callback(task):
            pass
        
        orchestrator.register_agent(
            "agent1",
            AgentRole.COORDINATOR,
            ["test"],
            callback
        )
        
        result = orchestrator.coordinate_complex_task(
            "Complex task",
            [
                {"type": "subtask1", "capabilities": ["test"]},
                {"type": "subtask2", "capabilities": ["test"]}
            ]
        )
        
        assert len(result["subtasks"]) == 2
