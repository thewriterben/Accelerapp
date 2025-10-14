"""
Specialized prompts for different agent types in code generation.
Provides optimized prompts for firmware, software, UI, and other tasks.
"""

from typing import Dict, Any, Optional


class PromptTemplates:
    """
    Collection of specialized prompt templates for different code generation tasks.
    Each template is optimized for specific agent capabilities.
    """

    # Firmware generation prompts
    FIRMWARE_BASE = """You are an expert embedded systems programmer specializing in {platform} firmware development.

Task: Generate production-ready firmware code for the following specification:

Hardware Platform: {platform}
MCU: {mcu}
Clock Speed: {clock_speed}

Peripherals:
{peripherals}

Requirements:
- Write clean, efficient, production-ready code
- Include proper initialization and error handling
- Add appropriate comments for complex sections
- Follow {platform} best practices and coding standards
- Optimize for memory and performance
- Include proper header guards and includes

Generate the complete firmware implementation:
"""

    FIRMWARE_PERIPHERAL = """Generate a peripheral driver for {peripheral_type} on {platform}.

Peripheral Details:
{peripheral_config}

Requirements:
- Hardware abstraction layer
- Initialization function
- Read/write functions
- Error handling
- Interrupt support if applicable

Generate the driver code:
"""

    # Software SDK generation prompts
    SOFTWARE_SDK = """You are an expert software developer creating SDK libraries.

Task: Generate a {language} SDK for interfacing with a hardware device.

Device Specification:
{device_spec}

Communication Protocol: {protocol}

Requirements:
- Create a clean, well-documented API
- Include device initialization and cleanup
- Implement all peripheral interfaces
- Add error handling and validation
- Include usage examples
- Follow {language} best practices

Generate the complete SDK implementation:
"""

    SOFTWARE_DRIVER = """Generate a {language} driver library for the following device:

Device: {device_name}
Platform: {platform}
Communication: {communication}

Features to implement:
{features}

Requirements:
- Clean class/module structure
- Async support if applicable
- Type hints (Python) or strong typing
- Comprehensive error handling
- Thread-safe operations

Generate the driver code:
"""

    # UI generation prompts
    UI_FRAMEWORK = """You are an expert frontend developer specializing in {framework}.

Task: Generate a user interface for controlling a hardware device.

Device: {device_name}
Features:
{features}

UI Requirements:
- Responsive design
- Real-time updates
- Interactive controls
- Status indicators
- Error display
- Follow {framework} best practices

Generate the complete UI implementation:
"""

    UI_COMPONENT = """Generate a {framework} component for {component_type}.

Component Specification:
{component_spec}

Requirements:
- Reusable component design
- Props/event handling
- State management
- Responsive styling
- Accessibility support

Generate the component code:
"""

    # Agent collaboration prompts
    AGENT_COORDINATION = """You are coordinating code generation across multiple specialized agents.

Current Task: {task_description}

Context from other agents:
{agent_context}

Your role: {agent_role}

Generate code that integrates with the following components:
{integration_points}

Ensure consistency and compatibility with the overall system:
"""

    # Code review and optimization prompts
    CODE_REVIEW = """Review the following code for {code_type}:

Code:
{code}

Review for:
- Correctness and functionality
- Performance optimization opportunities
- Security vulnerabilities
- Code style and best practices
- Documentation completeness

Provide detailed review feedback:
"""

    CODE_OPTIMIZATION = """Optimize the following {language} code:

Current Implementation:
{code}

Optimization Goals:
- {optimization_goals}

Target Platform: {platform}

Provide optimized version with explanations:
"""

    @classmethod
    def format_firmware_prompt(
        cls, platform: str, mcu: str, clock_speed: str, peripherals: str, **kwargs
    ) -> str:
        """
        Format firmware generation prompt.

        Args:
            platform: Target platform (arduino, stm32, esp32, etc.)
            mcu: Microcontroller model
            clock_speed: Operating frequency
            peripherals: Peripheral configuration text
            **kwargs: Additional context

        Returns:
            Formatted prompt string
        """
        return cls.FIRMWARE_BASE.format(
            platform=platform, mcu=mcu, clock_speed=clock_speed, peripherals=peripherals
        )

    @classmethod
    def format_peripheral_prompt(
        cls, peripheral_type: str, platform: str, peripheral_config: str, **kwargs
    ) -> str:
        """
        Format peripheral driver prompt.

        Args:
            peripheral_type: Type of peripheral (LED, sensor, motor, etc.)
            platform: Target platform
            peripheral_config: Peripheral configuration details
            **kwargs: Additional context

        Returns:
            Formatted prompt string
        """
        return cls.FIRMWARE_PERIPHERAL.format(
            peripheral_type=peripheral_type, platform=platform, peripheral_config=peripheral_config
        )

    @classmethod
    def format_sdk_prompt(cls, language: str, device_spec: str, protocol: str, **kwargs) -> str:
        """
        Format SDK generation prompt.

        Args:
            language: Programming language (python, cpp, javascript)
            device_spec: Device specification text
            protocol: Communication protocol
            **kwargs: Additional context

        Returns:
            Formatted prompt string
        """
        return cls.SOFTWARE_SDK.format(
            language=language, device_spec=device_spec, protocol=protocol
        )

    @classmethod
    def format_ui_prompt(cls, framework: str, device_name: str, features: str, **kwargs) -> str:
        """
        Format UI generation prompt.

        Args:
            framework: UI framework (react, vue, html)
            device_name: Name of the device
            features: Feature list text
            **kwargs: Additional context

        Returns:
            Formatted prompt string
        """
        return cls.UI_FRAMEWORK.format(
            framework=framework, device_name=device_name, features=features
        )

    @classmethod
    def format_agent_coordination_prompt(
        cls,
        task_description: str,
        agent_context: str,
        agent_role: str,
        integration_points: str,
        **kwargs,
    ) -> str:
        """
        Format agent coordination prompt.

        Args:
            task_description: Description of current task
            agent_context: Context from other agents
            agent_role: Role of current agent
            integration_points: Points of integration
            **kwargs: Additional context

        Returns:
            Formatted prompt string
        """
        return cls.AGENT_COORDINATION.format(
            task_description=task_description,
            agent_context=agent_context,
            agent_role=agent_role,
            integration_points=integration_points,
        )

    @classmethod
    def get_system_prompt(cls, agent_type: str) -> str:
        """
        Get system-level prompt for an agent type.

        Args:
            agent_type: Type of agent (firmware, software, ui, coordinator)

        Returns:
            System prompt for the agent
        """
        system_prompts = {
            "firmware": (
                "You are an expert embedded systems programmer with deep knowledge of "
                "microcontroller architectures, real-time systems, and hardware interfaces. "
                "You write efficient, production-ready firmware code following best practices."
            ),
            "software": (
                "You are an expert software engineer specializing in SDK and driver development. "
                "You create clean, well-documented APIs that are easy to use and maintain. "
                "You follow language-specific best practices and design patterns."
            ),
            "ui": (
                "You are an expert frontend developer with expertise in modern UI frameworks. "
                "You create responsive, accessible, and user-friendly interfaces. "
                "You follow component-based architecture and state management best practices."
            ),
            "coordinator": (
                "You are an expert system architect coordinating multiple specialized agents. "
                "You ensure consistency, compatibility, and quality across all generated components. "
                "You understand the big picture and maintain integration standards."
            ),
            "reviewer": (
                "You are an expert code reviewer with deep knowledge across multiple domains. "
                "You identify bugs, security issues, performance problems, and style inconsistencies. "
                "You provide constructive, actionable feedback."
            ),
        }

        return system_prompts.get(
            agent_type, "You are an expert programmer helping with code generation tasks."
        )

    @classmethod
    def add_context(cls, base_prompt: str, context: Dict[str, Any]) -> str:
        """
        Add additional context to a base prompt.

        Args:
            base_prompt: Base prompt template
            context: Dictionary of additional context

        Returns:
            Enhanced prompt with context
        """
        if not context:
            return base_prompt

        context_str = "\n\nAdditional Context:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"

        return base_prompt + context_str
