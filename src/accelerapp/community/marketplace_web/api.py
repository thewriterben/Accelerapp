"""
Marketplace web interface API.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from accelerapp.marketplace import TemplateRegistry, TemplateSearch, TemplateMetadata


@dataclass
class Review:
    """Represents a template review."""

    template_id: str
    user: str
    rating: float
    comment: str
    helpful_count: int = 0


class MarketplaceAPI:
    """
    REST API for marketplace web interface.
    Provides endpoints for template discovery, ratings, and reviews.
    """

    def __init__(self, registry: Optional[TemplateRegistry] = None):
        """
        Initialize marketplace API.

        Args:
            registry: Template registry (creates new one if not provided)
        """
        self.registry = registry or TemplateRegistry()
        self.reviews: Dict[str, List[Review]] = {}

    def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "downloads",
    ) -> List[Dict[str, Any]]:
        """
        Search templates with filters.

        Args:
            query: Search query
            category: Filter by category
            platform: Filter by platform
            tags: Filter by tags
            min_rating: Minimum rating
            sort_by: Sort field

        Returns:
            List of template dictionaries
        """
        templates = self.registry.list_templates(category=category, platform=platform)
        search = TemplateSearch(templates)

        results = search.search(
            query=query, category=category, platform=platform, tags=tags, min_rating=min_rating, sort_by=sort_by
        )

        return [self._template_to_dict(t) for t in results]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template details.

        Args:
            template_id: Template identifier

        Returns:
            Template dictionary or None
        """
        metadata = self.registry.get_metadata(template_id)
        if not metadata:
            return None

        return self._template_to_dict(metadata)

    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular templates.

        Args:
            limit: Number of templates to return

        Returns:
            List of template dictionaries
        """
        templates = self.registry.list_templates()
        search = TemplateSearch(templates)
        popular = search.get_popular(limit=limit)

        return [self._template_to_dict(t) for t in popular]

    def get_top_rated_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top rated templates.

        Args:
            limit: Number of templates to return

        Returns:
            List of template dictionaries
        """
        templates = self.registry.list_templates()
        search = TemplateSearch(templates)
        top_rated = search.get_top_rated(limit=limit)

        return [self._template_to_dict(t) for t in top_rated]

    def add_review(
        self, template_id: str, user: str, rating: float, comment: str
    ) -> Optional[Review]:
        """
        Add a review to a template.

        Args:
            template_id: Template identifier
            user: Reviewer username
            rating: Rating (0-5)
            comment: Review comment

        Returns:
            Created Review or None
        """
        if template_id not in self.registry.templates:
            return None

        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5")

        review = Review(template_id=template_id, user=user, rating=rating, comment=comment)

        if template_id not in self.reviews:
            self.reviews[template_id] = []

        self.reviews[template_id].append(review)
        self._update_template_rating(template_id)

        return review

    def get_reviews(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Get reviews for a template.

        Args:
            template_id: Template identifier

        Returns:
            List of review dictionaries
        """
        reviews = self.reviews.get(template_id, [])
        return [
            {
                "user": r.user,
                "rating": r.rating,
                "comment": r.comment,
                "helpful_count": r.helpful_count,
            }
            for r in reviews
        ]

    def _update_template_rating(self, template_id: str):
        """Update template average rating."""
        reviews = self.reviews.get(template_id, [])
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            self.registry.update_rating(template_id, avg_rating)

    def get_categories(self) -> List[str]:
        """
        Get all template categories.

        Returns:
            List of categories
        """
        templates = self.registry.list_templates()
        search = TemplateSearch(templates)
        return search.get_categories()

    def get_platforms(self) -> List[str]:
        """
        Get all supported platforms.

        Returns:
            List of platforms
        """
        templates = self.registry.list_templates()
        search = TemplateSearch(templates)
        return search.get_platforms()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get marketplace statistics.

        Returns:
            Statistics dictionary
        """
        registry_stats = self.registry.get_statistics()
        total_reviews = sum(len(reviews) for reviews in self.reviews.values())

        return {
            **registry_stats,
            "total_reviews": total_reviews,
        }

    def _template_to_dict(self, template: TemplateMetadata) -> Dict[str, Any]:
        """Convert template metadata to dictionary."""
        return template.to_dict()
