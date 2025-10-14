"""
Community project showcase system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ShowcaseProject:
    """Represents a community project in the showcase."""

    id: str
    title: str
    description: str
    author: str
    hardware_platform: str
    repository_url: Optional[str] = None
    demo_video_url: Optional[str] = None
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    views: int = 0
    likes: int = 0
    is_featured: bool = False


class ProjectShowcase:
    """
    Manages community project showcase with featured projects and galleries.
    """

    def __init__(self):
        """Initialize project showcase."""
        self.projects: Dict[str, ShowcaseProject] = {}

    def submit_project(
        self,
        project_id: str,
        title: str,
        description: str,
        author: str,
        hardware_platform: str,
        repository_url: Optional[str] = None,
        demo_video_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
    ) -> ShowcaseProject:
        """
        Submit a project to the showcase.

        Args:
            project_id: Unique project identifier
            title: Project title
            description: Project description
            author: Project author
            hardware_platform: Hardware platform used
            repository_url: Optional repository URL
            demo_video_url: Optional demo video URL
            tags: Optional tags
            technologies: Optional technologies used

        Returns:
            Created ShowcaseProject
        """
        project = ShowcaseProject(
            id=project_id,
            title=title,
            description=description,
            author=author,
            hardware_platform=hardware_platform,
            repository_url=repository_url,
            demo_video_url=demo_video_url,
            tags=tags or [],
            technologies=technologies or [],
        )
        self.projects[project_id] = project
        return project

    def add_image(self, project_id: str, image_url: str) -> bool:
        """
        Add an image to a project.

        Args:
            project_id: Project identifier
            image_url: Image URL

        Returns:
            True if successful
        """
        if project_id in self.projects:
            self.projects[project_id].images.append(image_url)
            return True
        return False

    def get_project(self, project_id: str) -> Optional[ShowcaseProject]:
        """
        Get a project by ID.

        Args:
            project_id: Project identifier

        Returns:
            ShowcaseProject or None
        """
        project = self.projects.get(project_id)
        if project:
            project.views += 1
        return project

    def list_projects(
        self,
        hardware_platform: Optional[str] = None,
        tags: Optional[List[str]] = None,
        featured_only: bool = False,
    ) -> List[ShowcaseProject]:
        """
        List projects with optional filters.

        Args:
            hardware_platform: Filter by hardware platform
            tags: Filter by tags
            featured_only: Show only featured projects

        Returns:
            List of ShowcaseProject
        """
        projects = list(self.projects.values())

        if hardware_platform:
            projects = [p for p in projects if p.hardware_platform == hardware_platform]

        if tags:
            projects = [p for p in projects if any(tag in p.tags for tag in tags)]

        if featured_only:
            projects = [p for p in projects if p.is_featured]

        # Sort: featured first, then by likes
        projects.sort(key=lambda p: (not p.is_featured, -p.likes))
        return projects

    def like_project(self, project_id: str) -> bool:
        """
        Like a project.

        Args:
            project_id: Project identifier

        Returns:
            True if successful
        """
        if project_id in self.projects:
            self.projects[project_id].likes += 1
            return True
        return False

    def feature_project(self, project_id: str, featured: bool = True) -> bool:
        """
        Feature or unfeature a project.

        Args:
            project_id: Project identifier
            featured: Featured status

        Returns:
            True if successful
        """
        if project_id in self.projects:
            self.projects[project_id].is_featured = featured
            return True
        return False

    def search_projects(self, query: str) -> List[ShowcaseProject]:
        """
        Search projects by title or description.

        Args:
            query: Search query

        Returns:
            List of matching ShowcaseProject
        """
        query_lower = query.lower()
        return [
            p
            for p in self.projects.values()
            if query_lower in p.title.lower() or query_lower in p.description.lower()
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get showcase statistics.

        Returns:
            Statistics dictionary
        """
        total_projects = len(self.projects)
        total_views = sum(p.views for p in self.projects.values())
        total_likes = sum(p.likes for p in self.projects.values())
        projects_by_platform = {}

        for project in self.projects.values():
            platform = project.hardware_platform
            projects_by_platform[platform] = projects_by_platform.get(platform, 0) + 1

        return {
            "total_projects": total_projects,
            "total_views": total_views,
            "total_likes": total_likes,
            "featured_projects": sum(1 for p in self.projects.values() if p.is_featured),
            "projects_by_platform": projects_by_platform,
        }
