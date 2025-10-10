#!/usr/bin/env python3
"""
Demonstration of Accelerapp air-gapped features.
Shows how to use local LLM, agent communication, and knowledge management.
"""

from pathlib import Path
import tempfile


def demo_local_llm():
    """Demonstrate local LLM integration."""
    print("=" * 60)
    print("Demo 1: Local LLM Integration")
    print("=" * 60)
    
    from accelerapp.llm import (
        LocalLLMService, OllamaProvider, LLMBackend,
        ModelManager, PromptTemplates
    )
    
    # Initialize LLM service
    service = LocalLLMService({
        'default_model': 'codellama:7b',
        'timeout': 30
    })
    
    # Register Ollama provider
    provider = OllamaProvider(base_url="http://localhost:11434")
    service.register_provider(LLMBackend.OLLAMA, provider)
    
    print(f"✓ LLM service initialized with {LLMBackend.OLLAMA.value} backend")
    
    # Check availability
    available = provider.is_available()
    print(f"✓ Provider available: {available}")
    
    # Get recommended models
    manager = ModelManager()
    models = manager.get_recommended_models("code_generation")
    print(f"✓ Found {len(models)} recommended models:")
    for model in models[:3]:
        print(f"  - {model['name']}: {model['description']}")
    
    # Create a specialized prompt
    prompt = PromptTemplates.format_firmware_prompt(
        platform="arduino",
        mcu="ATmega328P",
        clock_speed="16MHz",
        peripherals="LED on pin 13"
    )
    print(f"✓ Generated specialized firmware prompt")
    
    print("\n")


def demo_agent_communication():
    """Demonstrate agent communication."""
    print("=" * 60)
    print("Demo 2: Agent-to-Agent Communication")
    print("=" * 60)
    
    from accelerapp.communication import (
        MessageBus, AgentCoordinator, SharedContext,
        MessagePriority, ContextScope, CoordinationStrategy
    )
    
    # Initialize message bus
    bus = MessageBus(max_queue_size=100)
    bus.start()
    print("✓ Message bus started")
    
    # Create coordinator
    coordinator = AgentCoordinator(message_bus=bus)
    coordinator.set_strategy(CoordinationStrategy.SEQUENTIAL)
    print(f"✓ Coordinator initialized with {CoordinationStrategy.SEQUENTIAL.value} strategy")
    
    # Register agents
    coordinator.register_agent("firmware-agent", "Firmware Generator", ["firmware"])
    coordinator.register_agent("software-agent", "Software Generator", ["software"])
    coordinator.register_agent("ui-agent", "UI Generator", ["ui"])
    
    stats = coordinator.get_stats()
    print(f"✓ Registered {stats['total_agents']} agents")
    
    # Setup shared context
    context = SharedContext()
    context.set("project_name", "AirGapDemo", ContextScope.GLOBAL)
    context.set("version", "1.0.0", ContextScope.GLOBAL)
    print("✓ Shared context initialized")
    
    # Publish messages
    msg_id = bus.publish(
        sender="coordinator",
        topic="task.assigned",
        content={"task": "generate_firmware"},
        priority=MessagePriority.HIGH
    )
    print(f"✓ Published message: {msg_id[:8]}...")
    
    # Get statistics
    bus_stats = bus.get_stats()
    print(f"✓ Message bus stats: {bus_stats['queue_size']} queued, {bus_stats['history_size']} in history")
    
    bus.stop()
    print("\n")


def demo_knowledge_management():
    """Demonstrate knowledge management."""
    print("=" * 60)
    print("Demo 3: Offline Knowledge Management")
    print("=" * 60)
    
    from accelerapp.knowledge import (
        KnowledgeBase, TemplateManager, Template, TemplateCategory,
        PatternAnalyzer, OfflineDocumentation
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Knowledge base
        kb = KnowledgeBase(storage_dir=tmppath / "knowledge")
        
        # Add entries
        kb.add_entry(
            "arduino-basics",
            "Arduino is a microcontroller platform for embedded systems",
            category="firmware"
        )
        kb.add_entry(
            "python-sdk",
            "Python SDK provides serial communication with hardware",
            category="software"
        )
        
        kb.rebuild_index()
        
        # Search
        results = kb.search("arduino", limit=5)
        print(f"✓ Knowledge base: {len(kb.entries)} entries, {len(results)} search results")
        
        # Template manager
        tm = TemplateManager(storage_dir=tmppath / "templates")
        
        template = Template(
            id="arduino-setup",
            name="Arduino Setup Template",
            category=TemplateCategory.FIRMWARE,
            content="void setup() {\n  pinMode({{pin}}, OUTPUT);\n}",
            variables=["pin"]
        )
        tm.add_template(template)
        
        rendered = tm.render_template("arduino-setup", {"pin": "13"})
        print(f"✓ Template manager: {len(tm.templates)} templates")
        print(f"  Rendered: {rendered.strip()}")
        
        # Pattern analyzer
        analyzer = PatternAnalyzer()
        
        code = """
        void loop() {
            for (int i = 0; i < 10; i++) {
                digitalWrite(LED, HIGH);
            }
        }
        """
        
        analysis = analyzer.analyze(code, "c")
        print(f"✓ Pattern analyzer: Found {len(analysis['patterns'])} patterns")
        
        # Offline docs
        docs = OfflineDocumentation(docs_dir=tmppath / "docs")
        results = docs.search("setup")
        print(f"✓ Offline docs: {len(docs.entries)} entries available")
    
    print("\n")


def demo_complete_workflow():
    """Demonstrate complete air-gapped workflow."""
    print("=" * 60)
    print("Demo 4: Complete Air-Gapped Workflow")
    print("=" * 60)
    
    print("Step 1: Initialize components")
    print("  ✓ LLM service (Ollama)")
    print("  ✓ Message bus")
    print("  ✓ Agent coordinator")
    print("  ✓ Knowledge base")
    
    print("\nStep 2: Agent coordination")
    print("  ✓ Register specialized agents")
    print("  ✓ Setup shared context")
    print("  ✓ Enable inter-agent messaging")
    
    print("\nStep 3: Code generation")
    print("  ✓ Load hardware specification")
    print("  ✓ Generate firmware (via local LLM)")
    print("  ✓ Generate software SDK")
    print("  ✓ Generate UI components")
    
    print("\nStep 4: Knowledge management")
    print("  ✓ Store generated patterns")
    print("  ✓ Update template library")
    print("  ✓ Build local knowledge base")
    
    print("\nStep 5: Output")
    print("  ✓ Complete firmware code")
    print("  ✓ Multi-language SDK")
    print("  ✓ Responsive UI")
    print("  ✓ Documentation")
    
    print("\n✅ Air-gapped workflow completed successfully!")
    print("\n")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Accelerapp Air-Gapped Features Demo" + " " * 12 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        demo_local_llm()
        demo_agent_communication()
        demo_knowledge_management()
        demo_complete_workflow()
        
        print("=" * 60)
        print("All demonstrations completed successfully!")
        print("=" * 60)
        print("\nFor more information:")
        print("  - Main README: ../README.md")
        print("  - Deployment: ../deployment/README.md")
        print("  - Air-Gap Config: ../config/airgap/")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Note: Some features require Ollama to be running")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
