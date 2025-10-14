"""
Phase 3 Advanced Features Demo
Demonstrates AI enhancement, enterprise features, and enhanced CLI.
"""

from accelerapp.ai import (
    AIModelVersionManager,
    ABTestingFramework,
    AdvancedPromptEngine,
    ModelPerformanceAnalyzer,
    AgentSwarmOrchestrator,
)
from accelerapp.ai.swarm_orchestrator import AgentRole
from accelerapp.enterprise import (
    SSOManager,
    RBACManager,
    TenantManager,
    EnterpriseAuditLogger,
    DataGovernor,
    BIDashboard,
)
from accelerapp.enterprise.governance.data_governor import DataClassification
from accelerapp.developer import EnhancedCLI


def demo_ai_enhancement():
    """Demonstrate AI enhancement features."""
    print("\n" + "=" * 80)
    print("AI ENHANCEMENT DEMO")
    print("=" * 80)
    
    # 1. Model Version Management
    print("\n1. Model Version Management")
    print("-" * 40)
    
    manager = AIModelVersionManager()
    
    # Register versions
    v1 = manager.register_version(
        "code_gen_model",
        "1.0.0",
        {"accuracy": 0.85, "latency": 0.8},
        {"framework": "transformers"}
    )
    print(f"✓ Registered {v1.name} v{v1.version}")
    
    v2 = manager.register_version(
        "code_gen_model",
        "2.0.0",
        {"accuracy": 0.92, "latency": 0.5},
        {"framework": "transformers", "optimized": True}
    )
    print(f"✓ Registered {v2.name} v{v2.version}")
    
    # Set active and rollback
    manager.set_active_version("code_gen_model", "2.0.0")
    active = manager.get_active_version("code_gen_model")
    print(f"✓ Active version: {active.version}")
    
    stats = manager.get_version_stats()
    print(f"✓ Managing {stats['total_models']} models, {stats['total_versions']} versions")
    
    # 2. A/B Testing
    print("\n2. A/B Testing Framework")
    print("-" * 40)
    
    framework = ABTestingFramework()
    
    test = framework.create_test(
        "prompt_test",
        "Prompt Template Test",
        "Testing different prompt styles",
        [
            {"name": "concise", "config": {"style": "concise"}},
            {"name": "detailed", "config": {"style": "detailed"}}
        ]
    )
    print(f"✓ Created test: {test.name}")
    
    # Simulate metrics
    for i in range(10):
        framework.record_metric("prompt_test", "concise", "accuracy", 0.88 + i * 0.01)
        framework.record_metric("prompt_test", "detailed", "accuracy", 0.85 + i * 0.008)
    
    results = framework.get_results("prompt_test")
    print(f"✓ Collected {results['total_samples']} samples")
    
    significance = framework.calculate_statistical_significance("prompt_test", "accuracy")
    if significance and significance.get("significant"):
        print(f"✓ Winner: {significance['winner']} (+{significance['improvement_percentage']:.1f}%)")
    
    # 3. Advanced Prompt Engine
    print("\n3. Advanced Prompt Engineering")
    print("-" * 40)
    
    engine = AdvancedPromptEngine()
    
    prompt = engine.render_prompt(
        "code_generation",
        {
            "language": "C++",
            "purpose": "IoT sensor management",
            "requirements": "Real-time data processing",
            "platform": "ESP32",
            "constraints": "4MB Flash, 512KB RAM"
        }
    )
    
    if prompt:
        print(f"✓ Generated prompt ({len(prompt)} chars)")
        print(f"  Preview: {prompt[:100]}...")
    
    templates = engine.list_templates()
    print(f"✓ Available templates: {len(templates)}")
    
    # 4. Performance Analytics
    print("\n4. Model Performance Analytics")
    print("-" * 40)
    
    analyzer = ModelPerformanceAnalyzer()
    
    # Record performance
    for i in range(5):
        analyzer.record_performance(
            "code_agent",
            "generation",
            {
                "latency": 0.4 + i * 0.1,
                "accuracy": 0.90 + i * 0.01,
                "tokens_per_sec": 95 + i * 2
            }
        )
    
    stats = analyzer.get_agent_performance("code_agent")
    print(f"✓ Recorded {stats['total_measurements']} measurements")
    print(f"  Avg latency: {stats['metrics']['latency']['mean']:.2f}s")
    print(f"  Avg accuracy: {stats['metrics']['accuracy']['mean']:.2%}")
    
    trend = analyzer.get_trend("code_agent", "accuracy")
    print(f"✓ Performance trend: {trend['trend']}")
    
    # 5. Agent Swarm Orchestration
    print("\n5. Agent Swarm Orchestration")
    print("-" * 40)
    
    orchestrator = AgentSwarmOrchestrator()
    
    # Register agents
    def worker_callback(task):
        print(f"    Processing task: {task.task_id}")
    
    orchestrator.register_agent(
        "worker1",
        AgentRole.WORKER,
        ["code_generation", "optimization"],
        worker_callback,
        priority=2
    )
    
    orchestrator.register_agent(
        "worker2",
        AgentRole.WORKER,
        ["testing", "documentation"],
        worker_callback,
        priority=1
    )
    
    # Submit tasks
    task1 = orchestrator.submit_task(
        "task001",
        "code_generation",
        {"platform": "esp32"},
        ["code_generation"]
    )
    
    task2 = orchestrator.submit_task(
        "task002",
        "testing",
        {"test_type": "unit"},
        ["testing"]
    )
    
    swarm_status = orchestrator.get_swarm_status()
    print(f"✓ Swarm: {swarm_status['total_agents']} agents, {swarm_status['total_tasks']} tasks")
    print(f"  In progress: {swarm_status['in_progress']}")


def demo_enterprise_features():
    """Demonstrate enterprise features."""
    print("\n" + "=" * 80)
    print("ENTERPRISE FEATURES DEMO")
    print("=" * 80)
    
    # 1. Multi-tenancy
    print("\n1. Multi-Tenancy Support")
    print("-" * 40)
    
    tm = TenantManager()
    
    tenant = tm.create_tenant(
        "Acme Corporation",
        config={"region": "us-east-1"},
        resource_limits={"max_devices": 500}
    )
    print(f"✓ Created tenant: {tenant.name}")
    
    # Create resources
    for i in range(3):
        tm.create_resource(tenant.tenant_id, "device", {"name": f"Device-{i+1}"})
    
    usage = tm.get_tenant_usage(tenant.tenant_id)
    print(f"✓ Tenant resources: {usage['total_resources']}")
    print(f"  Limits: {usage['limits']['max_devices']} max devices")
    
    # 2. SSO Authentication
    print("\n2. SSO Authentication")
    print("-" * 40)
    
    sso = SSOManager()
    
    provider = sso.register_provider(
        "corporate_saml",
        "saml",
        "Corporate SAML SSO",
        {"idp_url": "https://idp.acme.com"}
    )
    print(f"✓ Registered SSO provider: {provider.name}")
    
    session = sso.authenticate_saml("corporate_saml", "mock_saml_response")
    if session:
        print(f"✓ Authenticated user: {session.user_id[:16]}...")
        print(f"  Session expires: {session.expires_at}")
    
    providers = sso.list_providers()
    print(f"✓ Total SSO providers: {len(providers)}")
    
    # 3. RBAC
    print("\n3. Role-Based Access Control")
    print("-" * 40)
    
    rbac = RBACManager()
    
    # Assign roles
    rbac.assign_role("user001", "developer")
    rbac.assign_role("user002", "viewer")
    
    print("✓ Assigned roles to users")
    
    # Check permissions
    if rbac.check_permission("user001", "write_devices"):
        print("✓ user001 can write devices")
    
    if not rbac.check_permission("user002", "write_devices"):
        print("✓ user002 cannot write devices (viewer role)")
    
    roles = rbac.list_roles()
    print(f"✓ Available roles: {len(roles)}")
    
    # 4. Audit Logging
    print("\n4. Enterprise Audit Logging")
    print("-" * 40)
    
    logger = EnterpriseAuditLogger()
    
    # Log events
    logger.log_event(
        tenant.tenant_id,
        "user001",
        "create_device",
        "device",
        "dev001",
        "success",
        {"device_name": "Temperature Sensor"}
    )
    
    logger.log_event(
        tenant.tenant_id,
        "user001",
        "update_device",
        "device",
        "dev001",
        "success",
        {"field": "location"}
    )
    
    events = logger.query_events(tenant_id=tenant.tenant_id)
    print(f"✓ Logged {len(events)} audit events")
    
    activity = logger.get_user_activity("user001")
    print(f"✓ User activity: {len(activity)} actions")
    
    # 5. Data Governance
    print("\n5. Data Governance")
    print("-" * 40)
    
    governor = DataGovernor()
    
    classification = governor.classify_data(
        "user_credentials",
        contains_pii=True
    )
    print(f"✓ Data classified as: {classification.value}")
    
    compliance = governor.check_compliance(
        DataClassification.RESTRICTED,
        encryption_enabled=True,
        anonymization_enabled=True
    )
    
    if compliance["compliant"]:
        print("✓ Data handling is compliant")
    else:
        print(f"✗ Compliance issues: {compliance['issues']}")
    
    policies = governor.list_policies()
    print(f"✓ Governance policies: {len(policies)}")
    
    # 6. Business Intelligence
    print("\n6. Business Intelligence Dashboard")
    print("-" * 40)
    
    dashboard = BIDashboard()
    
    # Record metrics
    for i in range(10):
        dashboard.record_metric("api_calls", 100 + i * 10)
        dashboard.record_metric("active_devices", 50 + i * 2)
    
    overview = dashboard.get_dashboard_overview()
    print(f"✓ Tracking {overview['total_metrics']} metrics")
    
    api_summary = dashboard.get_metric_summary("api_calls")
    print(f"  API calls: {api_summary['summary']['total']:.0f} total")
    print(f"  Average: {api_summary['summary']['mean']:.0f} per measurement")


def demo_enhanced_cli():
    """Demonstrate enhanced CLI features."""
    print("\n" + "=" * 80)
    print("ENHANCED CLI DEMO")
    print("=" * 80)
    
    cli = EnhancedCLI()
    
    # Banner
    print("\n1. Application Banner")
    print("-" * 40)
    cli.show_banner()
    
    # Tables
    print("\n2. Formatted Tables")
    print("-" * 40)
    cli.show_table(
        "Device Status",
        ["Device ID", "Platform", "Status", "Uptime"],
        [
            ["ESP32-001", "ESP32", "Active", "24h"],
            ["ARD-002", "Arduino", "Idle", "1h"],
            ["STM-003", "STM32", "Active", "72h"]
        ]
    )
    
    # Panels
    print("\n3. Information Panels")
    print("-" * 40)
    cli.show_panel(
        "Phase 3 features include:\n"
        "• AI Enhancement\n"
        "• Enterprise Features\n"
        "• Enhanced CLI\n"
        "• Cloud-Native Deployment",
        "Features",
        "cyan"
    )
    
    # Tree structure
    print("\n4. Hierarchical Trees")
    print("-" * 40)
    cli.show_tree(
        "Project Structure",
        {
            "firmware": ["main.cpp", "config.h", "sensors.cpp"],
            "sdk": {
                "python": ["device.py", "utils.py"],
                "javascript": ["device.js", "api.js"]
            },
            "tests": ["test_device.py", "test_api.py"]
        }
    )
    
    # Status messages
    print("\n5. Status Messages")
    print("-" * 40)
    cli.show_success("Code generation completed successfully!")
    cli.show_info("Using cached model data")
    cli.show_warning("Device temperature approaching limit")
    cli.show_error("Failed to connect to device")
    
    # Generation results
    print("\n6. Generation Results Display")
    print("-" * 40)
    cli.display_generation_results({
        "firmware_files": 12,
        "sdk_files": 8,
        "ui_files": 15,
        "test_files": 6,
        "output_dir": "./generated_output",
        "file_tree": {
            "firmware": ["main.cpp", "config.h"],
            "sdk": ["python", "javascript"],
            "ui": ["components", "pages"]
        }
    })


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("ACCELERAPP PHASE 3: ADVANCED FEATURES DEMO")
    print("=" * 80)
    print("\nThis demo showcases:")
    print("• AI Enhancement (Model Management, A/B Testing, Prompts, Analytics, Swarm)")
    print("• Enterprise Features (Multi-tenancy, SSO, RBAC, Audit, Governance, BI)")
    print("• Enhanced CLI (Rich UI, Progress, Tables, Trees)")
    
    try:
        # Run demos
        demo_ai_enhancement()
        demo_enterprise_features()
        demo_enhanced_cli()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nFor more information:")
        print("• Documentation: docs/PHASE3_FEATURES.md")
        print("• API Reference: See module docstrings")
        print("• Tests: tests/test_ai_module.py, tests/test_enterprise.py")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
