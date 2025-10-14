"""
Model Performance Analytics System.
Tracks and analyzes AI agent effectiveness and performance metrics.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict


@dataclass
class PerformanceMetric:
    """Represents a performance metric measurement."""
    
    timestamp: str
    agent_name: str
    task_type: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]


class ModelPerformanceAnalyzer:
    """
    Analyzes AI model and agent performance.
    Tracks metrics over time and provides insights.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize performance analyzer.
        
        Args:
            storage_path: Path to store performance data
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "performance"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self._load_metrics()
    
    def _load_metrics(self) -> None:
        """Load performance metrics from storage."""
        metrics_file = self.storage_path / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    for agent_name, measurements in data.items():
                        self.metrics[agent_name] = [
                            PerformanceMetric(**m) for m in measurements
                        ]
            except Exception:
                self.metrics = defaultdict(list)
    
    def _save_metrics(self) -> None:
        """Save performance metrics to storage."""
        metrics_file = self.storage_path / "metrics.json"
        data = {
            agent_name: [asdict(m) for m in measurements]
            for agent_name, measurements in self.metrics.items()
        }
        with open(metrics_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_performance(
        self,
        agent_name: str,
        task_type: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record performance metrics for an agent.
        
        Args:
            agent_name: Name of the agent
            task_type: Type of task performed
            metrics: Performance metrics (e.g., latency, accuracy, throughput)
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            task_type=task_type,
            metrics=metrics,
            metadata=metadata or {}
        )
        
        self.metrics[agent_name].append(metric)
        self._save_metrics()
    
    def get_agent_performance(
        self,
        agent_name: str,
        task_type: Optional[str] = None,
        time_window: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get performance statistics for an agent.
        
        Args:
            agent_name: Name of the agent
            task_type: Optional task type filter
            time_window: Optional time window in hours
            
        Returns:
            Dictionary with performance statistics
        """
        measurements = self.metrics.get(agent_name, [])
        
        # Filter by task type
        if task_type:
            measurements = [m for m in measurements if m.task_type == task_type]
        
        # Filter by time window
        if time_window:
            cutoff = datetime.utcnow() - timedelta(hours=time_window)
            measurements = [
                m for m in measurements
                if datetime.fromisoformat(m.timestamp) > cutoff
            ]
        
        if not measurements:
            return {
                "agent_name": agent_name,
                "task_type": task_type,
                "total_measurements": 0,
                "metrics": {}
            }
        
        # Aggregate metrics
        all_metric_names = set()
        for m in measurements:
            all_metric_names.update(m.metrics.keys())
        
        aggregated = {}
        for metric_name in all_metric_names:
            values = [
                m.metrics[metric_name]
                for m in measurements
                if metric_name in m.metrics
            ]
            
            if values:
                aggregated[metric_name] = {
                    "count": len(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1]
                }
                
                # Calculate percentiles
                sorted_values = sorted(values)
                n = len(sorted_values)
                aggregated[metric_name]["p50"] = sorted_values[n // 2]
                aggregated[metric_name]["p95"] = sorted_values[int(n * 0.95)]
                aggregated[metric_name]["p99"] = sorted_values[int(n * 0.99)]
        
        return {
            "agent_name": agent_name,
            "task_type": task_type,
            "total_measurements": len(measurements),
            "time_range": {
                "start": measurements[0].timestamp if measurements else None,
                "end": measurements[-1].timestamp if measurements else None
            },
            "metrics": aggregated
        }
    
    def compare_agents(
        self,
        agent_names: List[str],
        metric_name: str,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple agents.
        
        Args:
            agent_names: List of agent names to compare
            metric_name: Metric to compare
            task_type: Optional task type filter
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "metric": metric_name,
            "task_type": task_type,
            "agents": []
        }
        
        for agent_name in agent_names:
            stats = self.get_agent_performance(agent_name, task_type)
            
            if metric_name in stats["metrics"]:
                metric_data = stats["metrics"][metric_name]
                comparison["agents"].append({
                    "name": agent_name,
                    "mean": metric_data["mean"],
                    "p95": metric_data["p95"],
                    "count": metric_data["count"]
                })
        
        # Rank agents by mean performance
        if comparison["agents"]:
            comparison["agents"].sort(key=lambda x: x["mean"])
            comparison["best_agent"] = comparison["agents"][0]["name"]
            comparison["worst_agent"] = comparison["agents"][-1]["name"]
        
        return comparison
    
    def get_trend(
        self,
        agent_name: str,
        metric_name: str,
        task_type: Optional[str] = None,
        time_window: int = 24
    ) -> Dict[str, Any]:
        """
        Get performance trend over time.
        
        Args:
            agent_name: Name of the agent
            metric_name: Metric to analyze
            task_type: Optional task type filter
            time_window: Time window in hours
            
        Returns:
            Dictionary with trend analysis
        """
        measurements = self.metrics.get(agent_name, [])
        
        # Filter by task type
        if task_type:
            measurements = [m for m in measurements if m.task_type == task_type]
        
        # Filter by time window
        cutoff = datetime.utcnow() - timedelta(hours=time_window)
        measurements = [
            m for m in measurements
            if datetime.fromisoformat(m.timestamp) > cutoff
            and metric_name in m.metrics
        ]
        
        if not measurements:
            return {
                "agent_name": agent_name,
                "metric": metric_name,
                "trend": "no_data"
            }
        
        # Extract values with timestamps
        data_points = [
            {
                "timestamp": m.timestamp,
                "value": m.metrics[metric_name]
            }
            for m in measurements
        ]
        
        # Calculate simple trend (linear regression approximation)
        values = [p["value"] for p in data_points]
        n = len(values)
        
        if n < 2:
            trend = "stable"
        else:
            # Simple slope calculation
            x = list(range(n))
            mean_x = sum(x) / n
            mean_y = sum(values) / n
            
            numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
            denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
            
            if denominator > 0:
                slope = numerator / denominator
                
                # Determine trend based on slope
                if slope > 0.01:
                    trend = "improving" if metric_name in ["accuracy", "success_rate"] else "degrading"
                elif slope < -0.01:
                    trend = "degrading" if metric_name in ["accuracy", "success_rate"] else "improving"
                else:
                    trend = "stable"
            else:
                trend = "stable"
        
        return {
            "agent_name": agent_name,
            "metric": metric_name,
            "task_type": task_type,
            "time_window_hours": time_window,
            "data_points": len(data_points),
            "trend": trend,
            "values": {
                "first": values[0],
                "last": values[-1],
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
        }
    
    def get_all_agents(self) -> List[str]:
        """
        Get list of all agents with recorded metrics.
        
        Returns:
            List of agent names
        """
        return list(self.metrics.keys())
    
    def clear_old_metrics(self, days: int = 30) -> int:
        """
        Clear metrics older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of metrics removed
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        removed = 0
        
        for agent_name in self.metrics:
            original_count = len(self.metrics[agent_name])
            self.metrics[agent_name] = [
                m for m in self.metrics[agent_name]
                if datetime.fromisoformat(m.timestamp) > cutoff
            ]
            removed += original_count - len(self.metrics[agent_name])
        
        self._save_metrics()
        return removed
