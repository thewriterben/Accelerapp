"""
Advanced Prompt Engineering System.
Provides sophisticated prompt templates and optimization.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class PromptTemplate:
    """Represents a prompt template with metadata."""
    
    name: str
    template: str
    variables: List[str]
    category: str
    description: str
    examples: List[Dict[str, Any]]
    optimization_hints: List[str]


class AdvancedPromptEngine:
    """
    Advanced prompt engineering system with template management.
    Provides optimized prompts for various AI tasks.
    """
    
    def __init__(self):
        """Initialize prompt engine with built-in templates."""
        self.templates: Dict[str, PromptTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize built-in prompt templates."""
        
        # Code generation template
        self.register_template(PromptTemplate(
            name="code_generation",
            template="""Generate {language} code for {purpose}.

Requirements:
{requirements}

Platform: {platform}
Constraints: {constraints}

Provide clean, well-documented code following best practices.""",
            variables=["language", "purpose", "requirements", "platform", "constraints"],
            category="generation",
            description="Generate code for specific platforms",
            examples=[{
                "language": "C++",
                "purpose": "motor control",
                "requirements": "PID control with speed feedback",
                "platform": "Arduino",
                "constraints": "Limited memory, real-time performance"
            }],
            optimization_hints=[
                "Be specific about requirements",
                "Include performance constraints",
                "Specify target platform details"
            ]
        ))
        
        # Code optimization template
        self.register_template(PromptTemplate(
            name="code_optimization",
            template="""Optimize the following {language} code for {optimization_goal}.

Code:
```{language}
{code}
```

Target Platform: {platform}
Constraints: {constraints}

Provide optimized version with explanation of improvements.""",
            variables=["language", "optimization_goal", "code", "platform", "constraints"],
            category="optimization",
            description="Optimize existing code",
            examples=[{
                "language": "C",
                "optimization_goal": "memory efficiency",
                "code": "// example code here",
                "platform": "ESP32",
                "constraints": "256KB RAM"
            }],
            optimization_hints=[
                "Specify clear optimization goals",
                "Include platform limitations",
                "Provide complete context"
            ]
        ))
        
        # Architecture design template
        self.register_template(PromptTemplate(
            name="architecture_design",
            template="""Design system architecture for {system_description}.

Requirements:
{requirements}

Constraints:
{constraints}

Components needed:
{components}

Provide architecture diagram description and component interactions.""",
            variables=["system_description", "requirements", "constraints", "components"],
            category="architecture",
            description="Design system architecture",
            examples=[{
                "system_description": "IoT sensor network",
                "requirements": "Real-time data collection, cloud sync",
                "constraints": "Low power, mesh networking",
                "components": "Sensors, gateway, cloud backend"
            }],
            optimization_hints=[
                "Describe system purpose clearly",
                "List all components",
                "Specify scalability requirements"
            ]
        ))
        
        # Debugging assistant template
        self.register_template(PromptTemplate(
            name="debugging_assistant",
            template="""Debug the following issue in {language} code:

Problem Description:
{problem}

Code:
```{language}
{code}
```

Error Message:
{error_message}

Platform: {platform}

Identify the issue and provide a fix with explanation.""",
            variables=["language", "problem", "code", "error_message", "platform"],
            category="debugging",
            description="Debug code issues",
            examples=[{
                "language": "Python",
                "problem": "Memory leak in long-running process",
                "code": "# code snippet",
                "error_message": "MemoryError after 2 hours",
                "platform": "Linux server"
            }],
            optimization_hints=[
                "Provide complete error messages",
                "Include relevant code context",
                "Describe expected vs actual behavior"
            ]
        ))
        
        # Test generation template
        self.register_template(PromptTemplate(
            name="test_generation",
            template="""Generate unit tests for the following {language} code:

Code to Test:
```{language}
{code}
```

Testing Framework: {framework}
Coverage Goal: {coverage_goal}

Generate comprehensive tests covering edge cases and error conditions.""",
            variables=["language", "code", "framework", "coverage_goal"],
            category="testing",
            description="Generate unit tests",
            examples=[{
                "language": "Python",
                "code": "def calculate(x, y): return x + y",
                "framework": "pytest",
                "coverage_goal": "100%"
            }],
            optimization_hints=[
                "Specify testing framework",
                "Include edge case requirements",
                "Define coverage expectations"
            ]
        ))
    
    def register_template(self, template: PromptTemplate) -> None:
        """
        Register a new prompt template.
        
        Args:
            template: PromptTemplate to register
        """
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name.
        
        Args:
            name: Template name
            
        Returns:
            PromptTemplate or None
        """
        return self.templates.get(name)
    
    def render_prompt(self, template_name: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Render a prompt from template with variables.
        
        Args:
            template_name: Name of template to use
            variables: Variables to substitute
            
        Returns:
            Rendered prompt string or None
        """
        template = self.templates.get(template_name)
        if not template:
            return None
        
        try:
            return template.template.format(**variables)
        except KeyError:
            # Missing required variables
            return None
    
    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """
        List available templates, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of PromptTemplate instances
        """
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    def optimize_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        optimization_goal: str = "clarity"
    ) -> Optional[str]:
        """
        Optimize a prompt for specific goals.
        
        Args:
            template_name: Template to use
            variables: Variables to substitute
            optimization_goal: Goal (clarity, conciseness, specificity)
            
        Returns:
            Optimized prompt or None
        """
        base_prompt = self.render_prompt(template_name, variables)
        if not base_prompt:
            return None
        
        template = self.templates[template_name]
        
        # Add optimization hints
        hints = "\n\n".join([f"- {hint}" for hint in template.optimization_hints])
        
        if optimization_goal == "clarity":
            optimized = f"{base_prompt}\n\nOptimization Focus: Provide clear, detailed explanations."
        elif optimization_goal == "conciseness":
            optimized = f"{base_prompt}\n\nOptimization Focus: Be concise and direct."
        elif optimization_goal == "specificity":
            optimized = f"{base_prompt}\n\nOptimization Focus: Include specific implementation details."
        else:
            optimized = base_prompt
        
        return optimized
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a template.
        
        Args:
            template_name: Template name
            
        Returns:
            Dictionary with template information
        """
        template = self.templates.get(template_name)
        if not template:
            return None
        
        return {
            "name": template.name,
            "category": template.category,
            "description": template.description,
            "variables": template.variables,
            "examples": template.examples,
            "optimization_hints": template.optimization_hints
        }
    
    def validate_variables(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that all required variables are provided.
        
        Args:
            template_name: Template name
            variables: Variables to validate
            
        Returns:
            Dictionary with validation results
        """
        template = self.templates.get(template_name)
        if not template:
            return {"valid": False, "error": "Template not found"}
        
        missing = [v for v in template.variables if v not in variables]
        
        return {
            "valid": len(missing) == 0,
            "missing_variables": missing,
            "provided_variables": list(variables.keys())
        }
