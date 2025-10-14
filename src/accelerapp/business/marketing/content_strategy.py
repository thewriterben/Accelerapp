"""
Content strategy and marketing management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ContentType(Enum):
    """Content types."""

    BLOG_POST = "blog_post"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    TUTORIAL = "tutorial"
    VIDEO = "video"
    WEBINAR = "webinar"


class ContentStatus(Enum):
    """Content status."""

    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Content:
    """Represents marketing content."""

    content_id: str
    title: str
    content_type: ContentType
    status: ContentStatus
    author: str
    summary: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    published_at: Optional[str] = None
    views: int = 0
    shares: int = 0


class ContentManager:
    """
    Manages marketing content, case studies, and content strategy.
    """

    def __init__(self):
        """Initialize content manager."""
        self.content: Dict[str, Content] = {}
        self._initialize_sample_content()

    def _initialize_sample_content(self):
        """Initialize sample content."""
        sample_content = [
            Content(
                content_id="getting-started",
                title="Getting Started with Accelerapp",
                content_type=ContentType.TUTORIAL,
                status=ContentStatus.PUBLISHED,
                author="Accelerapp Team",
                summary="Learn how to generate your first firmware with Accelerapp",
                tags=["tutorial", "getting-started", "firmware"],
                published_at=datetime.utcnow().isoformat(),
            ),
            Content(
                content_id="iot-case-study",
                title="Building IoT Devices with Accelerapp",
                content_type=ContentType.CASE_STUDY,
                status=ContentStatus.PUBLISHED,
                author="Tech Corp",
                summary="How Tech Corp reduced development time by 70% using Accelerapp",
                tags=["case-study", "iot", "success-story"],
                published_at=datetime.utcnow().isoformat(),
            ),
            Content(
                content_id="hardware-whitepaper",
                title="Modern Hardware Development Workflows",
                content_type=ContentType.WHITEPAPER,
                status=ContentStatus.PUBLISHED,
                author="Research Team",
                summary="Comprehensive guide to modern hardware development practices",
                tags=["whitepaper", "hardware", "best-practices"],
                published_at=datetime.utcnow().isoformat(),
            ),
        ]

        for content in sample_content:
            self.content[content.content_id] = content

    def create_content(
        self,
        content_id: str,
        title: str,
        content_type: ContentType,
        author: str,
        summary: str,
        tags: Optional[List[str]] = None,
    ) -> Content:
        """
        Create new content.

        Args:
            content_id: Content identifier
            title: Content title
            content_type: Type of content
            author: Content author
            summary: Content summary
            tags: Optional tags

        Returns:
            Created Content
        """
        content = Content(
            content_id=content_id,
            title=title,
            content_type=content_type,
            status=ContentStatus.DRAFT,
            author=author,
            summary=summary,
            tags=tags or [],
        )

        self.content[content_id] = content
        return content

    def publish_content(self, content_id: str) -> bool:
        """
        Publish content.

        Args:
            content_id: Content identifier

        Returns:
            True if successful
        """
        if content_id not in self.content:
            return False

        content = self.content[content_id]
        content.status = ContentStatus.PUBLISHED
        content.published_at = datetime.utcnow().isoformat()
        return True

    def get_content(self, content_id: str) -> Optional[Content]:
        """
        Get content by ID.

        Args:
            content_id: Content identifier

        Returns:
            Content or None
        """
        content = self.content.get(content_id)
        if content and content.status == ContentStatus.PUBLISHED:
            content.views += 1
        return content

    def list_content(
        self, content_type: Optional[ContentType] = None, status: Optional[ContentStatus] = None, tags: Optional[List[str]] = None
    ) -> List[Content]:
        """
        List content with optional filters.

        Args:
            content_type: Optional content type filter
            status: Optional status filter
            tags: Optional tags filter

        Returns:
            List of Content
        """
        contents = list(self.content.values())

        if content_type:
            contents = [c for c in contents if c.content_type == content_type]

        if status:
            contents = [c for c in contents if c.status == status]

        if tags:
            contents = [c for c in contents if any(tag in c.tags for tag in tags)]

        # Sort by published date
        contents.sort(key=lambda c: c.published_at or c.created_at, reverse=True)
        return contents

    def track_share(self, content_id: str) -> bool:
        """
        Track a content share.

        Args:
            content_id: Content identifier

        Returns:
            True if successful
        """
        if content_id in self.content:
            self.content[content_id].shares += 1
            return True
        return False

    def get_popular_content(self, limit: int = 10) -> List[Content]:
        """
        Get most popular content.

        Args:
            limit: Number of items to return

        Returns:
            List of Content
        """
        published_content = [c for c in self.content.values() if c.status == ContentStatus.PUBLISHED]
        published_content.sort(key=lambda c: (c.views + c.shares), reverse=True)
        return published_content[:limit]

    def get_content_calendar(self) -> Dict[str, List[Content]]:
        """
        Get content calendar organized by status.

        Returns:
            Dictionary of content by status
        """
        calendar = {
            "draft": [],
            "review": [],
            "published": [],
            "archived": [],
        }

        for content in self.content.values():
            calendar[content.status.value].append(content)

        return calendar

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get content statistics.

        Returns:
            Statistics dictionary
        """
        total_content = len(self.content)
        published_content = sum(1 for c in self.content.values() if c.status == ContentStatus.PUBLISHED)
        total_views = sum(c.views for c in self.content.values())
        total_shares = sum(c.shares for c in self.content.values())

        by_type = {}
        for content in self.content.values():
            content_type = content.content_type.value
            by_type[content_type] = by_type.get(content_type, 0) + 1

        return {
            "total_content": total_content,
            "published_content": published_content,
            "total_views": total_views,
            "total_shares": total_shares,
            "by_type": by_type,
            "engagement_rate": (total_shares / total_views * 100) if total_views > 0 else 0,
        }

    def generate_content_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive content report.

        Returns:
            Content report dictionary
        """
        stats = self.get_statistics()
        popular = self.get_popular_content(5)
        calendar = self.get_content_calendar()

        return {
            "summary": stats,
            "popular_content": [
                {
                    "title": c.title,
                    "type": c.content_type.value,
                    "views": c.views,
                    "shares": c.shares,
                }
                for c in popular
            ],
            "calendar_summary": {status: len(items) for status, items in calendar.items()},
        }
