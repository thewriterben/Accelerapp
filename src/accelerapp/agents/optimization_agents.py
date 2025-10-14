"""
Code optimization agents for performance, memory, and security analysis.
These agents provide automated code improvement suggestions.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class PerformanceOptimizationAgent(BaseAgent):
    """Agent for identifying and suggesting performance optimizations."""

    def __init__(self):
        """Initialize performance optimization agent."""
        capabilities = [
            "performance_analysis",
            "bottleneck_detection",
            "algorithm_optimization",
            "loop_optimization",
            "caching_suggestions",
        ]
        super().__init__("Performance Optimization Agent", capabilities)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze code for performance issues and suggest optimizations.

        Args:
            spec: Specification containing code to analyze
            context: Optional context information

        Returns:
            Analysis results and optimization suggestions
        """
        code = spec.get("code", "")
        language = spec.get("language", "unknown")

        issues = []
        suggestions = []

        # Check for common performance issues
        if "for" in code.lower() and "sleep" in code.lower():
            issues.append(
                {
                    "type": "blocking_operation",
                    "severity": "high",
                    "description": "Blocking sleep in loop detected",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Use non-blocking delays",
                    "description": "Replace blocking sleep with timer-based approach",
                    "impact": "high",
                }
            )

        # Check for inefficient string concatenation
        if "+=" in code and ("string" in code.lower() or "str" in code.lower()):
            issues.append(
                {
                    "type": "inefficient_operation",
                    "severity": "medium",
                    "description": "Inefficient string concatenation detected",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Use string builder/buffer",
                    "description": "Replace += with StringBuilder or list join",
                    "impact": "medium",
                }
            )

        # Check for nested loops
        loop_count = code.count("for") + code.count("while")
        if loop_count > 2:
            issues.append(
                {
                    "type": "algorithm_complexity",
                    "severity": "medium",
                    "description": f"Multiple nested loops detected ({loop_count} loops)",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Consider algorithm optimization",
                    "description": "Review algorithm complexity and consider alternatives",
                    "impact": "high",
                }
            )

        # Check for repeated function calls
        if code.count("()") > 10:
            suggestions.append(
                {
                    "title": "Consider result caching",
                    "description": "Cache frequently called function results",
                    "impact": "medium",
                }
            )

        return {
            "status": "success",
            "agent": self.name,
            "analysis": {
                "issues_found": len(issues),
                "issues": issues,
                "suggestions": suggestions,
                "estimated_improvement": self._estimate_improvement(issues),
            },
        }

    def _estimate_improvement(self, issues: List[Dict]) -> str:
        """Estimate potential performance improvement."""
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        if severity_counts["high"] > 0:
            return "significant (20-50% faster)"
        elif severity_counts["medium"] > 1:
            return "moderate (10-20% faster)"
        else:
            return "minor (5-10% faster)"

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "performance_optimization",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Identifies performance bottlenecks and suggests optimizations",
        }


class MemoryOptimizationAgent(BaseAgent):
    """Agent for memory usage optimization and leak detection."""

    def __init__(self):
        """Initialize memory optimization agent."""
        capabilities = [
            "memory_analysis",
            "leak_detection",
            "allocation_optimization",
            "memory_profiling",
            "resource_management",
        ]
        super().__init__("Memory Optimization Agent", capabilities)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze code for memory issues and suggest optimizations.

        Args:
            spec: Specification containing code to analyze
            context: Optional context information

        Returns:
            Analysis results and optimization suggestions
        """
        code = spec.get("code", "")
        language = spec.get("language", "unknown")
        platform = spec.get("platform", "unknown")

        issues = []
        suggestions = []

        # Check for potential memory leaks
        has_malloc = "malloc" in code
        has_new = "new " in code or "new[" in code
        has_free = "free(" in code
        has_delete = "delete " in code or "delete[]" in code

        if has_malloc and not has_free:
            issues.append(
                {
                    "type": "memory_leak",
                    "severity": "critical",
                    "description": "malloc() without corresponding free()",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Add free() calls",
                    "description": "Ensure all malloc() allocations are freed",
                    "impact": "critical",
                }
            )

        if has_new and not has_delete:
            issues.append(
                {
                    "type": "memory_leak",
                    "severity": "critical",
                    "description": "new/new[] without corresponding delete/delete[]",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Add delete/delete[] calls",
                    "description": "Ensure all new allocations are deleted",
                    "impact": "critical",
                }
            )

        # Check for large stack allocations
        if "char" in code and "[" in code and "]" in code:
            # Simple heuristic: look for large arrays
            suggestions.append(
                {
                    "title": "Review array sizes",
                    "description": "Consider using dynamic allocation for large arrays",
                    "impact": "medium",
                }
            )

        # Check for string duplication
        string_count = code.count('"')
        if string_count > 10:
            suggestions.append(
                {
                    "title": "Use string constants",
                    "description": "Store frequently used strings in constants",
                    "impact": "low",
                }
            )

        # Platform-specific checks
        if platform in ["arduino", "esp32"]:
            # Check for Serial.print usage (uses RAM)
            if "Serial.print" in code and "F(" not in code:
                issues.append(
                    {
                        "type": "ram_usage",
                        "severity": "medium",
                        "description": "String literals using RAM instead of Flash",
                        "line": None,
                    }
                )
                suggestions.append(
                    {
                        "title": "Use F() macro",
                        "description": "Wrap string literals in F() to store in Flash",
                        "impact": "medium",
                    }
                )

        return {
            "status": "success",
            "agent": self.name,
            "analysis": {
                "issues_found": len(issues),
                "issues": issues,
                "suggestions": suggestions,
                "memory_estimate": self._estimate_memory_usage(code, platform),
            },
        }

    def _estimate_memory_usage(self, code: str, platform: str) -> Dict[str, Any]:
        """Estimate memory usage."""
        # Simple heuristic estimation
        var_count = code.count("int ") + code.count("float ") + code.count("char ")
        array_count = code.count("[")

        estimated_ram = var_count * 4 + array_count * 100

        return {
            "estimated_ram_bytes": estimated_ram,
            "platform": platform,
            "note": "Rough estimate based on code analysis",
        }

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "memory_optimization",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Analyzes memory usage and detects potential leaks",
        }


class CodeQualityAgent(BaseAgent):
    """Agent for code quality and best practices enforcement."""

    def __init__(self):
        """Initialize code quality agent."""
        capabilities = [
            "quality_analysis",
            "style_checking",
            "best_practices",
            "code_complexity",
            "maintainability",
        ]
        super().__init__("Code Quality Agent", capabilities)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze code quality and suggest improvements.

        Args:
            spec: Specification containing code to analyze
            context: Optional context information

        Returns:
            Analysis results and quality suggestions
        """
        code = spec.get("code", "")
        language = spec.get("language", "unknown")

        issues = []
        suggestions = []

        # Check function length
        functions = code.count("void ") + code.count("int ") + code.count("def ")
        lines = code.count("\n")
        avg_function_length = lines / max(functions, 1)

        if avg_function_length > 50:
            issues.append(
                {
                    "type": "function_length",
                    "severity": "medium",
                    "description": f"Functions are too long (avg {avg_function_length:.0f} lines)",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Break down large functions",
                    "description": "Split long functions into smaller, focused ones",
                    "impact": "high",
                }
            )

        # Check for magic numbers
        if any(char.isdigit() for char in code):
            suggestions.append(
                {
                    "title": "Use named constants",
                    "description": "Replace magic numbers with named constants",
                    "impact": "medium",
                }
            )

        # Check for comments
        comment_count = code.count("//") + code.count("/*")
        comment_ratio = comment_count / max(lines, 1)

        if comment_ratio < 0.1:
            issues.append(
                {
                    "type": "documentation",
                    "severity": "low",
                    "description": "Low comment density (documentation)",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Add code documentation",
                    "description": "Include comments explaining complex logic",
                    "impact": "medium",
                }
            )

        # Check for error handling
        has_error_handling = "try" in code or "catch" in code or "if" in code
        if not has_error_handling:
            issues.append(
                {
                    "type": "error_handling",
                    "severity": "high",
                    "description": "No error handling detected",
                    "line": None,
                }
            )
            suggestions.append(
                {
                    "title": "Add error handling",
                    "description": "Implement error checking and recovery",
                    "impact": "high",
                }
            )

        # Calculate quality score
        quality_score = self._calculate_quality_score(issues, code)

        return {
            "status": "success",
            "agent": self.name,
            "analysis": {
                "quality_score": quality_score,
                "grade": self._score_to_grade(quality_score),
                "issues_found": len(issues),
                "issues": issues,
                "suggestions": suggestions,
            },
        }

    def _calculate_quality_score(self, issues: List[Dict], code: str) -> float:
        """Calculate overall quality score (0-100)."""
        base_score = 100.0

        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "critical":
                base_score -= 30
            elif severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 10
            else:
                base_score -= 5

        return max(0.0, base_score)

    def _score_to_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "code_quality",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Analyzes code quality and enforces best practices",
        }


class SecurityAnalysisAgent(BaseAgent):
    """Agent for security vulnerability detection and analysis."""

    def __init__(self):
        """Initialize security analysis agent."""
        capabilities = [
            "vulnerability_detection",
            "security_audit",
            "buffer_overflow_check",
            "input_validation",
            "secure_coding",
        ]
        super().__init__("Security Analysis Agent", capabilities)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze code for security vulnerabilities.

        Args:
            spec: Specification containing code to analyze
            context: Optional context information

        Returns:
            Security analysis results
        """
        code = spec.get("code", "")
        language = spec.get("language", "unknown")

        vulnerabilities = []
        recommendations = []

        # Check for buffer overflow risks
        if "strcpy" in code or "strcat" in code or "gets" in code:
            vulnerabilities.append(
                {
                    "type": "buffer_overflow",
                    "severity": "critical",
                    "cwe": "CWE-120",
                    "description": "Unsafe string function detected",
                    "line": None,
                }
            )
            recommendations.append(
                {
                    "title": "Use safe string functions",
                    "description": "Replace strcpy with strncpy, strcat with strncat",
                    "priority": "critical",
                }
            )

        # Check for SQL injection (if database code)
        if "sql" in code.lower() or "query" in code.lower():
            if "+" in code and '"' in code:
                vulnerabilities.append(
                    {
                        "type": "sql_injection",
                        "severity": "critical",
                        "cwe": "CWE-89",
                        "description": "Potential SQL injection vulnerability",
                        "line": None,
                    }
                )
                recommendations.append(
                    {
                        "title": "Use parameterized queries",
                        "description": "Never concatenate user input into SQL queries",
                        "priority": "critical",
                    }
                )

        # Check for hardcoded credentials
        if "password" in code.lower() or "secret" in code.lower():
            if "=" in code and '"' in code:
                vulnerabilities.append(
                    {
                        "type": "hardcoded_credentials",
                        "severity": "high",
                        "cwe": "CWE-798",
                        "description": "Potential hardcoded credentials detected",
                        "line": None,
                    }
                )
                recommendations.append(
                    {
                        "title": "Use environment variables",
                        "description": "Store credentials in secure configuration",
                        "priority": "high",
                    }
                )

        # Check for integer overflow
        if "*" in code and ("int" in code or "long" in code):
            recommendations.append(
                {
                    "title": "Check for integer overflow",
                    "description": "Validate multiplication results for overflow",
                    "priority": "medium",
                }
            )

        # Check for input validation
        if "Serial.read" in code or "input" in code.lower():
            has_validation = "if" in code and (">" in code or "<" in code)
            if not has_validation:
                vulnerabilities.append(
                    {
                        "type": "missing_validation",
                        "severity": "medium",
                        "cwe": "CWE-20",
                        "description": "Input validation appears to be missing",
                        "line": None,
                    }
                )
                recommendations.append(
                    {
                        "title": "Validate all inputs",
                        "description": "Check range, type, and format of all inputs",
                        "priority": "high",
                    }
                )

        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities)

        return {
            "status": "success",
            "agent": self.name,
            "analysis": {
                "security_score": security_score,
                "risk_level": self._score_to_risk(security_score),
                "vulnerabilities_found": len(vulnerabilities),
                "vulnerabilities": vulnerabilities,
                "recommendations": recommendations,
            },
        }

    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> float:
        """Calculate security score (0-100)."""
        base_score = 100.0

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            if severity == "critical":
                base_score -= 40
            elif severity == "high":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            else:
                base_score -= 5

        return max(0.0, base_score)

    def _score_to_risk(self, score: float) -> str:
        """Convert security score to risk level."""
        if score >= 90:
            return "low"
        elif score >= 70:
            return "medium"
        elif score >= 50:
            return "high"
        else:
            return "critical"

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "security_analysis",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Detects security vulnerabilities and provides remediation advice",
        }


class RefactoringAgent(BaseAgent):
    """Agent for automated code refactoring suggestions."""

    def __init__(self):
        """Initialize refactoring agent."""
        capabilities = [
            "code_refactoring",
            "pattern_recognition",
            "code_smells",
            "design_improvement",
            "modularity",
        ]
        super().__init__("Refactoring Agent", capabilities)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze code and suggest refactoring opportunities.

        Args:
            spec: Specification containing code to analyze
            context: Optional context information

        Returns:
            Refactoring suggestions
        """
        code = spec.get("code", "")
        language = spec.get("language", "unknown")

        code_smells = []
        refactoring_suggestions = []

        # Check for duplicate code
        lines = code.split("\n")
        duplicates = self._find_duplicates(lines)
        if duplicates:
            code_smells.append(
                {
                    "type": "duplicate_code",
                    "severity": "medium",
                    "description": f"Found {len(duplicates)} duplicate code blocks",
                }
            )
            refactoring_suggestions.append(
                {
                    "title": "Extract common code",
                    "description": "Create functions for duplicate code blocks",
                    "technique": "Extract Method",
                    "benefit": "Improves maintainability and reduces errors",
                }
            )

        # Check for long parameter lists
        if "(" in code:
            param_counts = [line.count(",") for line in lines if "(" in line]
            max_params = max(param_counts) if param_counts else 0

            if max_params > 4:
                code_smells.append(
                    {
                        "type": "long_parameter_list",
                        "severity": "medium",
                        "description": f"Function with {max_params + 1} parameters detected",
                    }
                )
                refactoring_suggestions.append(
                    {
                        "title": "Introduce parameter object",
                        "description": "Group related parameters into a structure",
                        "technique": "Introduce Parameter Object",
                        "benefit": "Simplifies function signatures",
                    }
                )

        # Check for god object/class
        method_count = code.count("void ") + code.count("int ") + code.count("bool ")
        if method_count > 10:
            code_smells.append(
                {
                    "type": "god_object",
                    "severity": "high",
                    "description": "Too many methods in one class/file",
                }
            )
            refactoring_suggestions.append(
                {
                    "title": "Split responsibilities",
                    "description": "Break large class into smaller, focused classes",
                    "technique": "Extract Class",
                    "benefit": "Improves modularity and testability",
                }
            )

        # Check for nested conditionals
        indent_levels = [len(line) - len(line.lstrip()) for line in lines]
        max_indent = max(indent_levels) if indent_levels else 0

        if max_indent > 12:  # More than 3 levels
            code_smells.append(
                {
                    "type": "complex_conditionals",
                    "severity": "medium",
                    "description": "Deeply nested conditionals detected",
                }
            )
            refactoring_suggestions.append(
                {
                    "title": "Simplify conditionals",
                    "description": "Use guard clauses or extract to functions",
                    "technique": "Replace Nested Conditional with Guard Clauses",
                    "benefit": "Improves readability",
                }
            )

        return {
            "status": "success",
            "agent": self.name,
            "analysis": {
                "code_smells_found": len(code_smells),
                "code_smells": code_smells,
                "refactoring_suggestions": refactoring_suggestions,
                "priority": self._determine_priority(code_smells),
            },
        }

    def _find_duplicates(self, lines: List[str]) -> List[List[str]]:
        """Find duplicate code blocks."""
        duplicates = []
        # Simple heuristic: look for repeated sequences of 3+ lines
        for i in range(len(lines) - 2):
            block = lines[i : i + 3]
            block_str = "".join(block)
            if len(block_str.strip()) < 20:
                continue

            for j in range(i + 3, len(lines) - 2):
                compare_block = lines[j : j + 3]
                if block == compare_block:
                    duplicates.append(block)
                    break

        return duplicates

    def _determine_priority(self, code_smells: List[Dict]) -> str:
        """Determine refactoring priority."""
        if any(smell["severity"] == "high" for smell in code_smells):
            return "high"
        elif len(code_smells) > 3:
            return "medium"
        else:
            return "low"

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "refactoring",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Identifies code smells and suggests refactoring improvements",
        }
