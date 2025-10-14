"""
Business Intelligence Dashboard.
Provides analytics and reporting capabilities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict


class BIDashboard:
    """
    Business Intelligence dashboard for analytics and reporting.
    Provides insights into system usage and performance.
    """
    
    def __init__(self):
        """Initialize BI dashboard."""
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            dimensions: Optional metric dimensions (tags)
        """
        self.metrics[metric_name].append({
            "timestamp": datetime.utcnow().isoformat(),
            "value": value,
            "dimensions": dimensions or {}
        })
    
    def get_metric_summary(
        self,
        metric_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            Dictionary with metric summary
        """
        data_points = self.metrics.get(metric_name, [])
        
        # Filter by time range
        if start_time:
            data_points = [
                p for p in data_points
                if p["timestamp"] >= start_time
            ]
        
        if end_time:
            data_points = [
                p for p in data_points
                if p["timestamp"] <= end_time
            ]
        
        if not data_points:
            return {
                "metric": metric_name,
                "count": 0,
                "summary": {}
            }
        
        values = [p["value"] for p in data_points]
        
        return {
            "metric": metric_name,
            "count": len(values),
            "summary": {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "total": sum(values)
            }
        }
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """
        Get overview of all metrics.
        
        Returns:
            Dictionary with dashboard overview
        """
        overview = {
            "total_metrics": len(self.metrics),
            "metrics": []
        }
        
        for metric_name in self.metrics:
            summary = self.get_metric_summary(metric_name)
            overview["metrics"].append(summary)
        
        return overview
    
    def get_time_series(
        self,
        metric_name: str,
        interval_minutes: int = 60,
        limit: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a metric.
        
        Args:
            metric_name: Name of the metric
            interval_minutes: Time interval in minutes
            limit: Maximum number of data points
            
        Returns:
            List of time series data points
        """
        data_points = self.metrics.get(metric_name, [])
        
        if not data_points:
            return []
        
        # Group by time interval
        time_buckets = defaultdict(list)
        
        for point in data_points:
            timestamp = datetime.fromisoformat(point["timestamp"])
            bucket = timestamp.replace(
                minute=(timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0
            )
            time_buckets[bucket.isoformat()].append(point["value"])
        
        # Calculate averages for each bucket
        time_series = []
        for bucket_time in sorted(time_buckets.keys(), reverse=True)[:limit]:
            values = time_buckets[bucket_time]
            time_series.append({
                "timestamp": bucket_time,
                "value": sum(values) / len(values),
                "count": len(values)
            })
        
        return list(reversed(time_series))
    
    def compare_metrics(
        self,
        metric_names: List[str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple metrics.
        
        Args:
            metric_names: List of metric names to compare
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "metrics": [],
            "comparison_period": {
                "start": start_time,
                "end": end_time
            }
        }
        
        for metric_name in metric_names:
            summary = self.get_metric_summary(metric_name, start_time, end_time)
            comparison["metrics"].append(summary)
        
        return comparison
