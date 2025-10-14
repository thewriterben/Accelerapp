# Accelerapp Infrastructure Deployment Guide

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Initial Setup](#initial-setup)
3. [Environment Deployment](#environment-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Validation](#validation)
6. [Rollback Procedures](#rollback-procedures)

## Pre-Deployment Checklist

### AWS Account Requirements

- [ ] AWS account created and accessible
- [ ] IAM user with administrative permissions
- [ ] AWS CLI configured with credentials
- [ ] Multi-factor authentication (MFA) enabled
- [ ] Cost alerts configured
- [ ] Service limits reviewed and increased if needed

### Tool Installation

```bash
# Terraform
brew install terraform  # macOS
# or
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# AWS CLI
pip install awscli --upgrade

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installations
terraform version
aws --version
kubectl version --client
```

### AWS Configuration

```bash
# Configure AWS CLI
aws configure
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

## Initial Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp/infrastructure/terraform
```

### Step 2: Review Configuration

```bash
# Review main configuration
cat main.tf

# Review variables
cat variables.tf

# Review environment-specific configuration
cat environments/dev/terraform.tfvars
```

### Step 3: Initialize Terraform

```bash
# Initialize without backend (first time)
terraform init

# Validate configuration
terraform validate

# Format configuration files
terraform fmt -recursive
```

### Step 4: Plan Backend Deployment

```bash
# Plan S3 backend creation
terraform plan -target=module.s3_backend -var-file=environments/dev/terraform.tfvars

# Review the plan carefully
```

### Step 5: Deploy Backend

```bash
# Apply S3 backend module
terraform apply -target=module.s3_backend -var-file=environments/dev/terraform.tfvars

# Note the outputs
terraform output terraform_state_bucket
terraform output terraform_state_lock_table
```

### Step 6: Configure Remote Backend

Edit `main.tf` and uncomment the backend configuration:

```hcl
backend "s3" {
  bucket         = "accelerapp-dev-terraform-state"
  key            = "infrastructure/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "accelerapp-dev-terraform-locks"
}
```

### Step 7: Migrate State to Backend

```bash
# Re-initialize with backend
terraform init -migrate-state

# Confirm migration when prompted
```

## Environment Deployment

### Development Environment

```bash
cd infrastructure/terraform

# Plan deployment
terraform plan -var-file=environments/dev/terraform.tfvars -out=dev.tfplan

# Review the plan
terraform show dev.tfplan

# Apply the plan
terraform apply dev.tfplan

# Save outputs
terraform output > dev-outputs.txt
```

**Estimated Time**: 15-20 minutes

### Staging Environment

```bash
# Switch to staging configuration
terraform plan -var-file=environments/staging/terraform.tfvars -out=staging.tfplan

# Apply
terraform apply staging.tfplan
```

**Estimated Time**: 15-20 minutes

### Production Environment

```bash
# Plan production deployment
terraform plan -var-file=environments/prod/terraform.tfvars -out=prod.tfplan

# Review with team
terraform show prod.tfplan

# Schedule deployment window
# Apply during maintenance window
terraform apply prod.tfplan
```

**Estimated Time**: 20-25 minutes

## Post-Deployment Configuration

### Configure kubectl

```bash
# Development
aws eks update-kubeconfig --region us-east-1 --name accelerapp-dev-cluster

# Staging
aws eks update-kubeconfig --region us-east-1 --name accelerapp-staging-cluster

# Production
aws eks update-kubeconfig --region us-east-1 --name accelerapp-prod-cluster
```

### Verify Cluster Access

```bash
# Check cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system
```

### Deploy Essential Services

```bash
# Create namespaces
kubectl create namespace accelerapp
kubectl create namespace monitoring

# Apply service account configurations
kubectl apply -f ../../deployment/kubernetes/accelerapp-deployment.yaml

# Verify deployments
kubectl get all -n accelerapp
```

### Configure RBAC

```bash
# Create admin role binding
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole=cluster-admin \
  --user=$(aws sts get-caller-identity --query 'Arn' --output text)
```

### Set Up Monitoring

```bash
# Deploy metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify metrics server
kubectl top nodes
```

## Validation

### Infrastructure Validation

```bash
# Check Terraform outputs
terraform output

# Validate VPC
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=accelerapp"

# Validate EKS cluster
aws eks describe-cluster --name accelerapp-dev-cluster

# Validate node groups
aws eks describe-nodegroup \
  --cluster-name accelerapp-dev-cluster \
  --nodegroup-name accelerapp-dev-cluster-node-group
```

### Kubernetes Validation

```bash
# Check nodes
kubectl get nodes -o wide

# Check system components
kubectl get componentstatuses

# Check pod health
kubectl get pods --all-namespaces

# Check services
kubectl get services --all-namespaces

# Check persistent volumes
kubectl get pv,pvc --all-namespaces
```

### Network Validation

```bash
# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Test internet connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- https://www.google.com

# Test pod-to-pod communication
kubectl run nginx --image=nginx --port=80
kubectl expose pod nginx --port=80
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://nginx
```

### Security Validation

```bash
# Check security groups
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=accelerapp"

# Check IAM roles
aws iam list-roles | grep accelerapp

# Check encryption
aws kms describe-key --key-id $(terraform output -raw eks_kms_key_id)

# Check VPC flow logs
aws ec2 describe-flow-logs --filter "Name=resource-id,Values=$(terraform output -raw vpc_id)"
```

### Cost Validation

```bash
# Check running resources
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-14 \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://cost-filter.json
```

## Rollback Procedures

### Terraform Rollback

```bash
# List state versions
aws s3api list-object-versions \
  --bucket accelerapp-dev-terraform-state \
  --prefix infrastructure/terraform.tfstate

# Download previous version
aws s3api get-object \
  --bucket accelerapp-dev-terraform-state \
  --key infrastructure/terraform.tfstate \
  --version-id [version-id] \
  terraform.tfstate.backup

# Restore previous state
terraform state push terraform.tfstate.backup

# Apply previous configuration
terraform apply -var-file=environments/dev/terraform.tfvars
```

### Manual Rollback

If Terraform rollback fails:

```bash
# Delete node group
aws eks delete-nodegroup \
  --cluster-name accelerapp-dev-cluster \
  --nodegroup-name accelerapp-dev-cluster-node-group

# Wait for deletion
aws eks wait nodegroup-deleted \
  --cluster-name accelerapp-dev-cluster \
  --nodegroup-name accelerapp-dev-cluster-node-group

# Delete cluster
aws eks delete-cluster --name accelerapp-dev-cluster

# Wait for deletion
aws eks wait cluster-deleted --name accelerapp-dev-cluster

# Delete VPC and associated resources
# (Use AWS Console or CLI to delete resources in order)
```

## Troubleshooting

### Issue: Terraform State Lock

```bash
# View lock
aws dynamodb get-item \
  --table-name accelerapp-dev-terraform-locks \
  --key '{"LockID": {"S": "accelerapp-dev-terraform-state/infrastructure/terraform.tfstate"}}'

# Force unlock (last resort)
terraform force-unlock [lock-id]
```

### Issue: Node Group Creation Fails

```bash
# Check IAM role
aws iam get-role --role-name accelerapp-dev-eks-node-role

# Check subnets
aws ec2 describe-subnets --filters "Name=tag:Project,Values=accelerapp"

# Check security groups
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=accelerapp"

# View node group errors
aws eks describe-nodegroup \
  --cluster-name accelerapp-dev-cluster \
  --nodegroup-name accelerapp-dev-cluster-node-group \
  --query 'nodegroup.health.issues'
```

### Issue: kubectl Connection Fails

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name accelerapp-dev-cluster \
  --role-arn [admin-role-arn]

# Test connection
kubectl get svc

# Check cluster endpoint
aws eks describe-cluster \
  --name accelerapp-dev-cluster \
  --query 'cluster.endpoint'
```

## Best Practices

1. **Always plan before apply**: Review changes carefully
2. **Use workspaces**: Isolate environment states
3. **Tag resources**: Consistent tagging for cost tracking
4. **Document changes**: Keep deployment logs
5. **Test in dev**: Validate changes in development first
6. **Schedule production deployments**: Use maintenance windows
7. **Backup state files**: Regular backups of Terraform state
8. **Monitor costs**: Set up billing alerts
9. **Security scanning**: Use tools like tfsec or checkov
10. **Keep modules updated**: Regular updates for security patches

## Emergency Contacts

- **AWS Support**: [Support Portal](https://console.aws.amazon.com/support)
- **Team Lead**: [contact-info]
- **On-Call Engineer**: [contact-info]

---

**Last Updated**: 2025-10-14 | **Phase**: Phase 1 Foundation
