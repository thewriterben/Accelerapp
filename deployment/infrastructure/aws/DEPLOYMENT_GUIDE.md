# Phase 2: Core Services Deployment Guide

This guide provides instructions for deploying core infrastructure services for Accelerapp Phase 2, including RDS Aurora, Redis cache, S3 storage, CloudFront CDN, and AWS Secrets Manager.

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS account with necessary permissions (IAM, RDS, ElastiCache, S3, CloudFront, Secrets Manager)
- VPC with public and private subnets configured
- Application security group created

## Architecture Overview

The Phase 2 core services infrastructure consists of:

1. **RDS Aurora PostgreSQL** - Primary database cluster with multi-AZ deployment
2. **ElastiCache Redis** - Cache cluster with automatic failover
3. **S3 Buckets** - Separate buckets for assets and backups
4. **CloudFront CDN** - Content delivery network for static assets
5. **AWS Secrets Manager** - Secure storage for credentials and API keys

## Deployment Steps

### 1. Deploy RDS Aurora Database

The RDS Aurora cluster provides a highly available, scalable PostgreSQL database.

**Deploy using CloudFormation:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-database \
  --template-body file://database/rds-aurora.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-xxxxx \
    ParameterKey=PrivateSubnetIds,ParameterValue=subnet-xxxxx\\,subnet-yyyyy \
    ParameterKey=AppSecurityGroup,ParameterValue=sg-xxxxx \
    ParameterKey=DBMasterPassword,ParameterValue=YourSecurePassword123! \
  --capabilities CAPABILITY_IAM
```

**Features:**
- Multi-AZ deployment for high availability
- Automated backups with 7-day retention
- Encryption at rest using AWS KMS
- Performance Insights enabled
- CloudWatch Logs integration

**Connection Information:**

After deployment, retrieve the endpoints:

```bash
aws cloudformation describe-stacks \
  --stack-name accelerapp-database \
  --query 'Stacks[0].Outputs'
```

### 2. Deploy Redis Cache Cluster

The Redis cluster provides in-memory caching with automatic failover.

**Deploy using CloudFormation:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-cache \
  --template-body file://cache/redis-cluster.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-xxxxx \
    ParameterKey=PrivateSubnetIds,ParameterValue=subnet-xxxxx\\,subnet-yyyyy \
    ParameterKey=AppSecurityGroup,ParameterValue=sg-xxxxx
```

**Features:**
- Multi-AZ with automatic failover
- Encryption in transit and at rest
- Automated snapshots with 5-day retention
- Redis 7.0 with optimized parameter group

**Connection Information:**

```bash
aws cloudformation describe-stacks \
  --stack-name accelerapp-cache \
  --query 'Stacks[0].Outputs'
```

### 3. Deploy S3 Buckets

Create separate buckets for assets and backups.

**Deploy Assets Bucket:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-storage-assets \
  --template-body file://storage/s3-assets.yaml
```

**Features:**
- Versioning enabled
- Server-side encryption (AES256)
- CORS configuration for web access
- Lifecycle policy for old versions
- Public access blocked by default

**Deploy Backups Bucket:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-storage-backups \
  --template-body file://storage/s3-backups.yaml
```

**Features:**
- Versioning enabled
- Encryption at rest
- Lifecycle policy with Glacier transition after 30 days
- 1-year retention policy
- Public access blocked

### 4. Deploy CloudFront CDN

The CloudFront distribution provides global content delivery for static assets.

**Deploy using CloudFormation:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-cdn \
  --template-body file://cdn/cloudfront.yaml
```

**Features:**
- Origin Access Identity for secure S3 access
- HTTPS-only (redirect to HTTPS)
- Compression enabled
- Optimized caching with configurable TTLs
- Edge locations for low latency

**Distribution URL:**

```bash
aws cloudformation describe-stacks \
  --stack-name accelerapp-cdn \
  --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' \
  --output text
```

### 5. Deploy Secrets Manager

Securely store database credentials and API keys.

**Deploy Database Credentials Secret:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-secrets-db \
  --template-body file://secrets/db-credentials.yaml \
  --parameters \
    ParameterKey=RotationLambdaArn,ParameterValue=arn:aws:lambda:region:account:function/rotation-lambda
```

**Set the secret value:**

```bash
aws secretsmanager put-secret-value \
  --secret-id accelerapp/db/credentials \
  --secret-string '{"username":"admin","password":"YourSecurePassword123!","host":"db-endpoint","port":"5432","database":"accelerapp"}'
```

**Deploy API Keys Secret:**

```bash
aws cloudformation create-stack \
  --stack-name accelerapp-secrets-api \
  --template-body file://secrets/api-keys.yaml
```

**Set the API keys:**

```bash
aws secretsmanager put-secret-value \
  --secret-id accelerapp/api/keys \
  --secret-string '{"api_key":"your-api-key","webhook_secret":"your-webhook-secret"}'
```

## Environment Configuration

After deploying all services, configure your application environment:

**Environment Variables:**

```bash
# Database
export DB_HOST=$(aws cloudformation describe-stacks --stack-name accelerapp-database --query 'Stacks[0].Outputs[?OutputKey==`DBClusterEndpoint`].OutputValue' --output text)
export DB_PORT=5432
export DB_NAME=accelerapp
export DB_SECRET_ARN=$(aws cloudformation describe-stacks --stack-name accelerapp-secrets-db --query 'Stacks[0].Outputs[?OutputKey==`SecretArn`].OutputValue' --output text)

# Cache
export REDIS_HOST=$(aws cloudformation describe-stacks --stack-name accelerapp-cache --query 'Stacks[0].Outputs[?OutputKey==`CacheEndpoint`].OutputValue' --output text)
export REDIS_PORT=6379

# Storage
export S3_ASSETS_BUCKET=$(aws cloudformation describe-stacks --stack-name accelerapp-storage-assets --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)
export S3_BACKUPS_BUCKET=$(aws cloudformation describe-stacks --stack-name accelerapp-storage-backups --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)

# CDN
export CDN_DOMAIN=$(aws cloudformation describe-stacks --stack-name accelerapp-cdn --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' --output text)

# Secrets
export API_SECRET_ARN=$(aws cloudformation describe-stacks --stack-name accelerapp-secrets-api --query 'Stacks[0].Outputs[?OutputKey==`SecretArn`].OutputValue' --output text)
```

## Verification

### 1. Database Connectivity

Test database connection:

```bash
psql -h $DB_HOST -p 5432 -U admin -d accelerapp
```

### 2. Redis Connectivity

Test Redis connection:

```bash
redis-cli -h $REDIS_HOST -p 6379 ping
```

Expected output: `PONG`

### 3. S3 Bucket Access

Test S3 bucket access:

```bash
# Upload test file
echo "test" > test.txt
aws s3 cp test.txt s3://$S3_ASSETS_BUCKET/test.txt

# Download test file
aws s3 cp s3://$S3_ASSETS_BUCKET/test.txt test-downloaded.txt

# Clean up
rm test.txt test-downloaded.txt
aws s3 rm s3://$S3_ASSETS_BUCKET/test.txt
```

### 4. CloudFront Distribution

Test CloudFront:

```bash
curl -I https://$CDN_DOMAIN/test.txt
```

### 5. Secrets Manager

Retrieve secrets:

```bash
# Database credentials
aws secretsmanager get-secret-value --secret-id accelerapp/db/credentials

# API keys
aws secretsmanager get-secret-value --secret-id accelerapp/api/keys
```

## Monitoring and Maintenance

### CloudWatch Dashboards

Create a CloudWatch dashboard to monitor all services:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name accelerapp-phase2-services \
  --dashboard-body file://monitoring/dashboard.json
```

### Alarms

Set up CloudWatch alarms for critical metrics:

- **Database**: CPU utilization, connection count, replication lag
- **Cache**: CPU utilization, evictions, network throughput
- **S3**: Request rate, 4xx/5xx errors
- **CloudFront**: Request count, error rate, cache hit ratio

### Backup Verification

Regularly verify backups:

```bash
# List RDS snapshots
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier accelerapp-db-cluster

# List Redis snapshots
aws elasticache describe-snapshots \
  --replication-group-id accelerapp-cache-cluster

# List S3 versions
aws s3api list-object-versions \
  --bucket $S3_BACKUPS_BUCKET
```

## Cost Optimization

### Right-Sizing

- Monitor database and cache utilization
- Consider Aurora Serverless v2 for variable workloads
- Use CloudFront price class optimization

### Reserved Instances

Purchase reserved instances for predictable workloads:

```bash
# Check available RDS reserved instances
aws rds describe-reserved-db-instances-offerings

# Check available ElastiCache reserved nodes
aws elasticache describe-reserved-cache-nodes-offerings
```

### Lifecycle Policies

Ensure lifecycle policies are active:

- S3 versioning cleanup
- Glacier transition for backups
- CloudWatch Logs retention

## Security Best Practices

1. **Network Security**
   - Database and cache in private subnets only
   - Security groups with minimal ingress rules
   - VPC endpoints for AWS services

2. **Encryption**
   - All services use encryption at rest
   - Transit encryption enabled for Redis
   - HTTPS-only for CloudFront

3. **Access Control**
   - IAM roles for service access
   - Secrets Manager for credentials
   - Regular credential rotation

4. **Audit and Compliance**
   - CloudTrail logging enabled
   - VPC Flow Logs enabled
   - Regular security audits

## Troubleshooting

### Common Issues

**Database Connection Timeout**
- Check security group rules
- Verify subnet routing
- Check network ACLs

**Redis Connection Errors**
- Verify encryption settings match client
- Check security group ingress rules
- Ensure client supports Redis 7.0

**S3 Access Denied**
- Check bucket policy
- Verify IAM permissions
- Check CORS configuration

**CloudFront Cache Issues**
- Invalidate cache: `aws cloudfront create-invalidation --distribution-id ID --paths "/*"`
- Check origin response headers
- Verify cache behaviors

## Rollback Procedures

If deployment fails, rollback using:

```bash
# Delete stack (will delete all resources)
aws cloudformation delete-stack --stack-name <stack-name>

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name <stack-name>
```

**Note**: Database deletion protection must be disabled before stack deletion.

## Next Steps

After completing Phase 2 core services deployment:

1. Configure application to use deployed services
2. Set up monitoring and alerting
3. Configure automated backups
4. Implement disaster recovery procedures
5. Proceed to Phase 3: Application deployment

## Support

For issues or questions:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: See repository README.md
- AWS Support: https://aws.amazon.com/support

---

**Last Updated**: 2025-10-14  
**Version**: 1.0.0  
**Status**: Production Ready
