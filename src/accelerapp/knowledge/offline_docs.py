"""
Offline documentation system for air-gapped environments.
Provides searchable local documentation and help.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class DocEntry:
    """Documentation entry."""

    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "related": self.related,
        }


class OfflineDocumentation:
    """
    Offline documentation system with search capabilities.
    """

    def __init__(self, docs_dir: Optional[Path] = None):
        """Initialize documentation system."""
        self.docs_dir = docs_dir or Path.home() / ".accelerapp" / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.entries: Dict[str, DocEntry] = {}
        self._load_docs()
        self._init_default_docs()

    def add_entry(self, entry: DocEntry) -> None:
        """Add documentation entry."""
        self.entries[entry.id] = entry
        self._save_docs()

    def get_entry(self, entry_id: str) -> Optional[DocEntry]:
        """Get documentation entry by ID."""
        return self.entries.get(entry_id)

    def search(self, query: str, limit: int = 10) -> List[DocEntry]:
        """Search documentation."""
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            if (
                query_lower in entry.title.lower()
                or query_lower in entry.content.lower()
                or any(query_lower in tag.lower() for tag in entry.tags)
            ):
                results.append(entry)

        return results[:limit]

    def get_by_category(self, category: str) -> List[DocEntry]:
        """Get all entries in a category."""
        return [e for e in self.entries.values() if e.category == category]

    def _init_default_docs(self) -> None:
        """Initialize default documentation."""
        if self.entries:
            return  # Already have docs

        default_docs = [
            DocEntry(
                id="getting-started",
                title="Getting Started with Accelerapp",
                content="Accelerapp is a platform for generating firmware, software, and UI code...",
                category="guide",
                tags=["beginner", "tutorial"],
            ),
            DocEntry(
                id="airgap-setup",
                title="Air-Gapped Deployment Setup",
                content="Instructions for deploying Accelerapp in air-gapped environments...",
                category="deployment",
                tags=["airgap", "offline", "setup"],
            ),
            DocEntry(
                id="llm-configuration",
                title="Configuring Local LLM Models",
                content="How to configure and use local LLM models with Ollama...",
                category="configuration",
                tags=["llm", "ollama", "models"],
            ),
        ]

        for doc in default_docs:
            self.add_entry(doc)

    def _save_docs(self) -> None:
        """Save documentation to disk."""
        try:
            data = {eid: e.to_dict() for eid, e in self.entries.items()}
            with open(self.docs_dir / "docs.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save docs: {e}")

    def _load_docs(self) -> None:
        """Load documentation from disk."""
        docs_file = self.docs_dir / "docs.json"
        if not docs_file.exists():
            return

        try:
            with open(docs_file, "r") as f:
                data = json.load(f)

            for eid, edata in data.items():
                self.entries[eid] = DocEntry(**edata)
        except Exception as e:
            print(f"Warning: Failed to load docs: {e}")
