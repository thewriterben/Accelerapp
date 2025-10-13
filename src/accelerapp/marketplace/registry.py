"""
Template registry for managing marketplace templates.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from .template import TemplateMetadata, TemplatePackage


class TemplateRegistry:
    """
    Manages template registration and storage.
    Provides CRUD operations for templates.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize template registry.
        
        Args:
            storage_path: Path to store templates
        """
        self.storage_path = storage_path or Path.home() / '.accelerapp' / 'templates'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, TemplateMetadata] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from storage."""
        for template_dir in self.storage_path.iterdir():
            if template_dir.is_dir():
                try:
                    package = TemplatePackage.load_from_directory(template_dir)
                    self.templates[package.metadata.id] = package.metadata
                except Exception:
                    pass
    
    def register_template(
        self,
        package: TemplatePackage
    ) -> bool:
        """
        Register a new template.
        
        Args:
            package: Template package to register
            
        Returns:
            True if registered successfully
        """
        template_id = package.metadata.id
        
        if template_id in self.templates:
            return False
        
        # Save to storage
        template_dir = self.storage_path / template_id
        package.save_to_directory(template_dir)
        
        # Add to registry
        self.templates[template_id] = package.metadata
        
        return True
    
    def update_template(
        self,
        template_id: str,
        package: TemplatePackage
    ) -> bool:
        """
        Update an existing template.
        
        Args:
            template_id: Template identifier
            package: Updated template package
            
        Returns:
            True if updated successfully
        """
        if template_id not in self.templates:
            return False
        
        # Update metadata
        package.metadata.updated_at = datetime.utcnow().isoformat()
        
        # Save to storage
        template_dir = self.storage_path / template_id
        package.save_to_directory(template_dir)
        
        # Update registry
        self.templates[template_id] = package.metadata
        
        return True
    
    def get_template(self, template_id: str) -> Optional[TemplatePackage]:
        """
        Get a template package.
        
        Args:
            template_id: Template identifier
            
        Returns:
            TemplatePackage or None
        """
        if template_id not in self.templates:
            return None
        
        template_dir = self.storage_path / template_id
        if not template_dir.exists():
            return None
        
        return TemplatePackage.load_from_directory(template_dir)
    
    def get_metadata(self, template_id: str) -> Optional[TemplateMetadata]:
        """
        Get template metadata only.
        
        Args:
            template_id: Template identifier
            
        Returns:
            TemplateMetadata or None
        """
        return self.templates.get(template_id)
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if deleted successfully
        """
        if template_id not in self.templates:
            return False
        
        # Remove from storage
        template_dir = self.storage_path / template_id
        if template_dir.exists():
            import shutil
            shutil.rmtree(template_dir)
        
        # Remove from registry
        del self.templates[template_id]
        
        return True
    
    def list_templates(
        self,
        category: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[TemplateMetadata]:
        """
        List all templates with optional filters.
        
        Args:
            category: Filter by category
            platform: Filter by platform
            
        Returns:
            List of template metadata
        """
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if platform:
            templates = [t for t in templates if platform in t.platforms]
        
        return templates
    
    def increment_downloads(self, template_id: str):
        """
        Increment download count for a template.
        
        Args:
            template_id: Template identifier
        """
        if template_id in self.templates:
            self.templates[template_id].downloads += 1
    
    def update_rating(self, template_id: str, new_rating: float):
        """
        Update template rating.
        
        Args:
            template_id: Template identifier
            new_rating: New rating value
        """
        if template_id in self.templates:
            self.templates[template_id].rating = new_rating
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Statistics dictionary
        """
        categories = {}
        platforms = {}
        
        for template in self.templates.values():
            categories[template.category] = categories.get(template.category, 0) + 1
            for platform in template.platforms:
                platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            'total_templates': len(self.templates),
            'categories': categories,
            'platforms': platforms,
            'total_downloads': sum(t.downloads for t in self.templates.values()),
        }
