# Cost Optimization Guide

**Version**: 1.0.0  
**Last Updated**: 2025-10-14

This guide provides comprehensive strategies for optimizing infrastructure and operational costs for Accelerapp deployments.

---

## Table of Contents

1. [Cost Overview](#cost-overview)
2. [Cost Monitoring](#cost-monitoring)
3. [Cloud Provider Optimization](#cloud-provider-optimization)
4. [Resource Right-Sizing](#resource-right-sizing)
5. [Auto-Scaling Strategies](#auto-scaling-strategies)
6. [Storage Optimization](#storage-optimization)
7. [Network Cost Optimization](#network-cost-optimization)
8. [Development and Testing Costs](#development-and-testing-costs)

---

## Cost Overview

### Cost Categories

Typical cost breakdown for Accelerapp deployment:

| Category | Percentage | Monthly (Example) |
|----------|-----------|-------------------|
| Compute | 40-50% | $800-$1000 |
| Database | 20-25% | $400-$500 |
| Storage | 10-15% | $200-$300 |
| Network | 10-15% | $200-$300 |
| Monitoring | 5-10% | $100-$200 |
| **Total** | **100%** | **$2000** |

### Cost Monitoring Setup

Use the built-in cost monitoring system:

```python
from accelerapp.production.optimization import CostMonitor
from accelerapp.production.optimization.cost_monitor import ResourceType, CloudProvider

# Initialize cost monitor
monitor = CostMonitor()

# Track all resources
monitor.track_resource(
    resource_id="app-server-prod",
    resource_type=ResourceType.COMPUTE,
    provider=CloudProvider.AWS,
    usage_hours=720.0,  # Monthly
    cost_per_hour=0.096,
    metadata={
        "instance_type": "t3.medium",
        "region": "us-east-1",
        "utilization": 0.65
    }
)

# Generate monthly cost report
report = monitor.generate_cost_report("monthly-2025-10")
print(f"Total monthly cost: ${report.total_cost:.2f}")
print(f"Potential savings: ${report.estimated_savings:.2f}")
```

---

## Cost Monitoring

### Real-Time Cost Tracking

Track costs in real-time to identify issues early:

```python
def track_all_resources():
    """Track all infrastructure resources."""
    monitor = CostMonitor()
    
    # Application servers
    for i, server in enumerate(get_app_servers()):
        monitor.track_resource(
            resource_id=f"app-server-{i}",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            usage_hours=get_usage_hours(server),
            metadata={
                "utilization": server.get_utilization(),
                "instance_type": server.instance_type
            }
        )
    
    # Databases
    for db in get_databases():
        monitor.track_resource(
            resource_id=db.id,
            resource_type=ResourceType.DATABASE,
            provider=CloudProvider.AWS,
            usage_hours=get_usage_hours(db),
            metadata={
                "size": db.storage_gb,
                "iops": db.iops
            }
        )
    
    # Storage
    for bucket in get_storage():
        monitor.track_resource(
            resource_id=bucket.id,
            resource_type=ResourceType.STORAGE,
            provider=CloudProvider.AWS,
            usage_hours=720.0,
            metadata={
                "size_gb": bucket.size_gb,
                "requests": bucket.requests
            }
        )
    
    return monitor
```

### Cost Alerts

Set up alerts for cost anomalies:

```python
def check_cost_alerts(monitor):
    """Check for cost anomalies and send alerts."""
    # Get current month cost
    current_cost = monitor.get_total_cost()
    
    # Get forecast
    forecast = monitor.get_cost_forecast(days=30)
    
    # Alert if projected to exceed budget
    monthly_budget = 2000.0  # $2000/month budget
    if forecast["forecasted_cost"] > monthly_budget:
        send_alert(
            f"Cost Alert: Projected monthly cost ${forecast['forecasted_cost']:.2f} "
            f"exceeds budget of ${monthly_budget:.2f}"
        )
    
    # Alert on sudden spikes
    breakdown = monitor.get_cost_breakdown()
    for resource_type, cost in breakdown["by_resource_type"].items():
        if cost > monthly_budget * 0.5:  # Single resource > 50% of budget
            send_alert(
                f"Cost Spike Alert: {resource_type} costs ${cost:.2f} "
                f"(>{monthly_budget * 0.5:.2f})"
            )
```

### Cost Reports

Generate detailed cost reports:

```python
def generate_monthly_cost_report(month):
    """Generate comprehensive monthly cost report."""
    monitor = track_all_resources()
    
    report = monitor.generate_cost_report(f"monthly-{month}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Monthly Cost Report - {month}")
    print(f"{'='*60}\n")
    
    print(f"Total Cost: ${report.total_cost:.2f}")
    print(f"\nCost by Resource Type:")
    for rtype, cost in report.cost_by_resource_type.items():
        pct = (cost / report.total_cost) * 100
        print(f"  {rtype:15s}: ${cost:8.2f} ({pct:5.1f}%)")
    
    print(f"\nCost by Provider:")
    for provider, cost in report.cost_by_provider.items():
        print(f"  {provider:15s}: ${cost:8.2f}")
    
    print(f"\nTop Cost Resources:")
    for i, resource in enumerate(report.top_cost_resources[:5], 1):
        print(f"  {i}. {resource['resource_id']:20s}: ${resource['cost']:8.2f}")
    
    print(f"\nOptimization Opportunities: {len(report.optimization_opportunities)}")
    print(f"Potential Savings: ${report.estimated_savings:.2f}")
    print(f"{'='*60}\n")
    
    return report
```

---

## Cloud Provider Optimization

### AWS Cost Optimization

#### 1. Use Reserved Instances

For predictable workloads:

```python
# Calculate savings with Reserved Instances
on_demand_cost = 0.096 * 720  # t3.medium, 1 month
reserved_cost = 0.062 * 720   # 1-year reserved
savings = on_demand_cost - reserved_cost
savings_percent = (savings / on_demand_cost) * 100

print(f"Monthly savings: ${savings:.2f} ({savings_percent:.1f}%)")
# Output: Monthly savings: $24.48 (35.4%)
```

Recommendations:
- **1-year term**: 35-40% savings
- **3-year term**: 50-60% savings
- **Best for**: Production servers, databases

#### 2. Use Spot Instances

For fault-tolerant workloads:

```python
# Compare spot vs on-demand
on_demand_cost = 0.096 * 720  # t3.medium
spot_cost = 0.029 * 720       # Average spot price
savings = on_demand_cost - spot_cost
savings_percent = (savings / on_demand_cost) * 100

print(f"Monthly savings: ${savings:.2f} ({savings_percent:.1f}%)")
# Output: Monthly savings: $48.24 (69.8%)
```

Recommendations:
- **Savings**: 60-90%
- **Best for**: Batch processing, CI/CD, development
- **Risk**: Can be interrupted

#### 3. Use Savings Plans

Flexible commitment:

- **Compute Savings Plans**: Up to 66% savings
- **EC2 Instance Savings Plans**: Up to 72% savings
- **Flexibility**: Can change instance types/sizes

### Azure Cost Optimization

#### 1. Azure Hybrid Benefit

Use existing Windows Server licenses:

```python
# Savings with Azure Hybrid Benefit
standard_cost = 0.192 * 720  # Windows Server VM
hybrid_cost = 0.096 * 720    # With hybrid benefit
savings = standard_cost - hybrid_cost

print(f"Monthly savings: ${savings:.2f} (50%)")
```

#### 2. Reserved VM Instances

Similar to AWS Reserved Instances:
- **1-year**: 40-42% savings
- **3-year**: 58-62% savings

### GCP Cost Optimization

#### 1. Committed Use Discounts

Automatic discounts for sustained usage:
- **1-year**: 25-37% savings
- **3-year**: 52-60% savings

#### 2. Sustained Use Discounts

Automatic discounts (no commitment required):
- **25% of month**: 20% discount
- **50% of month**: 30% discount
- **100% of month**: 40% discount

---

## Resource Right-Sizing

### Identify Underutilized Resources

```python
def identify_underutilized_resources(monitor):
    """Find resources that can be downsized."""
    opportunities = monitor.identify_optimization_opportunities()
    
    underutilized = [
        opp for opp in opportunities 
        if opp["type"] == "underutilized_resource"
    ]
    
    total_savings = sum(opp["potential_savings"] for opp in underutilized)
    
    print(f"Found {len(underutilized)} underutilized resources")
    print(f"Potential savings: ${total_savings:.2f}/month\n")
    
    for opp in underutilized:
        print(f"Resource: {opp['resource_id']}")
        print(f"  Utilization: {opp['utilization']*100:.1f}%")
        print(f"  Current cost: ${opp['current_cost']:.2f}")
        print(f"  Potential savings: ${opp['potential_savings']:.2f}")
        print(f"  Recommendation: {opp['recommendation']}\n")
```

### Right-Sizing Strategies

#### 1. CPU Right-Sizing

```python
def recommend_instance_size(cpu_usage, memory_usage, current_instance):
    """Recommend appropriate instance size."""
    if cpu_usage < 0.3 and memory_usage < 0.3:
        return {
            "action": "downsize",
            "recommendation": f"Downsize from {current_instance} to t3.small",
            "savings_percent": 50
        }
    elif cpu_usage > 0.8 or memory_usage > 0.8:
        return {
            "action": "upsize",
            "recommendation": f"Upsize from {current_instance} to t3.large",
            "cost_increase_percent": 100
        }
    else:
        return {
            "action": "maintain",
            "recommendation": "Current size is appropriate"
        }
```

#### 2. Automated Right-Sizing

```python
def auto_rightsize_resources(monitor):
    """Automatically apply right-sizing recommendations."""
    opportunities = monitor.identify_optimization_opportunities()
    
    results = []
    for opp in opportunities:
        if opp["type"] in ["underutilized_resource", "oversized_resource"]:
            if opp.get("priority") == "high":
                # Apply optimization
                result = monitor.apply_cost_optimization(opp)
                results.append({
                    "resource_id": opp["resource_id"],
                    "action": "downsized",
                    "savings": opp["potential_savings"]
                })
    
    total_savings = sum(r["savings"] for r in results)
    print(f"Applied {len(results)} optimizations")
    print(f"Total monthly savings: ${total_savings:.2f}")
    
    return results
```

---

## Auto-Scaling Strategies

### Cost-Effective Auto-Scaling

Configure auto-scaling to balance performance and cost:

```yaml
# Kubernetes HPA with cost optimization
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: accelerapp-cost-optimized
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: accelerapp
  minReplicas: 2              # Maintain HA
  maxReplicas: 8              # Cost control
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75  # Higher threshold = fewer pods
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50              # Scale down by 50% at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60   # Quick scale-up
      policies:
      - type: Percent
        value: 100             # Double capacity when needed
        periodSeconds: 30
```

### Schedule-Based Scaling

Scale based on predictable patterns:

```python
import schedule
import time

def scale_for_business_hours():
    """Scale up during business hours, down after."""
    # Business hours: 8 AM - 6 PM
    current_hour = datetime.now().hour
    
    if 8 <= current_hour < 18:
        # Scale up for business hours
        scale_deployment("accelerapp", replicas=5)
    else:
        # Scale down for off-hours
        scale_deployment("accelerapp", replicas=2)

# Schedule scaling
schedule.every().hour.at(":00").do(scale_for_business_hours)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Storage Optimization

### Object Storage Lifecycle

Implement lifecycle policies to reduce storage costs:

```python
# AWS S3 lifecycle policy
lifecycle_policy = {
    "Rules": [
        {
            "Id": "ArchiveOldData",
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"  # Infrequent Access (cheaper)
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"       # Archive (very cheap)
                }
            ],
            "Expiration": {
                "Days": 365  # Delete after 1 year
            }
        }
    ]
}
```

Cost comparison:

| Storage Class | Cost/GB/Month | Use Case |
|--------------|---------------|----------|
| Standard | $0.023 | Frequently accessed |
| Infrequent Access | $0.0125 | < 1 access/month |
| Glacier | $0.004 | Archival |
| Deep Archive | $0.00099 | Long-term archival |

### Database Storage Optimization

#### 1. Clean Up Old Data

```python
def cleanup_old_data():
    """Remove or archive old data."""
    # Archive data older than 90 days
    old_data = db.query(GeneratedCode)\
        .filter(GeneratedCode.created_at < datetime.now() - timedelta(days=90))\
        .all()
    
    # Export to S3 archive
    for data in old_data:
        export_to_archive(data)
        db.delete(data)
    
    db.commit()
    print(f"Archived {len(old_data)} records")
```

#### 2. Optimize Database Storage

```sql
-- PostgreSQL: Reclaim space
VACUUM FULL;

-- Rebuild indexes
REINDEX DATABASE accelerapp;

-- Analyze tables for query optimization
ANALYZE;
```

---

## Network Cost Optimization

### Reduce Data Transfer Costs

#### 1. Use CDN

Offload static content to CDN:

```python
# Cost comparison
# Direct from server: $0.09/GB
# Via CDN (CloudFront): $0.085/GB (first 10 TB)

monthly_transfer_gb = 1000
direct_cost = monthly_transfer_gb * 0.09
cdn_cost = monthly_transfer_gb * 0.085
savings = direct_cost - cdn_cost

print(f"Monthly savings with CDN: ${savings:.2f}")
# Output: $5.00/month + better performance
```

#### 2. Compression

Enable compression to reduce transfer:

```python
# Example: Response size reduction with compression
original_size_mb = 10.0
compressed_size_mb = 2.5  # gzip compression
compression_ratio = compressed_size_mb / original_size_mb

transfer_cost_per_gb = 0.09
monthly_requests = 100000

original_cost = (original_size_mb / 1024) * monthly_requests * transfer_cost_per_gb
compressed_cost = (compressed_size_mb / 1024) * monthly_requests * transfer_cost_per_gb
savings = original_cost - compressed_cost

print(f"Monthly savings with compression: ${savings:.2f}")
```

#### 3. Regional Optimization

Keep data close to users:

```python
# Data transfer costs (AWS)
same_region = 0.00      # Free within same region
same_az = 0.01          # $0.01/GB between AZs
cross_region = 0.02     # $0.02/GB between regions
internet = 0.09         # $0.09/GB to internet

# Optimize by using regional deployments
```

---

## Development and Testing Costs

### Cost-Effective Dev/Test Environments

#### 1. Use Smaller Instances

```python
# Environment sizing
environments = {
    "production": {
        "instance": "t3.large",
        "cost_per_hour": 0.0832,
        "count": 3
    },
    "staging": {
        "instance": "t3.medium",
        "cost_per_hour": 0.0416,
        "count": 2
    },
    "development": {
        "instance": "t3.small",
        "cost_per_hour": 0.0208,
        "count": 1
    }
}

# Calculate monthly costs
for env, config in environments.items():
    monthly_cost = config["cost_per_hour"] * 720 * config["count"]
    print(f"{env}: ${monthly_cost:.2f}/month")

# Output:
# production: $179.71/month
# staging: $59.90/month
# development: $14.98/month
```

#### 2. Auto-Shutdown Dev Environments

```python
def auto_shutdown_dev_resources():
    """Shut down dev resources outside business hours."""
    current_hour = datetime.now().hour
    is_weekend = datetime.now().weekday() >= 5
    
    if current_hour < 8 or current_hour >= 18 or is_weekend:
        # Stop development instances
        for instance in get_dev_instances():
            stop_instance(instance.id)
            print(f"Stopped {instance.id}")
    
    # Savings: ~70% (running only 10 hours/day, 5 days/week)
```

#### 3. Use Spot Instances for CI/CD

```bash
# CI/CD pipeline with spot instances
# Cost savings: 60-90%

stages:
  - test
  - build
  - deploy

test:
  stage: test
  tags:
    - spot-instance  # Use spot instances for testing
  script:
    - pytest tests/

build:
  stage: build
  tags:
    - spot-instance
  script:
    - docker build -t app:latest .
```

---

## Cost Optimization Checklist

### Immediate Actions (Quick Wins)
- [ ] Enable auto-shutdown for dev/test environments
- [ ] Implement storage lifecycle policies
- [ ] Enable response compression
- [ ] Right-size over-provisioned resources
- [ ] Delete unused resources (old snapshots, unattached volumes)

### Short-Term (1-3 Months)
- [ ] Purchase Reserved Instances for stable workloads
- [ ] Implement auto-scaling policies
- [ ] Set up CDN for static content
- [ ] Optimize database queries and indexes
- [ ] Review and optimize data transfer patterns

### Long-Term (3-12 Months)
- [ ] Migrate appropriate workloads to spot instances
- [ ] Implement multi-region architecture
- [ ] Adopt serverless where appropriate
- [ ] Continuous cost monitoring and optimization
- [ ] Regular cost reviews and adjustments

---

## Cost Optimization Best Practices

### 1. Regular Cost Reviews

```python
def monthly_cost_review():
    """Perform monthly cost review."""
    monitor = track_all_resources()
    
    # Generate report
    report = monitor.generate_cost_report(f"review-{datetime.now().strftime('%Y-%m')}")
    
    # Identify top opportunities
    opportunities = sorted(
        report.optimization_opportunities,
        key=lambda x: x.get("potential_savings", 0),
        reverse=True
    )[:10]
    
    print("Top 10 Cost Optimization Opportunities:")
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp['type']}: ${opp.get('potential_savings', 0):.2f}")
    
    return opportunities
```

### 2. Set Budgets and Alerts

```python
# Configure budget alerts
MONTHLY_BUDGET = 2000.0  # $2000/month

def check_budget_alerts(monitor):
    """Check if spending is on track."""
    current_day = datetime.now().day
    days_in_month = 30
    expected_spend = (current_day / days_in_month) * MONTHLY_BUDGET
    
    actual_spend = monitor.get_total_cost()
    
    if actual_spend > expected_spend * 1.1:  # 10% over budget
        send_alert(f"Budget Alert: Spending ${actual_spend:.2f}, "
                  f"expected ${expected_spend:.2f}")
```

### 3. Tag Resources

Tag all resources for cost attribution:

```python
resource_tags = {
    "Environment": "production",
    "Project": "accelerapp",
    "Team": "platform",
    "CostCenter": "engineering",
    "Owner": "platform-team@company.com"
}
```

---

## Measuring Cost Optimization Success

### Key Metrics

Track these metrics to measure optimization success:

```python
def calculate_optimization_metrics(before_report, after_report):
    """Calculate optimization success metrics."""
    
    metrics = {
        "cost_reduction_dollars": before_report.total_cost - after_report.total_cost,
        "cost_reduction_percent": (
            (before_report.total_cost - after_report.total_cost) /
            before_report.total_cost * 100
        ),
        "savings_realized": before_report.estimated_savings,
        "optimization_opportunities_addressed": (
            len(before_report.optimization_opportunities) -
            len(after_report.optimization_opportunities)
        )
    }
    
    print(f"\nCost Optimization Results:")
    print(f"  Cost Reduction: ${metrics['cost_reduction_dollars']:.2f} "
          f"({metrics['cost_reduction_percent']:.1f}%)")
    print(f"  Savings Realized: ${metrics['savings_realized']:.2f}")
    print(f"  Opportunities Addressed: {metrics['optimization_opportunities_addressed']}")
    
    return metrics
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Next Review**: 2025-11-14
