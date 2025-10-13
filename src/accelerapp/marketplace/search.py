"""
Template search and filtering functionality.
"""

from typing import Dict, Any, List, Optional
from .template import TemplateMetadata


class TemplateSearch:
    """
    Search and filter templates in the marketplace.
    """
    
    def __init__(self, templates: List[TemplateMetadata]):
        """
        Initialize search engine.
        
        Args:
            templates: List of templates to search
        """
        self.templates = templates
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = 'downloads',
        ascending: bool = False
    ) -> List[TemplateMetadata]:
        """
        Search templates with multiple filters.
        
        Args:
            query: Search query for name/description
            category: Filter by category
            platform: Filter by platform
            tags: Filter by tags (all must match)
            min_rating: Minimum rating threshold
            sort_by: Field to sort by (downloads, rating, created_at, updated_at)
            ascending: Sort in ascending order
            
        Returns:
            List of matching templates
        """
        results = self.templates.copy()
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                t for t in results
                if query_lower in t.name.lower() or
                   query_lower in t.description.lower() or
                   query_lower in t.author.lower()
            ]
        
        # Category filter
        if category:
            results = [t for t in results if t.category == category]
        
        # Platform filter
        if platform:
            results = [t for t in results if platform in t.platforms]
        
        # Tags filter
        if tags:
            results = [
                t for t in results
                if all(tag in t.tags for tag in tags)
            ]
        
        # Rating filter
        if min_rating is not None:
            results = [t for t in results if t.rating >= min_rating]
        
        # Sort results
        if sort_by:
            reverse = not ascending
            
            if sort_by == 'downloads':
                results.sort(key=lambda t: t.downloads, reverse=reverse)
            elif sort_by == 'rating':
                results.sort(key=lambda t: t.rating, reverse=reverse)
            elif sort_by == 'created_at':
                results.sort(key=lambda t: t.created_at, reverse=reverse)
            elif sort_by == 'updated_at':
                results.sort(key=lambda t: t.updated_at, reverse=reverse)
            elif sort_by == 'name':
                results.sort(key=lambda t: t.name.lower(), reverse=reverse)
        
        return results
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of category names
        """
        categories = set(t.category for t in self.templates)
        return sorted(categories)
    
    def get_platforms(self) -> List[str]:
        """
        Get all unique platforms.
        
        Returns:
            List of platform names
        """
        platforms = set()
        for template in self.templates:
            platforms.update(template.platforms)
        return sorted(platforms)
    
    def get_tags(self) -> List[str]:
        """
        Get all unique tags.
        
        Returns:
            List of tag names
        """
        tags = set()
        for template in self.templates:
            tags.update(template.tags)
        return sorted(tags)
    
    def get_popular(self, limit: int = 10) -> List[TemplateMetadata]:
        """
        Get most popular templates by downloads.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of popular templates
        """
        sorted_templates = sorted(
            self.templates,
            key=lambda t: t.downloads,
            reverse=True
        )
        return sorted_templates[:limit]
    
    def get_top_rated(self, limit: int = 10) -> List[TemplateMetadata]:
        """
        Get top rated templates.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of top rated templates
        """
        sorted_templates = sorted(
            self.templates,
            key=lambda t: t.rating,
            reverse=True
        )
        return sorted_templates[:limit]
    
    def get_recent(self, limit: int = 10) -> List[TemplateMetadata]:
        """
        Get recently updated templates.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of recent templates
        """
        sorted_templates = sorted(
            self.templates,
            key=lambda t: t.updated_at or t.created_at,
            reverse=True
        )
        return sorted_templates[:limit]
