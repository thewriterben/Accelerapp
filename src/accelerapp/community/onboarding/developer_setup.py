"""
Developer onboarding and setup system.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OnboardingStep:
    """Represents an onboarding step."""

    number: int
    title: str
    description: str
    commands: List[str] = field(default_factory=list)
    verification_command: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class DeveloperProfile:
    """Represents a developer's profile."""

    username: str
    email: str
    experience_level: str  # beginner, intermediate, advanced
    interests: List[str] = field(default_factory=list)
    completed_steps: List[int] = field(default_factory=list)
    joined_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DeveloperOnboarding:
    """
    Manages developer onboarding with step-by-step setup guidance.
    """

    def __init__(self):
        """Initialize developer onboarding."""
        self.profiles: Dict[str, DeveloperProfile] = {}
        self.onboarding_steps: List[OnboardingStep] = []
        self._initialize_default_steps()

    def _initialize_default_steps(self):
        """Initialize default onboarding steps."""
        default_steps = [
            OnboardingStep(
                number=1,
                title="Install Python",
                description="Install Python 3.8 or higher",
                commands=["python --version"],
                verification_command="python --version",
                documentation_url="https://www.python.org/downloads/",
            ),
            OnboardingStep(
                number=2,
                title="Clone Repository",
                description="Clone the Accelerapp repository",
                commands=[
                    "git clone https://github.com/thewriterben/Accelerapp.git",
                    "cd Accelerapp",
                ],
                verification_command="git status",
            ),
            OnboardingStep(
                number=3,
                title="Install Dependencies",
                description="Install project dependencies",
                commands=["pip install -e .[dev]"],
                verification_command="pip list | grep accelerapp",
            ),
            OnboardingStep(
                number=4,
                title="Setup Pre-commit Hooks",
                description="Install and configure pre-commit hooks",
                commands=["pre-commit install"],
                verification_command="pre-commit --version",
            ),
            OnboardingStep(
                number=5,
                title="Run Tests",
                description="Verify your setup by running tests",
                commands=["pytest tests/"],
                verification_command="pytest tests/ -v",
            ),
            OnboardingStep(
                number=6,
                title="Explore Examples",
                description="Check out example projects",
                commands=["ls examples/", "python examples/platform_demo.py"],
            ),
        ]

        self.onboarding_steps = default_steps

    def create_profile(
        self,
        username: str,
        email: str,
        experience_level: str,
        interests: Optional[List[str]] = None,
    ) -> DeveloperProfile:
        """
        Create a developer profile.

        Args:
            username: Developer username
            email: Developer email
            experience_level: Experience level (beginner, intermediate, advanced)
            interests: List of interests

        Returns:
            Created DeveloperProfile
        """
        if experience_level not in ["beginner", "intermediate", "advanced"]:
            raise ValueError("Invalid experience level")

        profile = DeveloperProfile(
            username=username,
            email=email,
            experience_level=experience_level,
            interests=interests or [],
        )
        self.profiles[username] = profile
        return profile

    def get_profile(self, username: str) -> Optional[DeveloperProfile]:
        """
        Get a developer profile.

        Args:
            username: Developer username

        Returns:
            DeveloperProfile or None
        """
        return self.profiles.get(username)

    def get_next_step(self, username: str) -> Optional[OnboardingStep]:
        """
        Get the next onboarding step for a developer.

        Args:
            username: Developer username

        Returns:
            Next OnboardingStep or None if completed
        """
        profile = self.profiles.get(username)
        if not profile:
            return None

        for step in self.onboarding_steps:
            if step.number not in profile.completed_steps:
                return step

        return None

    def complete_step(self, username: str, step_number: int) -> bool:
        """
        Mark an onboarding step as complete.

        Args:
            username: Developer username
            step_number: Step number

        Returns:
            True if successful
        """
        profile = self.profiles.get(username)
        if not profile:
            return False

        if step_number not in profile.completed_steps:
            profile.completed_steps.append(step_number)
            profile.completed_steps.sort()
            return True
        return False

    def get_progress(self, username: str) -> Dict[str, Any]:
        """
        Get onboarding progress for a developer.

        Args:
            username: Developer username

        Returns:
            Progress dictionary
        """
        profile = self.profiles.get(username)
        if not profile:
            return {"error": "Profile not found"}

        total_steps = len(self.onboarding_steps)
        completed = len(profile.completed_steps)
        percentage = (completed / total_steps * 100) if total_steps > 0 else 0

        return {
            "username": username,
            "total_steps": total_steps,
            "completed_steps": completed,
            "remaining_steps": total_steps - completed,
            "progress_percentage": percentage,
            "is_complete": completed == total_steps,
        }

    def get_all_steps(self) -> List[OnboardingStep]:
        """
        Get all onboarding steps.

        Returns:
            List of OnboardingStep
        """
        return self.onboarding_steps

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get onboarding statistics.

        Returns:
            Statistics dictionary
        """
        total_developers = len(self.profiles)
        completed_onboarding = sum(
            1
            for p in self.profiles.values()
            if len(p.completed_steps) == len(self.onboarding_steps)
        )

        experience_levels = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for profile in self.profiles.values():
            experience_levels[profile.experience_level] += 1

        return {
            "total_developers": total_developers,
            "completed_onboarding": completed_onboarding,
            "in_progress": total_developers - completed_onboarding,
            "experience_levels": experience_levels,
            "total_steps": len(self.onboarding_steps),
        }
