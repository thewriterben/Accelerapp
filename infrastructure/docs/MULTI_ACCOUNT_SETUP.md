# Multi-Account AWS Setup for Accelerapp

## Overview

This guide describes the multi-account AWS structure for Accelerapp, providing secure isolation between environments and enabling centralized governance.

## Account Structure

```
Root Organization
├── Management Account (Root)
│   └── AWS Organizations, CloudTrail, Billing
├── Security Account
│   └── Security Hub, GuardDuty, CloudTrail aggregation
├── Shared Services Account
│   ├── CI/CD pipelines
│   ├── Container Registry (ECR)
│   └── Artifact storage
├── Development Account
│   └── Development EKS cluster
├── Staging Account
│   └── Staging EKS cluster
└── Production Account
    └── Production EKS cluster
```

## Account Setup

### 1. Create Organization

```bash
# From Management Account
aws organizations create-organization --feature-set ALL

# Verify organization
aws organizations describe-organization
```

### 2. Create Organizational Units (OUs)

```bash
# Get root ID
ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

# Create OUs
aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name "Security"

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name "Infrastructure"

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name "Workloads"
```

### 3. Create Member Accounts

```bash
# Development Account
aws organizations create-account \
  --email accelerapp-dev@example.com \
  --account-name "Accelerapp Development"

# Staging Account
aws organizations create-account \
  --email accelerapp-staging@example.com \
  --account-name "Accelerapp Staging"

# Production Account
aws organizations create-account \
  --email accelerapp-prod@example.com \
  --account-name "Accelerapp Production"

# Security Account
aws organizations create-account \
  --email accelerapp-security@example.com \
  --account-name "Accelerapp Security"

# Shared Services Account
aws organizations create-account \
  --email accelerapp-shared@example.com \
  --account-name "Accelerapp Shared Services"
```

## Cross-Account IAM Roles

### Create OrganizationAccountAccessRole

This role allows the management account to access member accounts.

**In Management Account:**

```bash
# Create assume role policy
cat > assume-role-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::MANAGEMENT_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
```

**In Each Member Account:**

```bash
# Create role
aws iam create-role \
  --role-name OrganizationAccountAccessRole \
  --assume-role-policy-document file://assume-role-policy.json

# Attach administrator access
aws iam attach-role-policy \
  --role-name OrganizationAccountAccessRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Create Cross-Account Deployment Role

**In Member Accounts:**

```hcl
# terraform/modules/iam/cross-account.tf
resource "aws_iam_role" "cross_account_deployment" {
  name = "CrossAccountDeploymentRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.shared_services_account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.external_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "deployment_policy" {
  role       = aws_iam_role.cross_account_deployment.name
  policy_arn = aws_iam_policy.deployment_policy.arn
}
```

## Service Control Policies (SCPs)

### Deny Root Account Usage

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootAccount",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        }
      }
    }
  ]
}
```

### Require MFA

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireMFA",
      "Effect": "Deny",
      "Action": [
        "ec2:*",
        "rds:*",
        "s3:*"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### Restrict Regions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        }
      }
    }
  ]
}
```

## Account-Specific Configuration

### Development Account

```hcl
# environments/dev/backend.tf
terraform {
  backend "s3" {
    bucket         = "accelerapp-dev-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "accelerapp-dev-terraform-locks"
    role_arn       = "arn:aws:iam::DEV_ACCOUNT_ID:role/TerraformRole"
  }
}

provider "aws" {
  region = "us-east-1"
  
  assume_role {
    role_arn = "arn:aws:iam::DEV_ACCOUNT_ID:role/TerraformRole"
  }
}
```

### Staging Account

```hcl
# environments/staging/backend.tf
terraform {
  backend "s3" {
    bucket         = "accelerapp-staging-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "accelerapp-staging-terraform-locks"
    role_arn       = "arn:aws:iam::STAGING_ACCOUNT_ID:role/TerraformRole"
  }
}

provider "aws" {
  region = "us-east-1"
  
  assume_role {
    role_arn = "arn:aws:iam::STAGING_ACCOUNT_ID:role/TerraformRole"
  }
}
```

### Production Account

```hcl
# environments/prod/backend.tf
terraform {
  backend "s3" {
    bucket         = "accelerapp-prod-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "accelerapp-prod-terraform-locks"
    role_arn       = "arn:aws:iam::PROD_ACCOUNT_ID:role/TerraformRole"
  }
}

provider "aws" {
  region = "us-east-1"
  
  assume_role {
    role_arn = "arn:aws:iam::PROD_ACCOUNT_ID:role/TerraformRole"
  }
}
```

## Centralized Logging

### CloudTrail Setup

**In Management Account:**

```bash
# Create S3 bucket for CloudTrail
aws s3 mb s3://accelerapp-cloudtrail-logs --region us-east-1

# Enable organization trail
aws cloudtrail create-trail \
  --name accelerapp-org-trail \
  --s3-bucket-name accelerapp-cloudtrail-logs \
  --is-organization-trail \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging --name accelerapp-org-trail
```

### CloudWatch Logs Aggregation

```hcl
# In Security Account
resource "aws_cloudwatch_log_destination" "central_logging" {
  name       = "CentralLogging"
  role_arn   = aws_iam_role.cloudwatch_logs.arn
  target_arn = aws_kinesis_firehose_delivery_stream.logs.arn
}

resource "aws_cloudwatch_log_destination_policy" "central_logging" {
  destination_name = aws_cloudwatch_log_destination.central_logging.name
  access_policy    = data.aws_iam_policy_document.cloudwatch_logs_destination.json
}
```

## Security Hub Configuration

**In Security Account:**

```bash
# Enable Security Hub
aws securityhub enable-security-hub

# Enable AWS Foundational Security Best Practices
aws securityhub batch-enable-standards \
  --standards-subscription-requests '[{"StandardsArn":"arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0"}]'

# Invite member accounts
aws securityhub create-members \
  --account-details '[
    {"AccountId":"DEV_ACCOUNT_ID","Email":"accelerapp-dev@example.com"},
    {"AccountId":"STAGING_ACCOUNT_ID","Email":"accelerapp-staging@example.com"},
    {"AccountId":"PROD_ACCOUNT_ID","Email":"accelerapp-prod@example.com"}
  ]'
```

## GuardDuty Configuration

**In Security Account:**

```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Invite member accounts
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)

aws guardduty create-members \
  --detector-id $DETECTOR_ID \
  --account-details '[
    {"AccountId":"DEV_ACCOUNT_ID","Email":"accelerapp-dev@example.com"},
    {"AccountId":"STAGING_ACCOUNT_ID","Email":"accelerapp-staging@example.com"},
    {"AccountId":"PROD_ACCOUNT_ID","Email":"accelerapp-prod@example.com"}
  ]'
```

## Cost Management

### Cost Allocation Tags

```bash
# Activate cost allocation tags
aws ce activate-cost-allocation-tags --tag-keys Environment Project Owner
```

### Budget Alerts

```bash
# Create budget
aws budgets create-budget \
  --account-id ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "Accelerapp-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "5000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

## Deployment Workflow

### 1. Assume Role in Target Account

```bash
# Set credentials for target account
aws sts assume-role \
  --role-arn arn:aws:iam::TARGET_ACCOUNT_ID:role/TerraformRole \
  --role-session-name terraform-session \
  --output json > credentials.json

# Export credentials
export AWS_ACCESS_KEY_ID=$(jq -r '.Credentials.AccessKeyId' credentials.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.Credentials.SecretAccessKey' credentials.json)
export AWS_SESSION_TOKEN=$(jq -r '.Credentials.SessionToken' credentials.json)
```

### 2. Deploy Infrastructure

```bash
# Deploy to development account
terraform apply -var-file=environments/dev/terraform.tfvars

# Deploy to staging account
terraform apply -var-file=environments/staging/terraform.tfvars

# Deploy to production account
terraform apply -var-file=environments/prod/terraform.tfvars
```

## Best Practices

1. **Use separate AWS accounts** for each environment
2. **Enable CloudTrail** in all accounts
3. **Implement SCPs** for organization-wide policies
4. **Use cross-account roles** instead of sharing credentials
5. **Enable GuardDuty** for threat detection
6. **Centralize logging** in security account
7. **Implement least privilege** access
8. **Regular security audits** using Security Hub
9. **Tag all resources** for cost tracking
10. **Monitor costs** across all accounts

---

**Last Updated**: 2025-10-14 | **Phase**: Phase 1 Foundation
