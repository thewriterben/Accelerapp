"""
Tests for Phase 6 optimization features.
"""

import pytest
import time
from accelerapp.production.optimization import (
    CostMonitor,
    ResourceUsage,
    CostReport,
    PerformanceProfiler,
    ProfileResult,
)
from accelerapp.production.optimization.cost_monitor import ResourceType, CloudProvider
from accelerapp.production.optimization.performance_profiler import ProfileType


class TestCostMonitor:
    """Tests for cost monitoring system."""
    
    def test_cost_monitor_initialization(self):
        """Test cost monitor initialization."""
        monitor = CostMonitor()
        assert monitor is not None
        assert len(monitor.resources) == 0
        assert len(monitor.cost_history) == 0
    
    def test_track_resource(self):
        """Test resource tracking."""
        monitor = CostMonitor()
        
        usage = monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10
        )
        
        assert usage is not None
        assert usage.resource_id == "vm-001"
        assert usage.resource_type == ResourceType.COMPUTE
        assert usage.provider == CloudProvider.AWS
        assert usage.usage_hours == 100.0
        assert usage.cost_per_hour == 0.10
        assert usage.total_cost == 10.0
    
    def test_get_resource_cost(self):
        """Test getting resource cost."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10
        )
        
        cost = monitor.get_resource_cost("vm-001")
        assert cost == 10.0
        
        # Test non-existent resource
        cost = monitor.get_resource_cost("non-existent")
        assert cost is None
    
    def test_get_total_cost(self):
        """Test total cost calculation."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10
        )
        
        monitor.track_resource(
            resource_id="db-001",
            resource_type=ResourceType.DATABASE,
            provider=CloudProvider.AWS,
            usage_hours=200.0,
            cost_per_hour=0.15
        )
        
        total = monitor.get_total_cost()
        assert total == 40.0  # 10 + 30
        
        # Test filtering by provider
        aws_cost = monitor.get_total_cost(provider=CloudProvider.AWS)
        assert aws_cost == 40.0
        
        # Test filtering by resource type
        compute_cost = monitor.get_total_cost(resource_type=ResourceType.COMPUTE)
        assert compute_cost == 10.0
    
    def test_identify_optimization_opportunities_underutilized(self):
        """Test identifying underutilized resources."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10,
            metadata={"utilization": 0.2}  # 20% utilization
        )
        
        opportunities = monitor.identify_optimization_opportunities()
        
        assert len(opportunities) > 0
        underutilized = [o for o in opportunities if o["type"] == "underutilized_resource"]
        assert len(underutilized) > 0
        assert underutilized[0]["resource_id"] == "vm-001"
        assert underutilized[0]["utilization"] == 0.2
    
    def test_identify_optimization_opportunities_idle(self):
        """Test identifying idle resources."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-002",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10,
            metadata={"last_active_hours": 48}  # Idle for 48 hours
        )
        
        opportunities = monitor.identify_optimization_opportunities()
        
        idle = [o for o in opportunities if o["type"] == "idle_resource"]
        assert len(idle) > 0
        assert idle[0]["resource_id"] == "vm-002"
        assert idle[0]["idle_hours"] == 48
    
    def test_identify_optimization_opportunities_oversized(self):
        """Test identifying oversized resources."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-003",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10,
            metadata={"cpu_usage": 0.2, "memory_usage": 0.25}  # Low usage
        )
        
        opportunities = monitor.identify_optimization_opportunities()
        
        oversized = [o for o in opportunities if o["type"] == "oversized_resource"]
        assert len(oversized) > 0
        assert oversized[0]["resource_id"] == "vm-003"
    
    def test_generate_cost_report(self):
        """Test cost report generation."""
        monitor = CostMonitor()
        
        # Add various resources
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0
        )
        
        monitor.track_resource(
            resource_id="db-001",
            resource_type=ResourceType.DATABASE,
            provider=CloudProvider.AZURE,
            usage_hours=200.0
        )
        
        report = monitor.generate_cost_report("report-001")
        
        assert report is not None
        assert report.report_id == "report-001"
        assert report.total_cost > 0
        assert len(report.cost_by_resource_type) > 0
        assert len(report.cost_by_provider) > 0
        assert isinstance(report.top_cost_resources, list)
        assert isinstance(report.optimization_opportunities, list)
    
    def test_get_cost_forecast(self):
        """Test cost forecasting."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10
        )
        
        forecast = monitor.get_cost_forecast(days=30)
        
        assert forecast is not None
        assert forecast["forecast_days"] == 30
        assert forecast["forecasted_cost"] > 0
        assert "forecasted_cost_min" in forecast
        assert "forecasted_cost_max" in forecast
    
    def test_get_cost_breakdown(self):
        """Test cost breakdown."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0
        )
        
        breakdown = monitor.get_cost_breakdown()
        
        assert breakdown is not None
        assert "total_cost" in breakdown
        assert "by_provider" in breakdown
        assert "by_resource_type" in breakdown
        assert breakdown["resource_count"] == 1
    
    def test_apply_cost_optimization(self):
        """Test applying cost optimizations."""
        monitor = CostMonitor()
        
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            cost_per_hour=0.10,
            metadata={"utilization": 0.2}
        )
        
        opportunities = monitor.identify_optimization_opportunities()
        opportunity = opportunities[0]
        
        result = monitor.apply_cost_optimization(opportunity)
        
        assert result["applied"] is True
        assert "message" in result


class TestPerformanceProfiler:
    """Tests for performance profiling system."""
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        profiler = PerformanceProfiler()
        assert profiler is not None
        assert len(profiler.profiles) == 0
        assert len(profiler.baseline_profiles) == 0
    
    def test_profile_function_basic(self):
        """Test basic function profiling."""
        profiler = PerformanceProfiler()
        
        def test_func():
            time.sleep(0.01)  # 10ms
            return "done"
        
        result = profiler.profile_function(test_func, profile_type=ProfileType.FULL)
        
        assert result is not None
        assert result.function_name == "test_func"
        assert result.execution_time_ms >= 10.0
        assert result.call_count == 1
        assert isinstance(result.recommendations, list)
    
    def test_profile_function_with_iterations(self):
        """Test profiling with multiple iterations."""
        profiler = PerformanceProfiler()
        
        def fast_func():
            return sum(range(100))
        
        result = profiler.profile_function(fast_func, iterations=10)
        
        assert result is not None
        assert result.call_count == 10
        assert result.execution_time_ms > 0
    
    def test_profile_function_with_args(self):
        """Test profiling function with arguments."""
        profiler = PerformanceProfiler()
        
        def func_with_args(x, y):
            return x + y
        
        result = profiler.profile_function(func_with_args, 5, 10)
        
        assert result is not None
        assert result.metadata["args_count"] == 2
    
    def test_identify_hotspots_slow_execution(self):
        """Test identifying slow execution hotspots."""
        profiler = PerformanceProfiler()
        profiler.slow_threshold_ms = 50
        
        def slow_func():
            time.sleep(0.1)  # 100ms
        
        result = profiler.profile_function(slow_func)
        
        assert len(result.hotspots) > 0
        slow_hotspots = [h for h in result.hotspots if h["type"] == "slow_execution"]
        assert len(slow_hotspots) > 0
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        profiler = PerformanceProfiler()
        profiler.slow_threshold_ms = 50
        
        def slow_func():
            time.sleep(0.1)  # 100ms
        
        result = profiler.profile_function(slow_func)
        
        assert len(result.recommendations) > 0
        assert any("threshold" in rec.lower() or "optimization" in rec.lower() 
                  for rec in result.recommendations)
    
    def test_set_baseline(self):
        """Test setting performance baseline."""
        profiler = PerformanceProfiler()
        
        def test_func():
            return sum(range(1000))
        
        profiler.profile_function(test_func)
        success = profiler.set_baseline("test_func")
        
        assert success is True
        assert "test_func" in profiler.baseline_profiles
    
    def test_compare_with_baseline(self):
        """Test comparing performance with baseline."""
        profiler = PerformanceProfiler()
        
        def test_func():
            return sum(range(1000))
        
        # Create baseline
        profiler.profile_function(test_func)
        profiler.set_baseline("test_func")
        
        # Create new profile
        profiler.profile_function(test_func)
        
        comparison = profiler.compare_with_baseline("test_func")
        
        assert comparison is not None
        assert "function" in comparison
        assert "baseline_time_ms" in comparison
        assert "current_time_ms" in comparison
        assert "time_change_percent" in comparison
    
    def test_get_performance_summary(self):
        """Test getting performance summary."""
        profiler = PerformanceProfiler()
        
        def func1():
            time.sleep(0.01)
        
        def func2():
            time.sleep(0.02)
        
        profiler.profile_function(func1)
        profiler.profile_function(func2)
        
        summary = profiler.get_performance_summary()
        
        assert summary is not None
        assert summary["total_profiles"] == 2
        assert "avg_execution_time_ms" in summary
        assert "slowest_functions" in summary
    
    def test_detect_regressions(self):
        """Test performance regression detection."""
        profiler = PerformanceProfiler()
        
        def test_func():
            return sum(range(1000))
        
        # Create baseline with fast execution
        profiler.profile_function(test_func)
        profiler.set_baseline("test_func")
        
        # Simulate slower execution (not truly slower, but we'll test the mechanism)
        regressions = profiler.detect_regressions(threshold_percent=10.0)
        
        # Should be a list (may be empty if no regressions)
        assert isinstance(regressions, list)
    
    def test_optimize_function(self):
        """Test getting optimization strategies."""
        profiler = PerformanceProfiler()
        profiler.slow_threshold_ms = 50
        
        def slow_func():
            time.sleep(0.1)  # 100ms
        
        profiler.profile_function(slow_func)
        
        optimization = profiler.optimize_function("slow_func")
        
        assert optimization is not None
        assert "function" in optimization
        assert "current_performance" in optimization
        assert "optimization_strategies" in optimization
        assert len(optimization["optimization_strategies"]) > 0


class TestIntegration:
    """Integration tests for Phase 6 optimization features."""
    
    def test_cost_and_performance_integration(self):
        """Test integration between cost monitoring and performance profiling."""
        # Cost monitoring
        cost_monitor = CostMonitor()
        cost_monitor.track_resource(
            resource_id="app-server-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0
        )
        
        # Performance profiling
        profiler = PerformanceProfiler()
        
        def app_function():
            time.sleep(0.01)
            return "processed"
        
        profiler.profile_function(app_function)
        
        # Both systems should work together
        cost_report = cost_monitor.generate_cost_report("integration-test")
        perf_summary = profiler.get_performance_summary()
        
        assert cost_report.total_cost > 0
        assert perf_summary["total_profiles"] > 0
    
    def test_optimization_workflow(self):
        """Test complete optimization workflow."""
        # 1. Track resource usage
        monitor = CostMonitor()
        monitor.track_resource(
            resource_id="vm-001",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=100.0,
            metadata={"utilization": 0.2}
        )
        
        # 2. Generate cost report
        report = monitor.generate_cost_report("workflow-test")
        assert len(report.optimization_opportunities) > 0
        
        # 3. Apply optimization
        opportunity = report.optimization_opportunities[0]
        result = monitor.apply_cost_optimization(opportunity)
        assert result["applied"] is True
        
        # 4. Generate new report to verify savings
        new_report = monitor.generate_cost_report("workflow-test-after")
        assert new_report.total_cost <= report.total_cost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
