"""
Template manager for code generation using Jinja2.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template, TemplateNotFound


class TemplateManager:
    """
    Manages code templates using Jinja2 templating engine.
    Supports platform-specific and language-specific templates.
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize template manager.
        
        Args:
            template_dir: Directory containing templates (defaults to package templates)
        """
        if template_dir is None:
            # Use package templates directory
            template_dir = Path(__file__).parent / 'files'
        
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom filters
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup custom Jinja2 filters."""
        
        def upper_snake_case(text: str) -> str:
            """Convert to UPPER_SNAKE_CASE."""
            return text.upper().replace(' ', '_').replace('-', '_')
        
        def camel_case(text: str) -> str:
            """Convert to camelCase."""
            words = text.replace('_', ' ').replace('-', ' ').split()
            if not words:
                return text
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        
        def pascal_case(text: str) -> str:
            """Convert to PascalCase."""
            words = text.replace('_', ' ').replace('-', ' ').split()
            return ''.join(w.capitalize() for w in words)
        
        self.env.filters['upper_snake_case'] = upper_snake_case
        self.env.filters['camel_case'] = camel_case
        self.env.filters['pascal_case'] = pascal_case
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template file
            context: Template context variables
            
        Returns:
            Rendered template string
            
        Raises:
            TemplateNotFound: If template doesn't exist
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            # Return empty string if template not found
            # This allows graceful degradation
            return ""
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string directly.
        
        Args:
            template_string: Template string
            context: Template context variables
            
        Returns:
            Rendered string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_name: Name of template to check
            
        Returns:
            True if template exists
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
    
    def list_templates(self) -> list:
        """
        List all available templates.
        
        Returns:
            List of template names
        """
        return self.env.list_templates()
    
    def add_template_directory(self, directory: Path):
        """
        Add an additional template directory.
        
        Args:
            directory: Path to template directory
        """
        # Create new loader with multiple directories
        loader = FileSystemLoader([str(self.template_dir), str(directory)])
        self.env.loader = loader
    
    def generate_from_platform(
        self,
        platform: str,
        language: str,
        template_type: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate code using platform and language specific template.
        
        Args:
            platform: Target platform (arduino, esp32, etc.)
            language: Target language (c, cpp, python, etc.)
            template_type: Type of template (main, config, driver, etc.)
            context: Template context
            
        Returns:
            Generated code
        """
        # Try platform-language-specific template first
        template_name = f"{platform}/{language}/{template_type}.j2"
        if self.template_exists(template_name):
            return self.render_template(template_name, context)
        
        # Fall back to platform-specific template
        template_name = f"{platform}/{template_type}.j2"
        if self.template_exists(template_name):
            return self.render_template(template_name, context)
        
        # Fall back to language-specific template
        template_name = f"{language}/{template_type}.j2"
        if self.template_exists(template_name):
            return self.render_template(template_name, context)
        
        # Fall back to generic template
        template_name = f"generic/{template_type}.j2"
        if self.template_exists(template_name):
            return self.render_template(template_name, context)
        
        # No template found, return empty string
        return ""
    
    def create_template(self, template_name: str, content: str):
        """
        Create a new template file.
        
        Args:
            template_name: Name for the template
            content: Template content
        """
        template_path = self.template_dir / template_name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
    
    def get_template_context_defaults(self) -> Dict[str, Any]:
        """
        Get default context variables for templates.
        
        Returns:
            Dictionary of default context variables
        """
        return {
            'project_name': 'AccelerApp Project',
            'generated_by': 'Accelerapp Code Generator',
            'version': '0.1.0',
        }
