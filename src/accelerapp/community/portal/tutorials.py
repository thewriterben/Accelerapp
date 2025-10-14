"""
Interactive tutorial management system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class DifficultyLevel(Enum):
    """Tutorial difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class TutorialStep:
    """Represents a step in a tutorial."""

    number: int
    title: str
    description: str
    code_example: Optional[str] = None
    validation_script: Optional[str] = None


@dataclass
class Tutorial:
    """Represents an interactive tutorial."""

    id: str
    title: str
    description: str
    author: str
    difficulty: DifficultyLevel
    category: str
    estimated_time_minutes: int
    steps: List[TutorialStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completions: int = 0
    rating: float = 0.0


class TutorialManager:
    """
    Manages interactive tutorials with step-by-step guidance.
    """

    def __init__(self):
        """Initialize tutorial manager."""
        self.tutorials: Dict[str, Tutorial] = {}
        self.user_progress: Dict[str, Dict[str, int]] = {}  # user_id -> {tutorial_id: step}

    def create_tutorial(
        self,
        tutorial_id: str,
        title: str,
        description: str,
        author: str,
        difficulty: DifficultyLevel,
        category: str,
        estimated_time_minutes: int,
        tags: Optional[List[str]] = None,
        prerequisites: Optional[List[str]] = None,
    ) -> Tutorial:
        """
        Create a new tutorial.

        Args:
            tutorial_id: Unique tutorial identifier
            title: Tutorial title
            description: Tutorial description
            author: Tutorial author
            difficulty: Difficulty level
            category: Tutorial category
            estimated_time_minutes: Estimated completion time
            tags: Optional tags
            prerequisites: Optional prerequisite tutorials

        Returns:
            Created Tutorial
        """
        tutorial = Tutorial(
            id=tutorial_id,
            title=title,
            description=description,
            author=author,
            difficulty=difficulty,
            category=category,
            estimated_time_minutes=estimated_time_minutes,
            tags=tags or [],
            prerequisites=prerequisites or [],
        )
        self.tutorials[tutorial_id] = tutorial
        return tutorial

    def add_step(
        self,
        tutorial_id: str,
        step_number: int,
        title: str,
        description: str,
        code_example: Optional[str] = None,
        validation_script: Optional[str] = None,
    ) -> bool:
        """
        Add a step to a tutorial.

        Args:
            tutorial_id: Tutorial identifier
            step_number: Step number
            title: Step title
            description: Step description
            code_example: Optional code example
            validation_script: Optional validation script

        Returns:
            True if successful
        """
        if tutorial_id not in self.tutorials:
            return False

        step = TutorialStep(
            number=step_number,
            title=title,
            description=description,
            code_example=code_example,
            validation_script=validation_script,
        )
        self.tutorials[tutorial_id].steps.append(step)
        self.tutorials[tutorial_id].steps.sort(key=lambda s: s.number)
        return True

    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """
        Get a tutorial by ID.

        Args:
            tutorial_id: Tutorial identifier

        Returns:
            Tutorial or None
        """
        return self.tutorials.get(tutorial_id)

    def list_tutorials(
        self,
        difficulty: Optional[DifficultyLevel] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Tutorial]:
        """
        List tutorials with optional filters.

        Args:
            difficulty: Filter by difficulty
            category: Filter by category
            tags: Filter by tags

        Returns:
            List of Tutorial
        """
        tutorials = list(self.tutorials.values())

        if difficulty:
            tutorials = [t for t in tutorials if t.difficulty == difficulty]

        if category:
            tutorials = [t for t in tutorials if t.category == category]

        if tags:
            tutorials = [t for t in tutorials if any(tag in t.tags for tag in tags)]

        return tutorials

    def start_tutorial(self, user_id: str, tutorial_id: str) -> bool:
        """
        Start a tutorial for a user.

        Args:
            user_id: User identifier
            tutorial_id: Tutorial identifier

        Returns:
            True if successful
        """
        if tutorial_id not in self.tutorials:
            return False

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        self.user_progress[user_id][tutorial_id] = 0
        return True

    def complete_step(self, user_id: str, tutorial_id: str, step_number: int) -> bool:
        """
        Mark a tutorial step as complete.

        Args:
            user_id: User identifier
            tutorial_id: Tutorial identifier
            step_number: Step number

        Returns:
            True if successful
        """
        if tutorial_id not in self.tutorials:
            return False

        if user_id not in self.user_progress:
            return False

        if tutorial_id not in self.user_progress[user_id]:
            return False

        self.user_progress[user_id][tutorial_id] = step_number
        return True

    def get_progress(self, user_id: str, tutorial_id: str) -> Optional[int]:
        """
        Get user progress in a tutorial.

        Args:
            user_id: User identifier
            tutorial_id: Tutorial identifier

        Returns:
            Current step number or None
        """
        if user_id not in self.user_progress:
            return None
        return self.user_progress[user_id].get(tutorial_id)

    def complete_tutorial(self, user_id: str, tutorial_id: str) -> bool:
        """
        Mark a tutorial as complete.

        Args:
            user_id: User identifier
            tutorial_id: Tutorial identifier

        Returns:
            True if successful
        """
        if tutorial_id not in self.tutorials:
            return False

        tutorial = self.tutorials[tutorial_id]
        if user_id in self.user_progress and tutorial_id in self.user_progress[user_id]:
            self.user_progress[user_id][tutorial_id] = len(tutorial.steps)
            tutorial.completions += 1
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get tutorial statistics.

        Returns:
            Statistics dictionary
        """
        total_tutorials = len(self.tutorials)
        total_completions = sum(t.completions for t in self.tutorials.values())
        tutorials_by_difficulty = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0,
        }

        for tutorial in self.tutorials.values():
            tutorials_by_difficulty[tutorial.difficulty.value] += 1

        return {
            "total_tutorials": total_tutorials,
            "total_completions": total_completions,
            "tutorials_by_difficulty": tutorials_by_difficulty,
            "average_rating": (
                sum(t.rating for t in self.tutorials.values()) / total_tutorials
                if total_tutorials > 0
                else 0.0
            ),
        }
