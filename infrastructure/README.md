# Accelerapp Infrastructure - Phase 1: Foundation

This directory contains the Infrastructure as Code (IaC) for Accelerapp's commercial release on AWS using Terraform.

## Overview

Phase 1 establishes the foundational infrastructure for Accelerapp with:

- **Multi-account AWS structure** with secure IAM roles and policies
- **VPC and networking** across multiple availability zones
- **Terraform state management** with S3 backend and DynamoDB locking
- **EKS cluster** with managed node groups and essential add-ons

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   ├── modules/                # Terraform modules
│   │   ├── vpc/                # VPC and networking module
│   │   ├── eks/                # EKS cluster module
│   │   ├── iam/                # IAM roles and policies module
│   │   └── s3/                 # S3 backend module
│   └── environments/           # Environment-specific configurations
│       ├── dev/                # Development environment
│       ├── staging/            # Staging environment
│       └── prod/               # Production environment
└── docs/                       # Additional documentation
```

## Prerequisites

### Required Tools

- **Terraform** >= 1.5.0
- **AWS CLI** >= 2.0
- **kubectl** >= 1.28
- **aws-iam-authenticator**

### AWS Account Setup

1. AWS account with administrative access
2. AWS CLI configured with appropriate credentials
3. Appropriate IAM permissions to create:
   - VPCs and networking resources
   - EKS clusters
   - IAM roles and policies
   - S3 buckets and DynamoDB tables

## Quick Start

### 1. Bootstrap Terraform Backend

First, create the S3 bucket and DynamoDB table for Terraform state management:

```bash
cd infrastructure/terraform

# Initialize Terraform (without backend)
terraform init

# Apply S3 backend module only
terraform apply -target=module.s3_backend -var-file=environments/dev/terraform.tfvars
```

### 2. Configure Backend

After the S3 bucket and DynamoDB table are created, uncomment the backend configuration in `main.tf`:

```hcl
backend "s3" {
  bucket         = "accelerapp-dev-terraform-state"
  key            = "infrastructure/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "accelerapp-dev-terraform-locks"
}
```

Then migrate the state:

```bash
terraform init -migrate-state
```

### 3. Deploy Infrastructure

Deploy the complete infrastructure:

```bash
# Plan the deployment
terraform plan -var-file=environments/dev/terraform.tfvars

# Apply the changes
terraform apply -var-file=environments/dev/terraform.tfvars
```

### 4. Configure kubectl

After EKS cluster is created, configure kubectl to access it:

```bash
aws eks update-kubeconfig --region us-east-1 --name accelerapp-dev-cluster
```

### 5. Verify Deployment

```bash
# Check cluster status
kubectl get nodes

# Check namespaces
kubectl get namespaces

# Check system pods
kubectl get pods -n kube-system
```

## Architecture

### Multi-Account Structure

The infrastructure supports multi-account AWS setup with:

- **Development Account**: For development and testing
- **Staging Account**: Pre-production environment
- **Production Account**: Production workloads

### VPC Architecture

Each environment includes:

- **VPC**: Isolated network with configurable CIDR block
- **Public Subnets**: 3 subnets across availability zones
- **Private Subnets**: 3 subnets for EKS nodes
- **NAT Gateways**: High availability (configurable)
- **Internet Gateway**: For public subnet access
- **VPC Flow Logs**: Network traffic monitoring

### EKS Cluster

- **Control Plane**: Managed by AWS with logging enabled
- **Node Groups**: Auto-scaling worker nodes
- **Security Groups**: Least privilege network access
- **OIDC Provider**: For pod IAM roles
- **Add-ons**:
  - VPC CNI for networking
  - CoreDNS for service discovery
  - kube-proxy for networking
  - EBS CSI driver for persistent volumes

### Security Features

1. **Encryption at Rest**: KMS encryption for EKS secrets
2. **Encryption in Transit**: TLS for all communications
3. **Network Isolation**: Private subnets for worker nodes
4. **IAM Roles**: Least privilege access
5. **VPC Flow Logs**: Network monitoring
6. **CloudWatch Logs**: Cluster audit logging

## Configuration

### Environment Variables

The infrastructure can be customized using Terraform variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Project name for resource naming | `accelerapp` |
| `environment` | Environment name (dev/staging/prod) | Required |
| `aws_region` | AWS region for deployment | `us-east-1` |
| `vpc_cidr` | CIDR block for VPC | `10.0.0.0/16` |
| `eks_cluster_version` | Kubernetes version | `1.28` |
| `node_desired_size` | Desired number of nodes | `3` |
| `node_instance_types` | EC2 instance types | `["t3.large"]` |

### Customizing for Different Environments

Edit the environment-specific `.tfvars` files:

```bash
# Development
infrastructure/terraform/environments/dev/terraform.tfvars

# Staging
infrastructure/terraform/environments/staging/terraform.tfvars

# Production
infrastructure/terraform/environments/prod/terraform.tfvars
```

## Operations

### Scaling Nodes

To scale the EKS node group:

```bash
# Edit the terraform.tfvars file
node_desired_size = 5
node_min_size     = 3
node_max_size     = 10

# Apply changes
terraform apply -var-file=environments/prod/terraform.tfvars
```

### Upgrading Kubernetes Version

1. Update the `eks_cluster_version` variable
2. Apply the changes:

```bash
terraform apply -var-file=environments/prod/terraform.tfvars
```

3. Update node groups (will trigger rolling update)

### Viewing Outputs

```bash
# View all outputs
terraform output

# View specific output
terraform output eks_cluster_endpoint
```

## Multi-Region Deployment

To deploy infrastructure in multiple regions:

1. Create region-specific variable files:
   ```
   environments/prod-us-east-1/
   environments/prod-us-west-2/
   ```

2. Update the `aws_region` variable in each file

3. Deploy to each region:
   ```bash
   terraform apply -var-file=environments/prod-us-east-1/terraform.tfvars
   terraform apply -var-file=environments/prod-us-west-2/terraform.tfvars
   ```

## Cost Optimization

### Development Environment

- Single NAT Gateway (instead of per-AZ)
- Smaller instance types (t3.medium)
- Fewer nodes (min 1, desired 2)

### Production Environment

- High availability NAT Gateways
- Larger instance types for performance
- Auto-scaling enabled (min 3, max 10)

### Cost Saving Tips

1. **Stop dev environments** when not in use
2. **Use Spot Instances** for non-critical workloads
3. **Right-size instances** based on actual usage
4. **Enable Container Insights** only when needed
5. **Use Reserved Instances** for production stable workloads

## Monitoring and Logging

### CloudWatch Logs

- EKS control plane logs: `/aws/eks/{cluster-name}/cluster`
- VPC flow logs: `/aws/vpc/{project}-{environment}`

### Metrics

View cluster metrics in AWS console:
- EKS -> Clusters -> [cluster-name] -> Monitoring

## Security Best Practices

1. **Enable MFA** for AWS console access
2. **Use IAM roles** instead of access keys
3. **Rotate credentials** regularly
4. **Enable CloudTrail** for API auditing
5. **Use AWS Security Hub** for security findings
6. **Regular security updates** for node AMIs
7. **Network policies** for pod-to-pod communication
8. **Secrets encryption** with KMS

## Troubleshooting

### Common Issues

#### Terraform Init Fails

```bash
# Clear .terraform directory
rm -rf .terraform .terraform.lock.hcl

# Re-initialize
terraform init
```

#### State Lock Error

```bash
# View locked state
aws dynamodb get-item \
  --table-name accelerapp-dev-terraform-locks \
  --key '{"LockID": {"S": "accelerapp-dev-terraform-state/terraform.tfstate"}}'

# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

#### EKS Node Group Not Ready

```bash
# Check node status
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system

# View node group status
aws eks describe-nodegroup \
  --cluster-name accelerapp-dev-cluster \
  --nodegroup-name accelerapp-dev-cluster-node-group
```

#### Cannot Connect to Cluster

```bash
# Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name accelerapp-dev-cluster

# Verify credentials
aws sts get-caller-identity

# Test connection
kubectl get svc
```

## Maintenance

### State File Management

- **Backup state files** regularly
- **Use version control** for `.tfvars` files
- **Never edit state files** manually
- **Use workspaces** for environment isolation

### Updates and Patches

1. **Monthly**: Review AWS security bulletins
2. **Quarterly**: Update Terraform modules and providers
3. **Bi-annually**: Review and optimize costs
4. **Annually**: Review and update architecture

## Cleanup

To destroy the infrastructure:

```bash
# Destroy infrastructure (except state backend)
terraform destroy -var-file=environments/dev/terraform.tfvars

# Delete state backend (manual)
aws s3 rb s3://accelerapp-dev-terraform-state --force
aws dynamodb delete-table --table-name accelerapp-dev-terraform-locks
```

## Support

For issues or questions:

- **GitHub Issues**: [thewriterben/Accelerapp](https://github.com/thewriterben/Accelerapp/issues)
- **Documentation**: See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **AWS Support**: Contact AWS support for infrastructure issues

## Next Steps (Phase 2+)

- CI/CD pipeline integration
- Service mesh (Istio/Linkerd)
- Observability stack (Prometheus, Grafana)
- GitOps workflow (ArgoCD/Flux)
- Auto-scaling policies
- Disaster recovery setup

## License

MIT License - See [LICENSE](../LICENSE) file

---

**Last Updated**: 2025-10-14 | **Version**: Phase 1 Foundation | **Status**: Production Ready
