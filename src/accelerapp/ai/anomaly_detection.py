"""
Anomaly Detection System for Predictive Maintenance.
Uses ML techniques to detect hardware anomalies and predict failures.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import deque, defaultdict
import math


@dataclass
class AnomalyEvent:
    """Represents an anomaly detection event."""
    
    timestamp: str
    device_id: str
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    metadata: Dict[str, Any]


class AnomalyDetector:
    """
    Detects anomalies in hardware metrics using statistical methods.
    Implements online learning for adaptive thresholds.
    """
    
    def __init__(self, storage_path: Optional[Path] = None, window_size: int = 100):
        """
        Initialize anomaly detector.
        
        Args:
            storage_path: Path to store anomaly data
            window_size: Number of samples for rolling statistics
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "anomaly_detection"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.window_size = window_size
        
        # Store recent values for each metric
        self.metric_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
        # Store baseline statistics
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Store detected anomalies
        self.anomalies: List[AnomalyEvent] = []
        
        self._load_baselines()
        self._load_anomalies()
    
    def _load_baselines(self) -> None:
        """Load baseline statistics from storage."""
        baseline_file = self.storage_path / "baselines.json"
        if baseline_file.exists():
            try:
                with open(baseline_file, "r") as f:
                    self.baselines = json.load(f)
            except Exception:
                self.baselines = {}
    
    def _save_baselines(self) -> None:
        """Save baseline statistics to storage."""
        baseline_file = self.storage_path / "baselines.json"
        with open(baseline_file, "w") as f:
            json.dump(self.baselines, f, indent=2)
    
    def _load_anomalies(self) -> None:
        """Load anomaly history from storage."""
        anomaly_file = self.storage_path / "anomalies.json"
        if anomaly_file.exists():
            try:
                with open(anomaly_file, "r") as f:
                    data = json.load(f)
                    self.anomalies = [AnomalyEvent(**a) for a in data]
            except Exception:
                self.anomalies = []
    
    def _save_anomalies(self) -> None:
        """Save anomaly history to storage."""
        anomaly_file = self.storage_path / "anomalies.json"
        with open(anomaly_file, "w") as f:
            json.dump([asdict(a) for a in self.anomalies], f, indent=2)
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate mean and standard deviation."""
        if not values:
            return {"mean": 0.0, "std": 0.0}
        
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        std = math.sqrt(variance)
        
        return {"mean": mean, "std": std}
    
    def update_baseline(self, device_id: str, metric_name: str, value: float) -> None:
        """
        Update baseline statistics with new measurement.
        
        Args:
            device_id: Device identifier
            metric_name: Metric name
            value: Measured value
        """
        key = f"{device_id}:{metric_name}"
        self.metric_windows[key].append(value)
        
        # Update baseline if we have enough samples
        min_samples = min(20, self.window_size // 2)
        if len(self.metric_windows[key]) >= min_samples:
            stats = self._calculate_statistics(list(self.metric_windows[key]))
            # Ensure minimum standard deviation to avoid false positives
            if stats["std"] < 0.1:
                stats["std"] = 0.1
            self.baselines[key] = stats
            self._save_baselines()
    
    def detect_anomaly(
        self,
        device_id: str,
        metric_name: str,
        value: float,
        threshold_factor: float = 3.0
    ) -> Optional[AnomalyEvent]:
        """
        Detect if a value is anomalous using statistical methods.
        
        Args:
            device_id: Device identifier
            metric_name: Metric name
            value: Measured value
            threshold_factor: Number of standard deviations for threshold
        
        Returns:
            AnomalyEvent if anomaly detected, None otherwise
        """
        key = f"{device_id}:{metric_name}"
        
        # Get baseline statistics
        baseline = self.baselines.get(key)
        if not baseline:
            # No baseline yet, just update and return
            self.update_baseline(device_id, metric_name, value)
            return None
        
        mean = baseline["mean"]
        std = baseline["std"]
        
        # Ensure minimum standard deviation to avoid false positives
        if std < 0.1:
            std = 0.1
        
        # Calculate z-score
        z_score = abs((value - mean) / std)
        
        # Determine if anomalous
        if z_score > threshold_factor:
            # Calculate expected range
            lower_bound = mean - threshold_factor * std
            upper_bound = mean + threshold_factor * std
            
            # Determine severity based on z-score
            if z_score > 5.0:
                severity = "critical"
            elif z_score > 4.0:
                severity = "high"
            elif z_score > 3.5:
                severity = "medium"
            else:
                severity = "low"
            
            # Calculate confidence (0-1)
            confidence = min(1.0, (z_score - threshold_factor) / threshold_factor)
            
            anomaly = AnomalyEvent(
                timestamp=datetime.now().isoformat(),
                device_id=device_id,
                metric_name=metric_name,
                value=value,
                expected_range=(lower_bound, upper_bound),
                severity=severity,
                confidence=confidence,
                metadata={
                    "z_score": z_score,
                    "mean": mean,
                    "std": std
                }
            )
            
            self.anomalies.append(anomaly)
            self._save_anomalies()
            
            return anomaly
        
        # Update baseline with normal value
        self.update_baseline(device_id, metric_name, value)
        return None
    
    def get_anomalies(
        self,
        device_id: Optional[str] = None,
        severity: Optional[str] = None,
        time_window: Optional[int] = None
    ) -> List[AnomalyEvent]:
        """
        Get detected anomalies with optional filtering.
        
        Args:
            device_id: Filter by device ID
            severity: Filter by severity
            time_window: Only return anomalies from last N hours
        
        Returns:
            List of anomaly events
        """
        filtered = self.anomalies
        
        if device_id:
            filtered = [a for a in filtered if a.device_id == device_id]
        
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        if time_window:
            cutoff = datetime.now() - timedelta(hours=time_window)
            filtered = [
                a for a in filtered 
                if datetime.fromisoformat(a.timestamp) > cutoff
            ]
        
        return filtered
    
    def predict_failure(
        self,
        device_id: str,
        lookback_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Predict potential hardware failure based on anomaly patterns.
        
        Args:
            device_id: Device identifier
            lookback_hours: Hours to look back for pattern analysis
        
        Returns:
            Failure prediction with risk level and recommendations
        """
        recent_anomalies = self.get_anomalies(
            device_id=device_id,
            time_window=lookback_hours
        )
        
        if not recent_anomalies:
            return {
                "risk_level": "low",
                "failure_probability": 0.0,
                "confidence": 1.0,
                "recommendations": ["System operating normally"],
                "anomaly_count": 0
            }
        
        # Calculate risk metrics
        critical_count = sum(1 for a in recent_anomalies if a.severity == "critical")
        high_count = sum(1 for a in recent_anomalies if a.severity == "high")
        total_count = len(recent_anomalies)
        
        # Calculate failure probability (simplified model)
        failure_prob = min(1.0, (critical_count * 0.3 + high_count * 0.15 + total_count * 0.05))
        
        # Determine risk level
        if failure_prob > 0.7:
            risk_level = "critical"
            recommendations = [
                "Immediate maintenance required",
                "Consider device replacement",
                "Schedule emergency inspection"
            ]
        elif failure_prob > 0.5:
            risk_level = "high"
            recommendations = [
                "Schedule maintenance within 24 hours",
                "Monitor closely",
                "Prepare backup device"
            ]
        elif failure_prob > 0.3:
            risk_level = "medium"
            recommendations = [
                "Schedule maintenance within 1 week",
                "Continue monitoring",
                "Review recent anomalies"
            ]
        else:
            risk_level = "low"
            recommendations = [
                "Continue normal operation",
                "Monitor for pattern changes"
            ]
        
        # Group anomalies by metric
        metrics_affected = defaultdict(int)
        for anomaly in recent_anomalies:
            metrics_affected[anomaly.metric_name] += 1
        
        return {
            "risk_level": risk_level,
            "failure_probability": failure_prob,
            "confidence": 0.8,  # Model confidence
            "recommendations": recommendations,
            "anomaly_count": total_count,
            "critical_anomalies": critical_count,
            "high_anomalies": high_count,
            "metrics_affected": dict(metrics_affected),
            "most_affected_metric": max(metrics_affected.items(), key=lambda x: x[1])[0] if metrics_affected else None
        }
    
    def clear_old_anomalies(self, days: int = 30) -> int:
        """
        Clear anomalies older than specified days.
        
        Args:
            days: Keep anomalies from last N days
        
        Returns:
            Number of anomalies cleared
        """
        cutoff = datetime.now() - timedelta(days=days)
        before_count = len(self.anomalies)
        
        self.anomalies = [
            a for a in self.anomalies
            if datetime.fromisoformat(a.timestamp) > cutoff
        ]
        
        self._save_anomalies()
        return before_count - len(self.anomalies)
    
    def get_device_health_score(self, device_id: str) -> float:
        """
        Calculate overall health score for a device (0-100).
        
        Args:
            device_id: Device identifier
        
        Returns:
            Health score (100 = perfect health, 0 = critical)
        """
        recent_anomalies = self.get_anomalies(device_id=device_id, time_window=24)
        
        if not recent_anomalies:
            return 100.0
        
        # Deduct points based on severity
        deductions = {
            "critical": 30,
            "high": 15,
            "medium": 7,
            "low": 3
        }
        
        score = 100.0
        for anomaly in recent_anomalies:
            score -= deductions.get(anomaly.severity, 5)
        
        return max(0.0, score)
