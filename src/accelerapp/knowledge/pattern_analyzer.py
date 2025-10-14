"""
Code pattern analyzer for learning from generated code.
Identifies common patterns and suggests optimizations.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class CodePattern:
    """Identified code pattern."""

    pattern_id: str
    pattern_type: str
    code_snippet: str
    frequency: int
    metadata: Dict[str, Any]
    first_seen: str
    last_seen: str


class PatternAnalyzer:
    """
    Analyzes generated code to identify patterns and improve quality.
    """

    def __init__(self):
        """Initialize pattern analyzer."""
        self.patterns: Dict[str, CodePattern] = {}

    def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code for patterns.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Analysis results
        """
        results = {
            "language": language,
            "line_count": len(code.split("\n")),
            "patterns": [],
            "suggestions": [],
        }

        # Simple pattern detection
        if language in ["c", "cpp"]:
            results["patterns"].extend(self._analyze_c_patterns(code))
        elif language == "python":
            results["patterns"].extend(self._analyze_python_patterns(code))

        return results

    def _analyze_c_patterns(self, code: str) -> List[str]:
        """Analyze C/C++ code patterns."""
        patterns = []

        if "for" in code:
            patterns.append("loop_pattern")
        if "malloc" in code or "free" in code:
            patterns.append("memory_management")
        if "struct" in code:
            patterns.append("data_structure")

        return patterns

    def _analyze_python_patterns(self, code: str) -> List[str]:
        """Analyze Python code patterns."""
        patterns = []

        if "class " in code:
            patterns.append("oop_pattern")
        if "def " in code:
            patterns.append("function_definition")
        if "import " in code:
            patterns.append("module_import")

        return patterns

    def record_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        code_snippet: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a code pattern."""
        now = datetime.now().isoformat()

        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = now
        else:
            self.patterns[pattern_id] = CodePattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                code_snippet=code_snippet,
                frequency=1,
                metadata=metadata or {},
                first_seen=now,
                last_seen=now,
            )

    def get_common_patterns(self, limit: int = 10) -> List[CodePattern]:
        """Get most common patterns."""
        sorted_patterns = sorted(self.patterns.values(), key=lambda p: p.frequency, reverse=True)
        return sorted_patterns[:limit]
