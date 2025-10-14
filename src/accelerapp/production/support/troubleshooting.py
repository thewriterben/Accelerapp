"""
Troubleshooting guide and support system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Issue:
    """Represents a common issue."""

    id: str
    title: str
    description: str
    category: str
    symptoms: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)
    related_docs: List[str] = field(default_factory=list)


@dataclass
class SupportTicket:
    """Represents a support ticket."""

    ticket_id: str
    user: str
    subject: str
    description: str
    status: str  # open, in_progress, resolved, closed
    priority: str  # low, medium, high, critical
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    responses: List[str] = field(default_factory=list)


class TroubleshootingGuide:
    """
    Troubleshooting guide and support ticket system.
    """

    def __init__(self):
        """Initialize troubleshooting guide."""
        self.issues: Dict[str, Issue] = {}
        self.tickets: Dict[str, SupportTicket] = {}
        self._initialize_common_issues()

    def _initialize_common_issues(self):
        """Initialize common issues database."""
        common_issues = [
            Issue(
                id="installation-failed",
                title="Installation Failed",
                description="Unable to install Accelerapp dependencies",
                category="installation",
                symptoms=[
                    "pip install fails with error",
                    "Missing dependencies",
                    "Python version incompatibility",
                ],
                solutions=[
                    "Ensure Python 3.8+ is installed: python --version",
                    "Upgrade pip: python -m pip install --upgrade pip",
                    "Install with: pip install -e .[dev]",
                    "Check requirements.txt for conflicts",
                ],
                related_docs=[
                    "README.md#installation",
                    "docs/TROUBLESHOOTING.md",
                ],
            ),
            Issue(
                id="generation-failed",
                title="Code Generation Failed",
                description="Firmware/software generation fails",
                category="generation",
                symptoms=[
                    "accelerapp generate command fails",
                    "Invalid YAML configuration",
                    "Platform not supported error",
                ],
                solutions=[
                    "Validate YAML syntax: accelerapp validate config.yaml",
                    "Check platform spelling (arduino, esp32, stm32)",
                    "Ensure all required fields are present",
                    "Review examples/ directory for reference",
                ],
                related_docs=[
                    "docs/CONFIGURATION.md",
                    "examples/config.yaml",
                ],
            ),
            Issue(
                id="hardware-connection",
                title="Hardware Connection Issues",
                description="Unable to connect to hardware device",
                category="hardware",
                symptoms=[
                    "Serial port not found",
                    "Permission denied errors",
                    "Upload fails",
                ],
                solutions=[
                    "Check device is connected: ls /dev/tty*",
                    "Add user to dialout group: sudo usermod -a -G dialout $USER",
                    "Install USB drivers for your hardware",
                    "Try different USB cable/port",
                ],
                related_docs=[
                    "docs/HARDWARE_SETUP.md",
                ],
            ),
            Issue(
                id="performance-slow",
                title="Slow Performance",
                description="Code generation or execution is slow",
                category="performance",
                symptoms=[
                    "Generation takes too long",
                    "High CPU/memory usage",
                    "System becomes unresponsive",
                ],
                solutions=[
                    "Enable caching: set ACCELERAPP_CACHE=true",
                    "Reduce parallel workers if memory constrained",
                    "Clear cache: rm -rf ~/.accelerapp/cache",
                    "Check system resources: top or htop",
                ],
                related_docs=[
                    "docs/PERFORMANCE.md",
                ],
            ),
        ]

        for issue in common_issues:
            self.issues[issue.id] = issue

    def search_issues(self, query: str) -> List[Issue]:
        """
        Search for issues by query.

        Args:
            query: Search query

        Returns:
            List of matching Issue
        """
        query_lower = query.lower()
        results = []

        for issue in self.issues.values():
            if (
                query_lower in issue.title.lower()
                or query_lower in issue.description.lower()
                or any(query_lower in symptom.lower() for symptom in issue.symptoms)
            ):
                results.append(issue)

        return results

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """
        Get issue details.

        Args:
            issue_id: Issue identifier

        Returns:
            Issue or None
        """
        return self.issues.get(issue_id)

    def list_issues_by_category(self, category: str) -> List[Issue]:
        """
        List issues by category.

        Args:
            category: Issue category

        Returns:
            List of Issue
        """
        return [issue for issue in self.issues.values() if issue.category == category]

    def create_ticket(
        self,
        ticket_id: str,
        user: str,
        subject: str,
        description: str,
        priority: str = "medium",
    ) -> SupportTicket:
        """
        Create a support ticket.

        Args:
            ticket_id: Ticket identifier
            user: User identifier
            subject: Ticket subject
            description: Ticket description
            priority: Ticket priority

        Returns:
            Created SupportTicket
        """
        ticket = SupportTicket(
            ticket_id=ticket_id,
            user=user,
            subject=subject,
            description=description,
            status="open",
            priority=priority,
        )

        self.tickets[ticket_id] = ticket
        return ticket

    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """
        Update ticket status.

        Args:
            ticket_id: Ticket identifier
            status: New status

        Returns:
            True if successful
        """
        if ticket_id not in self.tickets:
            return False

        self.tickets[ticket_id].status = status
        self.tickets[ticket_id].updated_at = datetime.utcnow().isoformat()
        return True

    def add_ticket_response(self, ticket_id: str, response: str) -> bool:
        """
        Add a response to a ticket.

        Args:
            ticket_id: Ticket identifier
            response: Response message

        Returns:
            True if successful
        """
        if ticket_id not in self.tickets:
            return False

        self.tickets[ticket_id].responses.append(response)
        self.tickets[ticket_id].updated_at = datetime.utcnow().isoformat()
        return True

    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """
        Get ticket details.

        Args:
            ticket_id: Ticket identifier

        Returns:
            SupportTicket or None
        """
        return self.tickets.get(ticket_id)

    def list_tickets(
        self, status: Optional[str] = None, priority: Optional[str] = None
    ) -> List[SupportTicket]:
        """
        List support tickets.

        Args:
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            List of SupportTicket
        """
        tickets = list(self.tickets.values())

        if status:
            tickets = [t for t in tickets if t.status == status]

        if priority:
            tickets = [t for t in tickets if t.priority == priority]

        return tickets

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get support statistics.

        Returns:
            Statistics dictionary
        """
        total_issues = len(self.issues)
        total_tickets = len(self.tickets)

        tickets_by_status = {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
            "closed": 0,
        }

        for ticket in self.tickets.values():
            tickets_by_status[ticket.status] = tickets_by_status.get(ticket.status, 0) + 1

        return {
            "total_issues": total_issues,
            "total_tickets": total_tickets,
            "tickets_by_status": tickets_by_status,
            "resolution_rate": (
                (tickets_by_status["resolved"] + tickets_by_status["closed"]) / total_tickets * 100
                if total_tickets > 0
                else 0
            ),
        }
