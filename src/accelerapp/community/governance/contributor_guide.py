"""
Contributor guide and governance system.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ContributionGuideline:
    """Represents a contribution guideline."""

    id: str
    title: str
    description: str
    category: str
    requirements: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class Contributor:
    """Represents a contributor."""

    username: str
    name: str
    email: str
    joined_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    contributions: int = 0
    badges: List[str] = field(default_factory=list)
    mentor: Optional[str] = None


class ContributorGuide:
    """
    Manages contributor guidelines and community standards.
    """

    def __init__(self):
        """Initialize contributor guide."""
        self.guidelines: Dict[str, ContributionGuideline] = {}
        self.contributors: Dict[str, Contributor] = {}
        self._initialize_default_guidelines()

    def _initialize_default_guidelines(self):
        """Initialize default contribution guidelines."""
        default_guidelines = [
            ContributionGuideline(
                id="code-style",
                title="Code Style Guidelines",
                description="Follow project coding standards",
                category="development",
                requirements=[
                    "Use Black formatter for Python code",
                    "Follow PEP 8 style guide",
                    "Add docstrings to all functions",
                    "Include type hints",
                ],
                examples=["See examples/ directory for reference implementations"],
            ),
            ContributionGuideline(
                id="testing",
                title="Testing Requirements",
                description="Write comprehensive tests",
                category="quality",
                requirements=[
                    "Write unit tests for new features",
                    "Maintain code coverage above 70%",
                    "Add integration tests for new modules",
                    "Run all tests before submitting PR",
                ],
            ),
            ContributionGuideline(
                id="documentation",
                title="Documentation Standards",
                description="Document all changes",
                category="documentation",
                requirements=[
                    "Update README for new features",
                    "Add docstrings to all public APIs",
                    "Include usage examples",
                    "Update CHANGELOG.md",
                ],
            ),
            ContributionGuideline(
                id="code-of-conduct",
                title="Code of Conduct",
                description="Community behavior standards",
                category="community",
                requirements=[
                    "Be respectful and inclusive",
                    "Welcome newcomers",
                    "Provide constructive feedback",
                    "Report violations to maintainers",
                ],
            ),
        ]

        for guideline in default_guidelines:
            self.guidelines[guideline.id] = guideline

    def add_guideline(
        self,
        guideline_id: str,
        title: str,
        description: str,
        category: str,
        requirements: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
    ) -> ContributionGuideline:
        """
        Add a new contribution guideline.

        Args:
            guideline_id: Guideline identifier
            title: Guideline title
            description: Guideline description
            category: Guideline category
            requirements: List of requirements
            examples: List of examples

        Returns:
            Created ContributionGuideline
        """
        guideline = ContributionGuideline(
            id=guideline_id,
            title=title,
            description=description,
            category=category,
            requirements=requirements or [],
            examples=examples or [],
        )
        self.guidelines[guideline_id] = guideline
        return guideline

    def get_guideline(self, guideline_id: str) -> Optional[ContributionGuideline]:
        """
        Get a guideline by ID.

        Args:
            guideline_id: Guideline identifier

        Returns:
            ContributionGuideline or None
        """
        return self.guidelines.get(guideline_id)

    def list_guidelines(self, category: Optional[str] = None) -> List[ContributionGuideline]:
        """
        List all guidelines with optional category filter.

        Args:
            category: Optional category filter

        Returns:
            List of ContributionGuideline
        """
        guidelines = list(self.guidelines.values())
        if category:
            guidelines = [g for g in guidelines if g.category == category]
        return guidelines

    def register_contributor(
        self, username: str, name: str, email: str, mentor: Optional[str] = None
    ) -> Contributor:
        """
        Register a new contributor.

        Args:
            username: Contributor username
            name: Contributor name
            email: Contributor email
            mentor: Optional mentor username

        Returns:
            Created Contributor
        """
        contributor = Contributor(username=username, name=name, email=email, mentor=mentor)
        self.contributors[username] = contributor
        return contributor

    def record_contribution(self, username: str) -> bool:
        """
        Record a contribution from a user.

        Args:
            username: Contributor username

        Returns:
            True if successful
        """
        if username in self.contributors:
            self.contributors[username].contributions += 1
            self._check_badges(username)
            return True
        return False

    def _check_badges(self, username: str):
        """Check and award badges based on contributions."""
        contributor = self.contributors[username]
        contributions = contributor.contributions

        badges_to_award = []
        if contributions >= 1 and "first-contribution" not in contributor.badges:
            badges_to_award.append("first-contribution")
        if contributions >= 10 and "contributor" not in contributor.badges:
            badges_to_award.append("contributor")
        if contributions >= 50 and "active-contributor" not in contributor.badges:
            badges_to_award.append("active-contributor")
        if contributions >= 100 and "core-contributor" not in contributor.badges:
            badges_to_award.append("core-contributor")

        contributor.badges.extend(badges_to_award)

    def get_contributor(self, username: str) -> Optional[Contributor]:
        """
        Get a contributor by username.

        Args:
            username: Contributor username

        Returns:
            Contributor or None
        """
        return self.contributors.get(username)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get contributor statistics.

        Returns:
            Statistics dictionary
        """
        total_contributors = len(self.contributors)
        total_contributions = sum(c.contributions for c in self.contributors.values())
        badges_awarded = sum(len(c.badges) for c in self.contributors.values())

        return {
            "total_contributors": total_contributors,
            "total_contributions": total_contributions,
            "badges_awarded": badges_awarded,
            "guidelines": len(self.guidelines),
        }
