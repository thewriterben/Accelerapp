"""
Performance profiling and optimization system.
"""

from typing import Dict, Any, List, Callable, Optional
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProfileType(str, Enum):
    """Types of profiling."""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    FULL = "full"


@dataclass
class ProfileResult:
    """Performance profiling result."""
    
    function_name: str
    profile_type: ProfileType
    execution_time_ms: float
    memory_used_mb: float
    memory_peak_mb: float
    call_count: int
    cpu_percent: float
    hotspots: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceProfiler:
    """
    Profile and optimize application performance.
    """
    
    def __init__(self):
        """Initialize performance profiler."""
        self.profiles: List[ProfileResult] = []
        self.baseline_profiles: Dict[str, ProfileResult] = {}
        
        # Performance thresholds
        self.slow_threshold_ms = 100  # Functions slower than 100ms
        self.memory_threshold_mb = 50  # Memory usage above 50MB
        
    def profile_function(
        self,
        func: Callable,
        *args,
        profile_type: ProfileType = ProfileType.FULL,
        iterations: int = 1,
        **kwargs
    ) -> ProfileResult:
        """
        Profile a function's performance.
        
        Args:
            func: Function to profile
            *args: Positional arguments for function
            profile_type: Type of profiling to perform
            iterations: Number of iterations to run
            **kwargs: Keyword arguments for function
            
        Returns:
            ProfileResult object
        """
        function_name = func.__name__
        
        # Start memory profiling if needed
        if profile_type in (ProfileType.MEMORY, ProfileType.FULL):
            tracemalloc.start()
        
        # Run function and measure time
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Function execution failed: {e}")
        
        end_time = time.perf_counter()
        
        # Calculate execution time
        execution_time_ms = (end_time - start_time) * 1000 / iterations
        
        # Get memory stats
        memory_used_mb = 0.0
        memory_peak_mb = 0.0
        if profile_type in (ProfileType.MEMORY, ProfileType.FULL):
            current, peak = tracemalloc.get_traced_memory()
            memory_used_mb = current / 1024 / 1024
            memory_peak_mb = peak / 1024 / 1024
            tracemalloc.stop()
        
        # Identify hotspots
        hotspots = self._identify_hotspots(function_name, execution_time_ms, memory_used_mb)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            execution_time_ms, memory_used_mb, hotspots
        )
        
        # Estimate CPU usage (simplified)
        cpu_percent = min(100.0, (execution_time_ms / 1000) * 100)
        
        result = ProfileResult(
            function_name=function_name,
            profile_type=profile_type,
            execution_time_ms=execution_time_ms,
            memory_used_mb=memory_used_mb,
            memory_peak_mb=memory_peak_mb,
            call_count=iterations,
            cpu_percent=cpu_percent,
            hotspots=hotspots,
            recommendations=recommendations,
            metadata={"args_count": len(args), "kwargs_count": len(kwargs)}
        )
        
        self.profiles.append(result)
        return result
    
    def _identify_hotspots(
        self,
        function_name: str,
        execution_time_ms: float,
        memory_mb: float
    ) -> List[Dict[str, Any]]:
        """
        Identify performance hotspots.
        
        Args:
            function_name: Name of profiled function
            execution_time_ms: Execution time in milliseconds
            memory_mb: Memory usage in MB
            
        Returns:
            List of hotspots
        """
        hotspots = []
        
        # Check for slow execution
        if execution_time_ms > self.slow_threshold_ms:
            hotspots.append({
                "type": "slow_execution",
                "function": function_name,
                "execution_time_ms": execution_time_ms,
                "threshold_ms": self.slow_threshold_ms,
                "severity": "high" if execution_time_ms > self.slow_threshold_ms * 5 else "medium"
            })
        
        # Check for high memory usage
        if memory_mb > self.memory_threshold_mb:
            hotspots.append({
                "type": "high_memory",
                "function": function_name,
                "memory_mb": memory_mb,
                "threshold_mb": self.memory_threshold_mb,
                "severity": "high" if memory_mb > self.memory_threshold_mb * 2 else "medium"
            })
        
        return hotspots
    
    def _generate_recommendations(
        self,
        execution_time_ms: float,
        memory_mb: float,
        hotspots: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate optimization recommendations.
        
        Args:
            execution_time_ms: Execution time
            memory_mb: Memory usage
            hotspots: Identified hotspots
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Time-based recommendations
        if execution_time_ms > self.slow_threshold_ms:
            recommendations.append(
                f"Function execution time ({execution_time_ms:.2f}ms) exceeds threshold. "
                "Consider optimizing algorithms or using caching."
            )
            
            if execution_time_ms > 1000:
                recommendations.append(
                    "Very slow execution detected. Consider asynchronous processing or "
                    "breaking down into smaller operations."
                )
        
        # Memory-based recommendations
        if memory_mb > self.memory_threshold_mb:
            recommendations.append(
                f"High memory usage ({memory_mb:.2f}MB) detected. "
                "Consider using generators, streaming, or batch processing."
            )
            
            if memory_mb > 100:
                recommendations.append(
                    "Excessive memory usage. Review data structures and implement "
                    "memory-efficient algorithms."
                )
        
        # Hotspot-based recommendations
        for hotspot in hotspots:
            if hotspot["severity"] == "high":
                recommendations.append(
                    f"Critical performance issue in {hotspot['type']}: "
                    f"Immediate optimization required."
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance within acceptable thresholds. No immediate action needed.")
        
        return recommendations
    
    def compare_with_baseline(self, function_name: str) -> Dict[str, Any]:
        """
        Compare current profile with baseline.
        
        Args:
            function_name: Name of function to compare
            
        Returns:
            Comparison results
        """
        baseline = self.baseline_profiles.get(function_name)
        
        if not baseline:
            return {
                "error": "No baseline found for function",
                "function": function_name
            }
        
        # Get most recent profile for this function
        current = None
        for profile in reversed(self.profiles):
            if profile.function_name == function_name:
                current = profile
                break
        
        if not current:
            return {
                "error": "No current profile found for function",
                "function": function_name
            }
        
        # Calculate changes
        time_change = (
            (current.execution_time_ms - baseline.execution_time_ms) /
            baseline.execution_time_ms * 100
        )
        
        memory_change = 0.0
        if baseline.memory_used_mb > 0:
            memory_change = (
                (current.memory_used_mb - baseline.memory_used_mb) /
                baseline.memory_used_mb * 100
            )
        
        return {
            "function": function_name,
            "baseline_time_ms": baseline.execution_time_ms,
            "current_time_ms": current.execution_time_ms,
            "time_change_percent": time_change,
            "baseline_memory_mb": baseline.memory_used_mb,
            "current_memory_mb": current.memory_used_mb,
            "memory_change_percent": memory_change,
            "performance_improved": time_change < 0,
            "regression_detected": time_change > 10  # More than 10% slower
        }
    
    def set_baseline(self, function_name: str) -> bool:
        """
        Set current profile as baseline for function.
        
        Args:
            function_name: Function name
            
        Returns:
            True if baseline set successfully
        """
        # Get most recent profile for this function
        for profile in reversed(self.profiles):
            if profile.function_name == function_name:
                self.baseline_profiles[function_name] = profile
                return True
        return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary.
        
        Returns:
            Performance summary
        """
        if not self.profiles:
            return {
                "total_profiles": 0,
                "message": "No profiles available"
            }
        
        total_profiles = len(self.profiles)
        avg_execution_time = sum(p.execution_time_ms for p in self.profiles) / total_profiles
        avg_memory = sum(p.memory_used_mb for p in self.profiles) / total_profiles
        
        # Find slowest functions
        slowest = sorted(self.profiles, key=lambda p: p.execution_time_ms, reverse=True)[:5]
        
        # Find memory-intensive functions
        memory_intensive = sorted(self.profiles, key=lambda p: p.memory_used_mb, reverse=True)[:5]
        
        # Count issues
        slow_count = sum(1 for p in self.profiles if p.execution_time_ms > self.slow_threshold_ms)
        memory_count = sum(1 for p in self.profiles if p.memory_used_mb > self.memory_threshold_mb)
        
        return {
            "total_profiles": total_profiles,
            "avg_execution_time_ms": avg_execution_time,
            "avg_memory_mb": avg_memory,
            "slow_functions_count": slow_count,
            "high_memory_functions_count": memory_count,
            "slowest_functions": [
                {
                    "name": p.function_name,
                    "time_ms": p.execution_time_ms
                }
                for p in slowest
            ],
            "memory_intensive_functions": [
                {
                    "name": p.function_name,
                    "memory_mb": p.memory_used_mb
                }
                for p in memory_intensive
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_regressions(self, threshold_percent: float = 10.0) -> List[Dict[str, Any]]:
        """
        Detect performance regressions compared to baselines.
        
        Args:
            threshold_percent: Threshold for regression detection (default 10%)
            
        Returns:
            List of detected regressions
        """
        regressions = []
        
        for func_name, baseline in self.baseline_profiles.items():
            comparison = self.compare_with_baseline(func_name)
            
            if comparison.get("regression_detected"):
                regressions.append({
                    "function": func_name,
                    "baseline_time_ms": comparison["baseline_time_ms"],
                    "current_time_ms": comparison["current_time_ms"],
                    "degradation_percent": comparison["time_change_percent"],
                    "severity": "critical" if comparison["time_change_percent"] > 50 else "high"
                })
        
        return regressions
    
    def optimize_function(self, function_name: str) -> Dict[str, Any]:
        """
        Get optimization strategies for a function.
        
        Args:
            function_name: Name of function to optimize
            
        Returns:
            Optimization strategies
        """
        # Get most recent profile
        profile = None
        for p in reversed(self.profiles):
            if p.function_name == function_name:
                profile = p
                break
        
        if not profile:
            return {
                "error": "No profile found for function",
                "function": function_name
            }
        
        strategies = []
        
        # Time optimization strategies
        if profile.execution_time_ms > self.slow_threshold_ms:
            strategies.append({
                "category": "performance",
                "strategy": "Algorithm Optimization",
                "description": "Review algorithm complexity and optimize hot paths",
                "priority": "high",
                "potential_improvement": "50-80%"
            })
            
            strategies.append({
                "category": "performance",
                "strategy": "Caching",
                "description": "Implement caching for frequently accessed data",
                "priority": "high",
                "potential_improvement": "60-90%"
            })
            
            strategies.append({
                "category": "performance",
                "strategy": "Parallel Processing",
                "description": "Use multiprocessing or async/await for I/O operations",
                "priority": "medium",
                "potential_improvement": "30-70%"
            })
        
        # Memory optimization strategies
        if profile.memory_used_mb > self.memory_threshold_mb:
            strategies.append({
                "category": "memory",
                "strategy": "Use Generators",
                "description": "Convert list operations to generators for streaming",
                "priority": "high",
                "potential_improvement": "50-90%"
            })
            
            strategies.append({
                "category": "memory",
                "strategy": "Batch Processing",
                "description": "Process data in smaller chunks",
                "priority": "medium",
                "potential_improvement": "40-60%"
            })
            
            strategies.append({
                "category": "memory",
                "strategy": "Object Pooling",
                "description": "Reuse objects instead of creating new ones",
                "priority": "low",
                "potential_improvement": "20-40%"
            })
        
        if not strategies:
            strategies.append({
                "category": "general",
                "strategy": "Maintain Current Performance",
                "description": "Performance is within acceptable ranges",
                "priority": "low",
                "potential_improvement": "0-10%"
            })
        
        return {
            "function": function_name,
            "current_performance": {
                "execution_time_ms": profile.execution_time_ms,
                "memory_mb": profile.memory_used_mb
            },
            "optimization_strategies": strategies,
            "recommendations": profile.recommendations
        }
