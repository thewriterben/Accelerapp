#!/usr/bin/env python3
"""
Demonstration of Accelerapp Phase 2 features.
Shows architecture enhancements, performance optimizations, and monitoring capabilities.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accelerapp.core import ServiceContainer, ConfigurationManager
from accelerapp.services import HardwareService, AIService, WorkflowService, MonitoringService
from accelerapp.services.workflow_service import Workflow
from accelerapp.utils import CacheManager, PerformanceProfiler, profile
from accelerapp.monitoring import setup_logging, get_logger, HealthStatus
from accelerapp.plugins import BasePlugin, PluginMetadata, PluginRegistry


def demo_dependency_injection():
    """Demonstrate dependency injection container."""
    print("\n" + "=" * 70)
    print("DEMO 1: Dependency Injection Container")
    print("=" * 70)

    container = ServiceContainer()

    # Register services
    container.register(HardwareService)
    container.register(AIService)
    container.register(WorkflowService)

    print("✓ Registered services in container")

    # Resolve services
    hw_service = container.resolve(HardwareService)
    ai_service = container.resolve(AIService)

    print(f"✓ Resolved HardwareService: {hw_service.name}")
    print(f"✓ Resolved AIService: {ai_service.name}")

    # Show all registered services
    services = container.get_all_services()
    print(f"\n  Registered services: {len(services)}")
    for name, stype in services.items():
        print(f"    - {name}: {stype}")


def demo_configuration_management():
    """Demonstrate configuration management."""
    print("\n" + "=" * 70)
    print("DEMO 2: Configuration Management")
    print("=" * 70)

    config_mgr = ConfigurationManager()
    config = config_mgr.load()

    print("✓ Configuration loaded successfully")
    print(f"\n  Service Config:")
    print(f"    Enabled: {config.service.enabled}")
    print(f"    Timeout: {config.service.timeout}s")
    print(f"    Retry attempts: {config.service.retry_attempts}")

    print(f"\n  Performance Config:")
    print(f"    Caching enabled: {config.performance.enable_caching}")
    print(f"    Cache TTL: {config.performance.cache_ttl}s")
    print(f"    Max workers: {config.performance.max_workers}")

    print(f"\n  Monitoring Config:")
    print(f"    Metrics enabled: {config.monitoring.enable_metrics}")
    print(f"    Metrics port: {config.monitoring.metrics_port}")
    print(f"    Log level: {config.monitoring.log_level}")


def demo_caching():
    """Demonstrate caching utilities."""
    print("\n" + "=" * 70)
    print("DEMO 3: Caching Utilities")
    print("=" * 70)

    cache = CacheManager(default_ttl=60, max_size=100)

    # Set and get values
    cache.set("user:123", {"name": "John", "role": "admin"})
    cache.set("config:app", {"theme": "dark", "language": "en"})

    print("✓ Cached 2 items")

    user = cache.get("user:123")
    config = cache.get("config:app")

    print(f"  Retrieved user: {user}")
    print(f"  Retrieved config: {config}")

    # Show cache stats
    stats = cache.get_stats()
    print(f"\n  Cache statistics:")
    print(f"    Size: {stats['size']}/{stats['max_size']}")
    print(f"    Default TTL: {stats['default_ttl']}s")


def demo_performance_profiling():
    """Demonstrate performance profiling."""
    print("\n" + "=" * 70)
    print("DEMO 4: Performance Profiling")
    print("=" * 70)

    profiler = PerformanceProfiler()

    # Profile operations
    with profiler.measure("database_query"):
        time.sleep(0.1)  # Simulate query

    with profiler.measure("api_call"):
        time.sleep(0.05)  # Simulate API call

    with profiler.measure("database_query"):
        time.sleep(0.12)  # Another query

    print("✓ Profiled multiple operations")

    # Get metrics
    db_metrics = profiler.get_metrics("database_query")
    api_metrics = profiler.get_metrics("api_call")

    print(f"\n  Database Query Metrics:")
    print(f"    Count: {db_metrics['count']}")
    print(f"    Min time: {db_metrics['min_time']:.3f}s")
    print(f"    Max time: {db_metrics['max_time']:.3f}s")
    print(f"    Avg time: {db_metrics['avg_time']:.3f}s")

    print(f"\n  API Call Metrics:")
    print(f"    Count: {api_metrics['count']}")
    print(f"    Avg time: {api_metrics['avg_time']:.3f}s")


def demo_monitoring():
    """Demonstrate monitoring and metrics."""
    print("\n" + "=" * 70)
    print("DEMO 5: Monitoring & Metrics Collection")
    print("=" * 70)

    # Setup structured logging
    setup_logging(level="INFO", structured=False)
    logger = get_logger(__name__, correlation_id="demo-123")

    logger.info("Monitoring demo started")
    print("✓ Structured logging configured")

    # Create monitoring service
    monitoring = MonitoringService()

    # Record metrics
    monitoring.record_metric("counter", "requests_total", 1)
    monitoring.record_metric("gauge", "active_connections", 10)
    monitoring.record_metric("histogram", "request_duration", 0.245)

    print("✓ Recorded metrics")

    # Get all metrics
    metrics = monitoring.get_all_metrics()

    print(f"\n  Metrics Summary:")
    print(f"    Uptime: {metrics['uptime_seconds']:.2f}s")
    print(f"    Counters: {len(metrics['counters'])}")
    print(f"    Gauges: {len(metrics['gauges'])}")
    print(f"    Histograms: {len(metrics['histograms'])}")


async def demo_services():
    """Demonstrate service layer."""
    print("\n" + "=" * 70)
    print("DEMO 6: Service Layer")
    print("=" * 70)

    # Initialize services
    hw_service = HardwareService()
    ai_service = AIService()
    workflow_service = WorkflowService()

    await hw_service.initialize()
    await ai_service.initialize()
    await workflow_service.initialize()

    print("✓ Services initialized")

    # Hardware service demo
    hw_service.register_device("sensor1", {"type": "temperature", "model": "DHT22"})
    hw_service.register_device("actuator1", {"type": "relay", "pins": [13]})

    devices = hw_service.list_devices()
    print(f"\n  Hardware Service:")
    print(f"    Registered devices: {len(devices)}")
    for device_id in devices:
        device = hw_service.get_device(device_id)
        print(f"      - {device_id}: {device['type']}")

    # Workflow service demo
    workflow = Workflow("data_processing", "Process sensor data")
    workflow.add_step("read", lambda ctx: {"data": [1, 2, 3, 4, 5]})
    workflow.add_step("filter", lambda ctx: {"data": [x for x in ctx.get("data", []) if x > 2]})
    workflow.add_step("aggregate", lambda ctx: {"result": sum(ctx.get("data", []))})

    workflow_service.register_workflow(workflow)

    result = workflow_service.execute_workflow("data_processing")

    print(f"\n  Workflow Service:")
    print(f"    Workflow: {result['workflow']}")
    print(f"    Steps completed: {result['steps_completed']}/{result['total_steps']}")
    print(f"    Final result: {result['results'][-1]['result']['result']}")

    # Cleanup
    await hw_service.shutdown()
    await ai_service.shutdown()
    await workflow_service.shutdown()

    print("\n✓ Services shutdown gracefully")


def demo_health_checks():
    """Demonstrate health check system."""
    print("\n" + "=" * 70)
    print("DEMO 7: Health Check System")
    print("=" * 70)

    monitoring = MonitoringService()

    # Register custom health checks
    monitoring.register_health_check(
        "database_connection",
        lambda: True,  # Simulated check
        critical=True,
        description="Database connectivity",
    )

    monitoring.register_health_check(
        "external_api",
        lambda: True,  # Simulated check
        critical=False,
        description="External API availability",
    )

    print("✓ Registered health checks")

    # Get health status
    health = monitoring.get_health_status()

    print(f"\n  Health Status: {health['status']}")
    print(f"  Total checks: {health['total_checks']}")
    print(f"  Failed checks: {health['failed_checks']}")

    print("\n  Individual Checks:")
    for check in health["checks"]:
        status_icon = "✓" if check["status"] == "healthy" else "✗"
        critical = "(critical)" if check["critical"] else "(non-critical)"
        print(f"    {status_icon} {check['name']}: {check['status']} {critical}")


def demo_plugin_system():
    """Demonstrate plugin system."""
    print("\n" + "=" * 70)
    print("DEMO 8: Plugin System")
    print("=" * 70)

    # Create a sample plugin
    class SamplePlugin(BasePlugin):
        def __init__(self):
            metadata = PluginMetadata(
                name="SamplePlugin",
                version="1.0.0",
                author="Demo Author",
                description="Sample plugin for demonstration",
                capabilities=["analysis", "transformation"],
            )
            super().__init__(metadata)

        async def initialize(self):
            await super().initialize()

        async def shutdown(self):
            await super().shutdown()

    # Create registry and register plugin
    registry = PluginRegistry()
    plugin = SamplePlugin()
    registry.register(plugin)

    print("✓ Plugin registered")

    # Get plugin info
    info = registry.get_plugin_info("SamplePlugin")

    print(f"\n  Plugin Information:")
    print(f"    Name: {info['name']}")
    print(f"    Version: {info['version']}")
    print(f"    Author: {info['author']}")
    print(f"    Capabilities: {', '.join(info['capabilities'])}")

    # Find plugins by capability
    analysis_plugins = registry.find_plugins_by_capability("analysis")
    print(f"\n  Plugins with 'analysis' capability: {len(analysis_plugins)}")


def demo_error_handling():
    """Demonstrate custom exception hierarchy."""
    print("\n" + "=" * 70)
    print("DEMO 9: Error Handling")
    print("=" * 70)

    from accelerapp.core import (
        ConfigurationError,
        ServiceError,
        ValidationError,
    )

    try:
        # Simulate configuration error
        raise ConfigurationError("Invalid configuration file", {"file": "config.yaml"})
    except ConfigurationError as e:
        print(f"✓ Caught ConfigurationError: {e.message}")
        print(f"  Details: {e.details}")

    try:
        # Simulate service error
        raise ServiceError("Service unavailable")
    except ServiceError as e:
        print(f"✓ Caught ServiceError: {e.message}")

    print("\n  Exception hierarchy working correctly")


async def main():
    """Run all demonstrations."""
    print("=" * 70)
    print("Accelerapp Phase 2 Architecture Demo")
    print("=" * 70)
    print("\nDemonstrating new features:")
    print("  - Dependency Injection")
    print("  - Configuration Management")
    print("  - Caching Utilities")
    print("  - Performance Profiling")
    print("  - Monitoring & Metrics")
    print("  - Service Layer")
    print("  - Health Checks")
    print("  - Plugin System")
    print("  - Error Handling")

    try:
        demo_dependency_injection()
        demo_configuration_management()
        demo_caching()
        demo_performance_profiling()
        demo_monitoring()
        await demo_services()
        demo_health_checks()
        demo_plugin_system()
        demo_error_handling()

        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nAll Phase 2 features demonstrated successfully!")
        print("\nFor more information:")
        print("  - Architecture: See ARCHITECTURE.md")
        print("  - Configuration: See config/*.yaml")
        print("  - Tests: See tests/test_phase2_*.py")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
