# Accelerapp Phase 2 Infrastructure Templates

This directory contains CloudFormation templates and deployment scripts for Accelerapp's Phase 2 core services infrastructure.

## Directory Structure

```
aws/
├── README.md                   # This file
├── DEPLOYMENT_GUIDE.md         # Detailed deployment instructions
├── generate_templates.py       # Template generation script
├── database/                   # RDS Aurora templates
│   ├── rds-aurora.yaml
│   └── rds-aurora.json
├── cache/                      # Redis cluster templates
│   ├── redis-cluster.yaml
│   └── redis-cluster.json
├── storage/                    # S3 bucket templates
│   ├── s3-assets.yaml
│   ├── s3-assets.json
│   ├── s3-backups.yaml
│   └── s3-backups.json
├── cdn/                        # CloudFront distribution templates
│   ├── cloudfront.yaml
│   └── cloudfront.json
└── secrets/                    # Secrets Manager templates
    ├── db-credentials.yaml
    ├── db-credentials.json
    ├── api-keys.yaml
    └── api-keys.json
```

## Services Deployed

### 1. RDS Aurora PostgreSQL Database
- Multi-AZ cluster with 2 instances
- Automated backups (7-day retention)
- Encryption at rest using KMS
- Performance Insights enabled
- CloudWatch Logs integration

### 2. ElastiCache Redis Cluster
- Multi-AZ with automatic failover
- 2 cache nodes (primary + replica)
- Encryption in transit and at rest
- Automated snapshots (5-day retention)
- Redis 7.0 with optimized settings

### 3. S3 Buckets
**Assets Bucket:**
- Static assets and content
- Versioning enabled
- CORS configuration for web access
- Lifecycle policy for old versions

**Backups Bucket:**
- Database and application backups
- Glacier transition after 30 days
- 1-year retention policy
- Strong encryption and access controls

### 4. CloudFront CDN
- Global content delivery
- HTTPS-only distribution
- Origin Access Identity for S3
- Compression enabled
- Optimized caching (configurable TTLs)

### 5. AWS Secrets Manager
**Database Credentials:**
- Secure storage for DB credentials
- Automatic rotation (30-day cycle)
- Encrypted with KMS

**API Keys:**
- Application API keys and tokens
- Manual rotation

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install pyyaml

# Configure AWS CLI
aws configure
```

### Generate Templates

```bash
# Generate all CloudFormation templates
python generate_templates.py
```

### Deploy All Services

```bash
# Set your AWS parameters
export VPC_ID="vpc-xxxxx"
export PRIVATE_SUBNETS="subnet-xxxxx,subnet-yyyyy"
export APP_SECURITY_GROUP="sg-xxxxx"
export DB_PASSWORD="YourSecurePassword123!"

# Deploy in order
./deploy-all.sh
```

Or deploy services individually (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)).

## Template Customization

Templates can be customized by modifying the generation script:

```python
from accelerapp.infrastructure import (
    CoreServicesManager,
    RDSAuroraConfig,
    RedisClusterConfig,
    S3BucketConfig,
    CloudFrontConfig,
    SecretsManagerConfig,
)

manager = CoreServicesManager()

# Customize RDS configuration
rds_config = RDSAuroraConfig(
    cluster_name="my-cluster",
    instance_class="db.r6g.xlarge",  # Larger instance
    backup_retention_days=14,         # Longer retention
    # ... other settings
)

template = manager.generate_rds_aurora_template(rds_config)
```

## Validation

Validate templates before deployment:

```bash
# Validate CloudFormation templates
aws cloudformation validate-template \
  --template-body file://database/rds-aurora.yaml

aws cloudformation validate-template \
  --template-body file://cache/redis-cluster.yaml

# ... validate other templates
```

## Cost Estimates

Approximate monthly costs (us-east-1):

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| RDS Aurora | 2 x db.r6g.large | ~$500 |
| ElastiCache | 2 x cache.r6g.large | ~$300 |
| S3 Assets | 100 GB + requests | ~$5 |
| S3 Backups | 500 GB + Glacier | ~$10 |
| CloudFront | 1 TB transfer | ~$85 |
| Secrets Manager | 2 secrets | ~$1 |
| **Total** | | **~$900/month** |

*Costs are estimates and may vary based on usage and region.*

## Testing

Run infrastructure tests:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/test_infrastructure.py -v

# Run with coverage
pytest tests/test_infrastructure.py --cov=accelerapp.infrastructure
```

## Monitoring

After deployment, monitor services via:

1. **AWS CloudWatch Dashboard**
   - Custom dashboard with all service metrics
   - See monitoring/dashboard.json

2. **CloudWatch Alarms**
   - CPU, memory, and network metrics
   - Error rates and latency

3. **AWS Health Dashboard**
   - Service status and maintenance windows

## Security

### Encryption
- All data encrypted at rest
- Transit encryption enabled for Redis
- HTTPS-only for CloudFront

### Access Control
- Security groups restrict network access
- IAM roles for service access
- Secrets Manager for credentials

### Compliance
- CloudTrail logging enabled
- VPC Flow Logs enabled
- Regular security audits

## Backup and Recovery

### Automated Backups
- RDS: Daily automated backups (7-day retention)
- Redis: Daily snapshots (5-day retention)
- S3: Versioning enabled on all buckets

### Manual Snapshots

```bash
# Create RDS snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier accelerapp-db-cluster \
  --db-cluster-snapshot-identifier manual-snapshot-$(date +%Y%m%d)

# Create Redis snapshot
aws elasticache create-snapshot \
  --replication-group-id accelerapp-cache-cluster \
  --snapshot-name manual-snapshot-$(date +%Y%m%d)
```

### Disaster Recovery
- Multi-AZ deployments for high availability
- Cross-region replication for critical data
- Documented recovery procedures (see DEPLOYMENT_GUIDE.md)

## Troubleshooting

### Common Issues

**Template Validation Errors**
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('template.yaml'))"
```

**Stack Creation Failures**
```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name <stack-name> \
  --max-items 10
```

**Resource Limits**
```bash
# Check service limits
aws service-quotas list-service-quotas \
  --service-code rds

aws service-quotas list-service-quotas \
  --service-code elasticache
```

## Updating Infrastructure

### Update Existing Stacks

```bash
aws cloudformation update-stack \
  --stack-name accelerapp-database \
  --template-body file://database/rds-aurora.yaml \
  --parameters <updated-parameters>
```

### Change Sets (Recommended)

```bash
# Create change set
aws cloudformation create-change-set \
  --stack-name accelerapp-database \
  --change-set-name update-2024-10-14 \
  --template-body file://database/rds-aurora.yaml

# Review changes
aws cloudformation describe-change-set \
  --change-set-name update-2024-10-14 \
  --stack-name accelerapp-database

# Execute if acceptable
aws cloudformation execute-change-set \
  --change-set-name update-2024-10-14 \
  --stack-name accelerapp-database
```

## Additional Resources

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment walkthrough
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS ElastiCache Documentation](https://docs.aws.amazon.com/elasticache/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Deployment Guide: See DEPLOYMENT_GUIDE.md
- AWS Support: https://aws.amazon.com/support

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Maintained By**: Accelerapp Team
