"""
Cost monitoring and optimization system for cloud and infrastructure resources.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ResourceType(str, Enum):
    """Types of resources to monitor."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"


@dataclass
class ResourceUsage:
    """Represents resource usage data."""
    
    resource_id: str
    resource_type: ResourceType
    provider: CloudProvider
    usage_hours: float
    cost_per_hour: float
    total_cost: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost based on usage."""
        return self.usage_hours * self.cost_per_hour


@dataclass
class CostReport:
    """Cost analysis report."""
    
    report_id: str
    start_date: str
    end_date: str
    total_cost: float
    cost_by_resource_type: Dict[str, float]
    cost_by_provider: Dict[str, float]
    top_cost_resources: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]
    estimated_savings: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class CostMonitor:
    """
    Monitor and optimize infrastructure and cloud costs.
    """
    
    def __init__(self):
        """Initialize cost monitor."""
        self.resources: Dict[str, ResourceUsage] = {}
        self.cost_history: List[ResourceUsage] = []
        self.reports: List[CostReport] = []
        
        # Cost optimization thresholds
        self.utilization_threshold = 0.3  # 30% minimum utilization
        self.idle_threshold_hours = 24  # Hours before considering idle
        
        # Pricing data (simplified - in production would come from cloud APIs)
        self.base_pricing = {
            (CloudProvider.AWS, ResourceType.COMPUTE): 0.10,
            (CloudProvider.AWS, ResourceType.STORAGE): 0.023,
            (CloudProvider.AWS, ResourceType.DATABASE): 0.15,
            (CloudProvider.AZURE, ResourceType.COMPUTE): 0.096,
            (CloudProvider.AZURE, ResourceType.STORAGE): 0.020,
            (CloudProvider.GCP, ResourceType.COMPUTE): 0.095,
            (CloudProvider.ON_PREMISE, ResourceType.COMPUTE): 0.05,
        }
    
    def track_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        provider: CloudProvider,
        usage_hours: float,
        cost_per_hour: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResourceUsage:
        """
        Track resource usage and cost.
        
        Args:
            resource_id: Unique resource identifier
            resource_type: Type of resource
            provider: Cloud provider
            usage_hours: Hours of usage
            cost_per_hour: Cost per hour (optional, will use default if not provided)
            metadata: Additional resource metadata
            
        Returns:
            ResourceUsage object
        """
        if cost_per_hour is None:
            cost_per_hour = self.base_pricing.get((provider, resource_type), 0.10)
        
        total_cost = usage_hours * cost_per_hour
        
        usage = ResourceUsage(
            resource_id=resource_id,
            resource_type=resource_type,
            provider=provider,
            usage_hours=usage_hours,
            cost_per_hour=cost_per_hour,
            total_cost=total_cost,
            metadata=metadata or {}
        )
        
        self.resources[resource_id] = usage
        self.cost_history.append(usage)
        
        return usage
    
    def get_resource_cost(self, resource_id: str) -> Optional[float]:
        """
        Get current cost for a specific resource.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Total cost or None if resource not found
        """
        resource = self.resources.get(resource_id)
        return resource.total_cost if resource else None
    
    def get_total_cost(
        self,
        provider: Optional[CloudProvider] = None,
        resource_type: Optional[ResourceType] = None
    ) -> float:
        """
        Get total cost with optional filters.
        
        Args:
            provider: Filter by cloud provider
            resource_type: Filter by resource type
            
        Returns:
            Total cost
        """
        total = 0.0
        for usage in self.resources.values():
            if provider and usage.provider != provider:
                continue
            if resource_type and usage.resource_type != resource_type:
                continue
            total += usage.total_cost
        return total
    
    def identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify cost optimization opportunities.
        
        Returns:
            List of optimization recommendations
        """
        opportunities = []
        
        for resource_id, usage in self.resources.items():
            # Check for underutilized resources
            utilization = usage.metadata.get("utilization", 1.0)
            if utilization < self.utilization_threshold:
                potential_savings = usage.total_cost * (1 - utilization)
                opportunities.append({
                    "type": "underutilized_resource",
                    "resource_id": resource_id,
                    "resource_type": usage.resource_type.value,
                    "utilization": utilization,
                    "current_cost": usage.total_cost,
                    "potential_savings": potential_savings,
                    "recommendation": f"Consider downsizing or terminating - only {utilization*100:.1f}% utilized",
                    "priority": "high" if utilization < 0.1 else "medium"
                })
            
            # Check for idle resources
            last_active = usage.metadata.get("last_active_hours", 0)
            if last_active > self.idle_threshold_hours:
                opportunities.append({
                    "type": "idle_resource",
                    "resource_id": resource_id,
                    "resource_type": usage.resource_type.value,
                    "idle_hours": last_active,
                    "current_cost": usage.total_cost,
                    "potential_savings": usage.total_cost,
                    "recommendation": f"Resource idle for {last_active} hours - consider terminating",
                    "priority": "high"
                })
            
            # Check for oversized resources
            if usage.resource_type == ResourceType.COMPUTE:
                cpu_usage = usage.metadata.get("cpu_usage", 0)
                memory_usage = usage.metadata.get("memory_usage", 0)
                if cpu_usage < 0.3 and memory_usage < 0.3:
                    potential_savings = usage.total_cost * 0.5  # Estimate 50% savings by downsizing
                    opportunities.append({
                        "type": "oversized_resource",
                        "resource_id": resource_id,
                        "resource_type": usage.resource_type.value,
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory_usage,
                        "current_cost": usage.total_cost,
                        "potential_savings": potential_savings,
                        "recommendation": "Consider using a smaller instance type",
                        "priority": "medium"
                    })
        
        # Check for multi-provider cost disparities
        provider_costs = {}
        for usage in self.resources.values():
            provider_costs[usage.provider] = provider_costs.get(usage.provider, 0) + usage.total_cost
        
        if len(provider_costs) > 1:
            costs_list = sorted(provider_costs.items(), key=lambda x: x[1])
            if len(costs_list) >= 2:
                cheapest = costs_list[0]
                most_expensive = costs_list[-1]
                if most_expensive[1] > cheapest[1] * 1.2:  # 20% more expensive
                    opportunities.append({
                        "type": "provider_optimization",
                        "recommendation": f"Consider migrating from {most_expensive[0].value} to {cheapest[0].value}",
                        "current_provider": most_expensive[0].value,
                        "suggested_provider": cheapest[0].value,
                        "current_cost": most_expensive[1],
                        "potential_cost": cheapest[1],
                        "potential_savings": most_expensive[1] - cheapest[1],
                        "priority": "low"
                    })
        
        return opportunities
    
    def generate_cost_report(
        self,
        report_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> CostReport:
        """
        Generate comprehensive cost report.
        
        Args:
            report_id: Report identifier
            start_date: Start date for report (ISO format)
            end_date: End date for report (ISO format)
            
        Returns:
            CostReport object
        """
        if start_date is None:
            start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if end_date is None:
            end_date = datetime.utcnow().isoformat()
        
        # Calculate costs by resource type
        cost_by_type = {}
        for usage in self.resources.values():
            rt = usage.resource_type.value
            cost_by_type[rt] = cost_by_type.get(rt, 0) + usage.total_cost
        
        # Calculate costs by provider
        cost_by_provider = {}
        for usage in self.resources.values():
            prov = usage.provider.value
            cost_by_provider[prov] = cost_by_provider.get(prov, 0) + usage.total_cost
        
        # Get top cost resources
        top_resources = sorted(
            [
                {
                    "resource_id": rid,
                    "resource_type": usage.resource_type.value,
                    "provider": usage.provider.value,
                    "cost": usage.total_cost
                }
                for rid, usage in self.resources.items()
            ],
            key=lambda x: x["cost"],
            reverse=True
        )[:10]
        
        # Get optimization opportunities
        opportunities = self.identify_optimization_opportunities()
        
        # Calculate estimated savings
        estimated_savings = sum(opp.get("potential_savings", 0) for opp in opportunities)
        
        total_cost = sum(usage.total_cost for usage in self.resources.values())
        
        report = CostReport(
            report_id=report_id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
            cost_by_resource_type=cost_by_type,
            cost_by_provider=cost_by_provider,
            top_cost_resources=top_resources,
            optimization_opportunities=opportunities,
            estimated_savings=estimated_savings
        )
        
        self.reports.append(report)
        return report
    
    def get_cost_forecast(self, days: int = 30) -> Dict[str, Any]:
        """
        Forecast costs for the next N days based on current usage.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Forecast data
        """
        current_daily_cost = self.get_total_cost() / 30  # Assume 30-day average
        forecasted_cost = current_daily_cost * days
        
        # Add some variance based on historical patterns
        variance = 0.1  # 10% variance
        
        return {
            "forecast_days": days,
            "current_daily_cost": current_daily_cost,
            "forecasted_cost": forecasted_cost,
            "forecasted_cost_min": forecasted_cost * (1 - variance),
            "forecasted_cost_max": forecasted_cost * (1 + variance),
            "confidence": 0.85,  # 85% confidence
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed cost breakdown.
        
        Returns:
            Cost breakdown data
        """
        return {
            "total_cost": self.get_total_cost(),
            "by_provider": {
                provider.value: self.get_total_cost(provider=provider)
                for provider in CloudProvider
            },
            "by_resource_type": {
                rt.value: self.get_total_cost(resource_type=rt)
                for rt in ResourceType
            },
            "resource_count": len(self.resources),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def apply_cost_optimization(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a cost optimization recommendation.
        
        Args:
            opportunity: Optimization opportunity to apply
            
        Returns:
            Result of optimization
        """
        result = {
            "applied": False,
            "opportunity_type": opportunity.get("type"),
            "resource_id": opportunity.get("resource_id"),
            "message": ""
        }
        
        resource_id = opportunity.get("resource_id")
        if not resource_id or resource_id not in self.resources:
            result["message"] = "Resource not found or not specified"
            return result
        
        opp_type = opportunity.get("type")
        
        if opp_type == "underutilized_resource":
            # Simulate downsizing
            resource = self.resources[resource_id]
            resource.cost_per_hour *= 0.5  # 50% cost reduction
            resource.total_cost = resource.usage_hours * resource.cost_per_hour
            result["applied"] = True
            result["message"] = "Resource downsized successfully"
            result["new_cost"] = resource.total_cost
            
        elif opp_type == "idle_resource":
            # Simulate termination
            resource = self.resources.pop(resource_id)
            result["applied"] = True
            result["message"] = "Idle resource terminated"
            result["savings"] = resource.total_cost
            
        elif opp_type == "oversized_resource":
            # Simulate right-sizing
            resource = self.resources[resource_id]
            resource.cost_per_hour *= 0.5  # 50% cost reduction
            resource.total_cost = resource.usage_hours * resource.cost_per_hour
            result["applied"] = True
            result["message"] = "Resource right-sized successfully"
            result["new_cost"] = resource.total_cost
        else:
            result["message"] = f"Optimization type '{opp_type}' not supported for automatic application"
        
        return result
