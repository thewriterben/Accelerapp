#!/usr/bin/env python3
"""
Integration example showing Phase 2 architecture with existing Accelerapp features.
Demonstrates how the new service layer, monitoring, and caching improve the code generation process.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accelerapp.core import ServiceContainer, ConfigurationManager
from accelerapp.services import HardwareService, AIService, MonitoringService
from accelerapp.agents import AIAgent, FirmwareAgent
from accelerapp.agents.optimization_agents import PerformanceOptimizationAgent
from accelerapp.utils import CacheManager, PerformanceProfiler, cache_result
from accelerapp.monitoring import setup_logging, get_logger, get_metrics


# Cached code generation with Phase 2 caching
@cache_result(ttl=300)
def generate_platform_code(platform: str, spec: dict) -> dict:
    """Generate code with caching to avoid regenerating identical specs."""
    print(f"    Generating code for {platform} (cache miss)")
    # Simulate code generation
    return {
        "platform": platform,
        "code": f"// Generated for {platform}\nvoid setup() {{\n  // Init code\n}}\n",
        "size": 1024,
    }


async def demo_integrated_generation():
    """Demonstrate integrated code generation with Phase 2 features."""
    print("\n" + "=" * 70)
    print("INTEGRATION DEMO: Phase 2 with Existing Features")
    print("=" * 70)

    # Setup Phase 2 infrastructure
    setup_logging(level="INFO", structured=False)
    logger = get_logger(__name__, correlation_id="gen-001")
    metrics = get_metrics()
    profiler = PerformanceProfiler()

    logger.info("Starting integrated code generation demo")

    # Initialize services
    container = ServiceContainer()
    
    hw_service = HardwareService()
    ai_service = AIService()
    monitoring_service = MonitoringService()

    await hw_service.initialize()
    await ai_service.initialize()
    await monitoring_service.initialize()

    print("✓ Services initialized")

    # Register existing agents with the new AI service
    ai_agent = AIAgent()
    firmware_agent = FirmwareAgent()
    perf_agent = PerformanceOptimizationAgent()

    ai_service.register_agent("ai_agent", ai_agent)
    ai_service.register_agent("firmware_agent", firmware_agent)
    ai_service.register_agent("perf_agent", perf_agent)

    print(f"✓ Registered {len(ai_service.list_agents())} agents")

    # Register hardware devices
    hw_service.register_device(
        "arduino_uno",
        {
            "platform": "arduino",
            "mcu": "ATmega328P",
            "memory": {"flash": 32768, "ram": 2048},
        },
    )
    hw_service.register_device(
        "esp32_dev",
        {
            "platform": "esp32",
            "mcu": "ESP32",
            "memory": {"flash": 4194304, "ram": 520192},
        },
    )

    print(f"✓ Registered {len(hw_service.list_devices())} devices")

    # Generate code with monitoring and caching
    print("\n  Code Generation with Phase 2 Features:")

    spec = {
        "device_name": "LED Controller",
        "platform": "arduino",
        "peripherals": [{"type": "led", "pin": 13}],
    }

    # First generation (cache miss)
    with profiler.measure("code_generation"):
        metrics.counter("code_generation_requests").inc()
        
        result1 = generate_platform_code(spec["platform"], spec)
        print(f"    ✓ Generated code: {len(result1['code'])} bytes")
        
        metrics.histogram("code_size_bytes").observe(result1["size"])

    # Second generation (cache hit)
    with profiler.measure("code_generation"):
        metrics.counter("code_generation_requests").inc()
        
        result2 = generate_platform_code(spec["platform"], spec)
        print(f"    ✓ Retrieved from cache: {len(result2['code'])} bytes")

    # Use optimization agent through AI service
    print("\n  Performance Optimization:")
    
    with profiler.measure("optimization_analysis"):
        opt_result = ai_service.generate(
            "perf_agent",
            {
                "code": result1["code"],
                "language": "cpp",
                "platform": "arduino",
            },
        )
        
        if opt_result["status"] == "success":
            analysis = opt_result["analysis"]
            print(f"    ✓ Found {analysis['issues_found']} optimization opportunities")
            if analysis["suggestions"]:
                print(f"    ✓ Top suggestion: {analysis['suggestions'][0]['title']}")

    # Check service health
    print("\n  System Health:")
    
    health = monitoring_service.get_health_status()
    print(f"    Overall status: {health['status']}")
    print(f"    Total checks: {health['total_checks']}")
    print(f"    Failed checks: {health['failed_checks']}")

    # Show performance metrics
    print("\n  Performance Metrics:")
    
    gen_metrics = profiler.get_metrics("code_generation")
    print(f"    Code generation calls: {gen_metrics['count']}")
    print(f"    Average time: {gen_metrics['avg_time']:.3f}s")
    print(f"    Min time: {gen_metrics['min_time']:.3f}s")
    print(f"    Max time: {gen_metrics['max_time']:.3f}s")

    opt_metrics = profiler.get_metrics("optimization_analysis")
    print(f"    Optimization calls: {opt_metrics['count']}")
    print(f"    Average time: {opt_metrics['avg_time']:.3f}s")

    # Show collected metrics
    all_metrics = monitoring_service.get_all_metrics()
    print(f"\n  Collected Metrics:")
    print(f"    Total requests: {all_metrics['counters'].get('code_generation_requests', 0)}")
    
    if "code_size_bytes" in all_metrics["histograms"]:
        code_size_stats = all_metrics["histograms"]["code_size_bytes"]
        print(f"    Code size - avg: {code_size_stats['avg']:.0f} bytes")

    # Cleanup
    await hw_service.shutdown()
    await ai_service.shutdown()
    await monitoring_service.shutdown()

    print("\n✓ Services shutdown gracefully")
    logger.info("Integrated demo completed successfully")


async def demo_workflow_with_agents():
    """Demonstrate workflow orchestration with existing agents."""
    print("\n" + "=" * 70)
    print("WORKFLOW DEMO: Multi-Agent Code Generation Pipeline")
    print("=" * 70)

    from accelerapp.services import WorkflowService
    from accelerapp.services.workflow_service import Workflow

    # Create workflow service
    workflow_service = WorkflowService()
    await workflow_service.initialize()

    # Create a code generation workflow
    workflow = Workflow(
        "code_generation_pipeline",
        "Complete code generation and optimization pipeline",
    )

    # Define workflow steps
    def analyze_spec(ctx):
        """Step 1: Analyze hardware specification."""
        print("    [Step 1] Analyzing hardware specification...")
        spec = ctx.get("spec", {})
        return {
            "analysis": {
                "platform": spec.get("platform"),
                "peripheral_count": len(spec.get("peripherals", [])),
                "complexity": "low",
            }
        }

    def generate_firmware(ctx):
        """Step 2: Generate firmware code."""
        print("    [Step 2] Generating firmware code...")
        analysis = ctx.get("analysis", {})
        return {
            "firmware": {
                "code": "void setup() { /* init */ }\nvoid loop() { /* main */ }",
                "size": 512,
            }
        }

    def optimize_code(ctx):
        """Step 3: Optimize generated code."""
        print("    [Step 3] Running optimization analysis...")
        firmware = ctx.get("firmware", {})
        return {
            "optimizations": [
                {"type": "memory", "impact": "medium"},
                {"type": "performance", "impact": "low"},
            ]
        }

    def validate_output(ctx):
        """Step 4: Validate generated code."""
        print("    [Step 4] Validating generated code...")
        firmware = ctx.get("firmware", {})
        optimizations = ctx.get("optimizations", [])
        return {
            "validation": {
                "passed": True,
                "issues": 0,
                "optimization_count": len(optimizations),
            }
        }

    # Add steps to workflow
    workflow.add_step("analyze", analyze_spec)
    workflow.add_step("generate", generate_firmware)
    workflow.add_step("optimize", optimize_code)
    workflow.add_step("validate", validate_output)

    # Register and execute workflow
    workflow_service.register_workflow(workflow)

    print("\n  Executing workflow pipeline:")
    
    result = workflow_service.execute_workflow(
        "code_generation_pipeline",
        context={
            "spec": {
                "platform": "arduino",
                "peripherals": [{"type": "led", "pin": 13}],
            }
        },
    )

    print(f"\n  Workflow Results:")
    print(f"    Status: Success")
    print(f"    Steps completed: {result['steps_completed']}/{result['total_steps']}")
    
    if result["results"]:
        last_result = result["results"][-1]["result"]
        validation = last_result.get("validation", {})
        print(f"    Validation passed: {validation.get('passed', False)}")
        print(f"    Issues found: {validation.get('issues', 0)}")
        print(f"    Optimizations applied: {validation.get('optimization_count', 0)}")

    await workflow_service.shutdown()
    print("\n✓ Workflow service shutdown")


async def main():
    """Run all integration demonstrations."""
    print("=" * 70)
    print("Accelerapp Phase 2 Integration Examples")
    print("=" * 70)
    print("\nDemonstrating:")
    print("  - Service layer with existing agents")
    print("  - Monitoring and metrics collection")
    print("  - Performance profiling")
    print("  - Caching for code generation")
    print("  - Workflow orchestration")
    print("  - Health checks and observability")

    try:
        await demo_integrated_generation()
        await demo_workflow_with_agents()

        print("\n" + "=" * 70)
        print("INTEGRATION DEMOS COMPLETED")
        print("=" * 70)
        print("\nPhase 2 features successfully integrated with existing Accelerapp!")
        print("\nKey Benefits Demonstrated:")
        print("  ✓ Service layer provides clean abstraction for agents")
        print("  ✓ Caching reduces repeated computation")
        print("  ✓ Performance profiling identifies bottlenecks")
        print("  ✓ Monitoring tracks system health and metrics")
        print("  ✓ Workflow engine orchestrates multi-step processes")
        print("  ✓ Structured logging provides observability")

    except Exception as e:
        print(f"\n❌ Error during integration demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
