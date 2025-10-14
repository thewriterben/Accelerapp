"""
Performance benchmarking system.
"""

from typing import Dict, Any, List, Callable, Optional
import time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Represents a benchmark test result."""

    name: str
    duration_ms: float
    operations_per_second: float
    memory_used_mb: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """
    Performance benchmarking and testing system.
    """

    def __init__(self):
        """Initialize performance benchmark."""
        self.results: List[BenchmarkResult] = []
        self.benchmarks: Dict[str, Callable] = {}

    def register_benchmark(self, name: str, func: Callable):
        """
        Register a benchmark function.

        Args:
            name: Benchmark name
            func: Benchmark function
        """
        self.benchmarks[name] = func

    def run_benchmark(self, name: str, iterations: int = 1000, **kwargs) -> BenchmarkResult:
        """
        Run a benchmark test.

        Args:
            name: Benchmark name
            iterations: Number of iterations
            **kwargs: Additional arguments for benchmark

        Returns:
            BenchmarkResult
        """
        if name not in self.benchmarks:
            raise ValueError(f"Benchmark not found: {name}")

        func = self.benchmarks[name]

        # Warm up
        for _ in range(10):
            try:
                func(**kwargs)
            except Exception:
                pass

        # Run benchmark
        start_time = time.perf_counter()
        success = True

        try:
            for _ in range(iterations):
                func(**kwargs)
        except Exception as e:
            success = False
            print(f"Benchmark failed: {e}")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        ops_per_second = iterations / (duration_ms / 1000) if duration_ms > 0 else 0

        result = BenchmarkResult(
            name=name,
            duration_ms=duration_ms,
            operations_per_second=ops_per_second,
            memory_used_mb=0.0,  # Simplified for now
            success=success,
            metadata={"iterations": iterations},
        )

        self.results.append(result)
        return result

    def run_all_benchmarks(self, iterations: int = 1000) -> List[BenchmarkResult]:
        """
        Run all registered benchmarks.

        Args:
            iterations: Number of iterations per benchmark

        Returns:
            List of BenchmarkResult
        """
        results = []
        for name in self.benchmarks:
            result = self.run_benchmark(name, iterations)
            results.append(result)
        return results

    def get_results(self, benchmark_name: Optional[str] = None) -> List[BenchmarkResult]:
        """
        Get benchmark results.

        Args:
            benchmark_name: Optional benchmark name filter

        Returns:
            List of BenchmarkResult
        """
        if benchmark_name:
            return [r for r in self.results if r.name == benchmark_name]
        return self.results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get benchmark statistics.

        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {"total_benchmarks": 0, "total_runs": 0}

        total_runs = len(self.results)
        successful_runs = sum(1 for r in self.results if r.success)
        avg_duration = sum(r.duration_ms for r in self.results) / total_runs
        avg_ops_per_sec = sum(r.operations_per_second for r in self.results) / total_runs

        return {
            "total_benchmarks": len(self.benchmarks),
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": total_runs - successful_runs,
            "avg_duration_ms": avg_duration,
            "avg_operations_per_second": avg_ops_per_sec,
        }

    def compare_results(self, baseline_name: str, current_name: str) -> Dict[str, Any]:
        """
        Compare two benchmark results.

        Args:
            baseline_name: Baseline benchmark name
            current_name: Current benchmark name

        Returns:
            Comparison dictionary
        """
        baseline_results = [r for r in self.results if r.name == baseline_name]
        current_results = [r for r in self.results if r.name == current_name]

        if not baseline_results or not current_results:
            return {"error": "Insufficient data for comparison"}

        baseline = baseline_results[-1]
        current = current_results[-1]

        duration_change = (current.duration_ms - baseline.duration_ms) / baseline.duration_ms * 100
        ops_change = (
            (current.operations_per_second - baseline.operations_per_second)
            / baseline.operations_per_second
            * 100
        )

        return {
            "baseline": baseline.name,
            "current": current.name,
            "duration_change_percent": duration_change,
            "operations_change_percent": ops_change,
            "improved": current.operations_per_second > baseline.operations_per_second,
        }


# Default benchmarks
def _default_code_generation_benchmark():
    """Benchmark code generation."""
    # Placeholder for actual code generation
    time.sleep(0.001)


def _default_template_processing_benchmark():
    """Benchmark template processing."""
    # Placeholder for actual template processing
    time.sleep(0.0005)
