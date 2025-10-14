"""
Template management system for code generation.
Handles template storage, versioning, and retrieval.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json


class TemplateCategory(Enum):
    """Template categories."""

    FIRMWARE = "firmware"
    SOFTWARE = "software"
    UI = "ui"
    DRIVER = "driver"
    CONFIG = "config"
    TEST = "test"


@dataclass
class Template:
    """Code template."""

    id: str
    name: str
    category: TemplateCategory
    content: str
    variables: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "content": self.content,
            "variables": self.variables,
            "description": self.description,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
        }


class TemplateManager:
    """
    Manages code templates with versioning and optimization.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize template manager."""
        self.storage_dir = storage_dir or Path.home() / ".accelerapp" / "templates"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, Template] = {}
        self._load_templates()

    def add_template(self, template: Template) -> None:
        """Add template to manager."""
        self.templates[template.id] = template
        self._save_templates()

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: Optional[TemplateCategory] = None) -> List[Template]:
        """List all templates, optionally filtered by category."""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def render_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """Render template with variables."""
        template = self.templates.get(template_id)
        if not template:
            return None

        # Simple variable substitution
        content = template.content
        for var, value in variables.items():
            content = content.replace(f"{{{{{var}}}}}", str(value))

        # Track usage
        template.usage_count += 1
        self._save_templates()

        return content

    def _save_templates(self) -> None:
        """Save templates to disk."""
        try:
            data = {tid: t.to_dict() for tid, t in self.templates.items()}
            with open(self.storage_dir / "templates.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save templates: {e}")

    def _load_templates(self) -> None:
        """Load templates from disk."""
        template_file = self.storage_dir / "templates.json"
        if not template_file.exists():
            return

        try:
            with open(template_file, "r") as f:
                data = json.load(f)

            for tid, tdata in data.items():
                tdata["category"] = TemplateCategory(tdata["category"])
                self.templates[tid] = Template(**tdata)
        except Exception as e:
            print(f"Warning: Failed to load templates: {e}")
