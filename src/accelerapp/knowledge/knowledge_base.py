"""
Local knowledge base system for offline operation.
Provides vector storage and similarity search without external dependencies.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import math
from pathlib import Path


@dataclass
class KnowledgeEntry:
    """Entry in the knowledge base."""

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    category: str = "general"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEntry":
        """Create from dictionary."""
        return cls(**data)


class SimpleEmbedding:
    """
    Simple text embedding using TF-IDF style approach.
    Suitable for offline operation without external models.
    """

    def __init__(self, vocab_size: int = 1000):
        """
        Initialize embedding generator.

        Args:
            vocab_size: Size of vocabulary
        """
        self.vocab_size = vocab_size
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        import re

        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r"\w+", text.lower())
        return tokens

    def build_vocabulary(self, documents: List[str]) -> None:
        """Build vocabulary from documents."""
        from collections import Counter

        # Count word frequencies
        word_counts = Counter()
        for doc in documents:
            tokens = self.tokenize(doc)
            word_counts.update(set(tokens))

        # Select most common words
        most_common = word_counts.most_common(self.vocab_size)
        self.vocabulary = {word: idx for idx, (word, _) in enumerate(most_common)}

        # Calculate IDF
        num_docs = len(documents)
        for word in self.vocabulary:
            doc_count = sum(1 for doc in documents if word in self.tokenize(doc))
            self.idf[word] = math.log(num_docs / (1 + doc_count))

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        tokens = self.tokenize(text)
        embedding = [0.0] * len(self.vocabulary)

        # Count token frequencies in document
        from collections import Counter

        token_counts = Counter(tokens)

        # Calculate TF-IDF
        for token, count in token_counts.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                tf = count / len(tokens) if tokens else 0
                idf = self.idf.get(token, 0)
                embedding[idx] = tf * idf

        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding


class KnowledgeBase:
    """
    Local knowledge base with vector storage and search.
    Operates entirely offline without external dependencies.
    """

    def __init__(self, storage_dir: Optional[Path] = None, vocab_size: int = 1000):
        """
        Initialize knowledge base.

        Args:
            storage_dir: Directory for persistent storage
            vocab_size: Vocabulary size for embeddings
        """
        self.storage_dir = storage_dir or Path.home() / ".accelerapp" / "knowledge"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.entries: Dict[str, KnowledgeEntry] = {}
        self.embedding_model = SimpleEmbedding(vocab_size=vocab_size)
        self.index_file = self.storage_dir / "index.json"

        self._load_index()

    def add_entry(
        self,
        entry_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        category: str = "general",
    ) -> KnowledgeEntry:
        """
        Add entry to knowledge base.

        Args:
            entry_id: Unique entry identifier
            content: Entry content/text
            metadata: Optional metadata
            category: Entry category

        Returns:
            Created KnowledgeEntry
        """
        # Generate embedding
        embedding = self.embedding_model.embed(content)

        entry = KnowledgeEntry(
            id=entry_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding,
            category=category,
        )

        self.entries[entry_id] = entry
        self._save_index()

        return entry

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """
        Get entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            KnowledgeEntry if found, None otherwise
        """
        return self.entries.get(entry_id)

    def search(
        self, query: str, limit: int = 10, category: Optional[str] = None, threshold: float = 0.0
    ) -> List[Tuple[KnowledgeEntry, float]]:
        """
        Search for similar entries.

        Args:
            query: Search query
            limit: Maximum results
            category: Optional category filter
            threshold: Minimum similarity threshold

        Returns:
            List of (entry, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed(query)

        # Calculate similarities
        results = []
        for entry in self.entries.values():
            # Apply category filter
            if category and entry.category != category:
                continue

            if entry.embedding:
                similarity = self._cosine_similarity(query_embedding, entry.embedding)

                if similarity >= threshold:
                    results.append((entry, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def update_entry(
        self,
        entry_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update existing entry.

        Args:
            entry_id: Entry identifier
            content: Optional new content
            metadata: Optional new metadata

        Returns:
            True if updated, False if not found
        """
        entry = self.entries.get(entry_id)
        if not entry:
            return False

        if content is not None:
            entry.content = content
            entry.embedding = self.embedding_model.embed(content)

        if metadata is not None:
            entry.metadata.update(metadata)

        entry.updated_at = datetime.now().isoformat()
        self._save_index()

        return True

    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete entry.

        Args:
            entry_id: Entry identifier

        Returns:
            True if deleted, False if not found
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save_index()
            return True
        return False

    def rebuild_index(self) -> None:
        """Rebuild vocabulary and embeddings."""
        documents = [entry.content for entry in self.entries.values()]
        self.embedding_model.build_vocabulary(documents)

        # Re-embed all entries
        for entry in self.entries.values():
            entry.embedding = self.embedding_model.embed(entry.content)

        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.

        Returns:
            Statistics dictionary
        """
        categories = {}
        for entry in self.entries.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1

        return {
            "total_entries": len(self.entries),
            "categories": categories,
            "vocab_size": len(self.embedding_model.vocabulary),
            "storage_dir": str(self.storage_dir),
        }

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _save_index(self) -> None:
        """Save index to disk."""
        try:
            data = {
                "entries": {eid: entry.to_dict() for eid, entry in self.entries.items()},
                "vocabulary": self.embedding_model.vocabulary,
                "idf": self.embedding_model.idf,
            }

            with open(self.index_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save index: {e}")

    def _load_index(self) -> None:
        """Load index from disk."""
        if not self.index_file.exists():
            return

        try:
            with open(self.index_file, "r") as f:
                data = json.load(f)

            self.entries = {
                eid: KnowledgeEntry.from_dict(entry_data)
                for eid, entry_data in data.get("entries", {}).items()
            }

            self.embedding_model.vocabulary = data.get("vocabulary", {})
            self.embedding_model.idf = data.get("idf", {})

        except Exception as e:
            print(f"Warning: Failed to load index: {e}")
