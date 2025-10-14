"""
A/B Testing Framework for AI Agent Configurations.
Enables testing different agent configurations and measuring performance.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import random
from pathlib import Path
from collections import defaultdict


@dataclass
class TestVariant:
    """Represents a variant in an A/B test."""
    
    name: str
    config: Dict[str, Any]
    weight: float = 0.5  # Traffic allocation weight
    metrics: Dict[str, List[float]] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = defaultdict(list)


@dataclass
class ABTest:
    """Represents an A/B test configuration."""
    
    test_id: str
    name: str
    description: str
    variants: List[TestVariant]
    created_at: str
    status: str  # active, paused, completed
    total_samples: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert defaultdict to regular dict
        for variant in result["variants"]:
            if "metrics" in variant:
                variant["metrics"] = dict(variant["metrics"])
        return result


class ABTestingFramework:
    """
    A/B testing framework for AI agent configurations.
    Enables testing different configurations and measuring statistical significance.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize A/B testing framework.
        
        Args:
            storage_path: Path to store test data
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "ab_tests"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.tests: Dict[str, ABTest] = {}
        self._load_tests()
    
    def _load_tests(self) -> None:
        """Load test data from storage."""
        for test_file in self.storage_path.glob("*.json"):
            try:
                with open(test_file, "r") as f:
                    data = json.load(f)
                    test = ABTest(
                        test_id=data["test_id"],
                        name=data["name"],
                        description=data["description"],
                        variants=[
                            TestVariant(
                                name=v["name"],
                                config=v["config"],
                                weight=v["weight"],
                                metrics=defaultdict(list, v.get("metrics", {}))
                            )
                            for v in data["variants"]
                        ],
                        created_at=data["created_at"],
                        status=data["status"],
                        total_samples=data.get("total_samples", 0)
                    )
                    self.tests[test.test_id] = test
            except Exception:
                continue
    
    def _save_test(self, test: ABTest) -> None:
        """Save test data to storage."""
        test_file = self.storage_path / f"{test.test_id}.json"
        with open(test_file, "w") as f:
            json.dump(test.to_dict(), f, indent=2)
    
    def create_test(
        self,
        test_id: str,
        name: str,
        description: str,
        variants: List[Dict[str, Any]]
    ) -> ABTest:
        """
        Create a new A/B test.
        
        Args:
            test_id: Unique test identifier
            name: Test name
            description: Test description
            variants: List of variant configurations
            
        Returns:
            Created ABTest instance
        """
        test_variants = [
            TestVariant(
                name=v["name"],
                config=v["config"],
                weight=v.get("weight", 1.0 / len(variants))
            )
            for v in variants
        ]
        
        test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            variants=test_variants,
            created_at=datetime.utcnow().isoformat(),
            status="active"
        )
        
        self.tests[test_id] = test
        self._save_test(test)
        return test
    
    def select_variant(self, test_id: str) -> Optional[TestVariant]:
        """
        Select a variant based on weights (for traffic allocation).
        
        Args:
            test_id: Test identifier
            
        Returns:
            Selected TestVariant or None
        """
        test = self.tests.get(test_id)
        if not test or test.status != "active":
            return None
        
        # Weighted random selection
        total_weight = sum(v.weight for v in test.variants)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for variant in test.variants:
            cumulative += variant.weight
            if r <= cumulative:
                return variant
        
        return test.variants[-1]  # Fallback to last variant
    
    def record_metric(
        self,
        test_id: str,
        variant_name: str,
        metric_name: str,
        value: float
    ) -> bool:
        """
        Record a metric value for a variant.
        
        Args:
            test_id: Test identifier
            variant_name: Variant name
            metric_name: Metric name
            value: Metric value
            
        Returns:
            True if successful, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False
        
        for variant in test.variants:
            if variant.name == variant_name:
                variant.metrics[metric_name].append(value)
                test.total_samples += 1
                self._save_test(test)
                return True
        
        return False
    
    def get_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test results with statistical analysis.
        
        Args:
            test_id: Test identifier
            
        Returns:
            Dictionary with test results
        """
        test = self.tests.get(test_id)
        if not test:
            return None
        
        results = {
            "test_id": test.test_id,
            "name": test.name,
            "status": test.status,
            "total_samples": test.total_samples,
            "variants": []
        }
        
        for variant in test.variants:
            variant_results = {
                "name": variant.name,
                "metrics": {}
            }
            
            for metric_name, values in variant.metrics.items():
                if values:
                    variant_results["metrics"][metric_name] = {
                        "count": len(values),
                        "mean": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "sum": sum(values)
                    }
                    
                    # Calculate variance and std dev
                    mean = variant_results["metrics"][metric_name]["mean"]
                    variance = sum((x - mean) ** 2 for x in values) / len(values)
                    variant_results["metrics"][metric_name]["variance"] = variance
                    variant_results["metrics"][metric_name]["std_dev"] = variance ** 0.5
            
            results["variants"].append(variant_results)
        
        return results
    
    def calculate_statistical_significance(
        self,
        test_id: str,
        metric_name: str,
        confidence_level: float = 0.95
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate statistical significance between variants.
        
        Args:
            test_id: Test identifier
            metric_name: Metric to analyze
            confidence_level: Confidence level (default 0.95)
            
        Returns:
            Dictionary with significance analysis
        """
        test = self.tests.get(test_id)
        if not test or len(test.variants) < 2:
            return None
        
        # Simple t-test approximation
        results = {
            "metric": metric_name,
            "confidence_level": confidence_level,
            "variants": []
        }
        
        for variant in test.variants:
            values = variant.metrics.get(metric_name, [])
            if values:
                mean = sum(values) / len(values)
                results["variants"].append({
                    "name": variant.name,
                    "mean": mean,
                    "sample_size": len(values)
                })
        
        # Determine if there's a clear winner
        if len(results["variants"]) >= 2:
            means = [v["mean"] for v in results["variants"]]
            max_mean = max(means)
            min_mean = min(means)
            
            # Simple check: if difference is > 10%, consider significant
            if max_mean > 0:
                diff_percentage = ((max_mean - min_mean) / max_mean) * 100
                results["significant"] = diff_percentage > 10
                results["winner"] = results["variants"][means.index(max_mean)]["name"]
                results["improvement_percentage"] = diff_percentage
            else:
                results["significant"] = False
        
        return results
    
    def pause_test(self, test_id: str) -> bool:
        """
        Pause an active test.
        
        Args:
            test_id: Test identifier
            
        Returns:
            True if successful, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False
        
        test.status = "paused"
        self._save_test(test)
        return True
    
    def complete_test(self, test_id: str) -> bool:
        """
        Mark a test as completed.
        
        Args:
            test_id: Test identifier
            
        Returns:
            True if successful, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False
        
        test.status = "completed"
        self._save_test(test)
        return True
    
    def list_tests(self, status: Optional[str] = None) -> List[ABTest]:
        """
        List all tests, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of ABTest instances
        """
        tests = list(self.tests.values())
        if status:
            tests = [t for t in tests if t.status == status]
        return tests
