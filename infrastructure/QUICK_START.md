# Accelerapp Infrastructure - Quick Start Guide

## Prerequisites

Install these tools before beginning:

```bash
# Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# AWS CLI
pip install awscli --upgrade

# kubectl
brew install kubectl  # macOS
# or download from https://kubernetes.io/docs/tasks/tools/
```

Configure AWS credentials:

```bash
aws configure
```

## 5-Minute Quick Deploy

### Option 1: Automated (Recommended)

```bash
# Clone repository
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp/infrastructure

# Validate setup
./scripts/validate.sh

# Deploy development environment
./scripts/bootstrap.sh dev
```

### Option 2: Manual Steps

```bash
cd Accelerapp/infrastructure/terraform

# 1. Initialize Terraform
terraform init

# 2. Deploy backend
terraform apply -target=module.s3_backend \
  -var-file=environments/dev/terraform.tfvars \
  -auto-approve

# 3. Configure remote backend
# Uncomment backend configuration in main.tf, then:
terraform init -migrate-state

# 4. Deploy infrastructure
terraform apply \
  -var-file=environments/dev/terraform.tfvars

# 5. Configure kubectl
aws eks update-kubeconfig \
  --region us-east-1 \
  --name accelerapp-dev-cluster

# 6. Verify
kubectl get nodes
```

## Verify Deployment

```bash
# Check cluster
kubectl cluster-info

# Check nodes
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system

# Deploy test app
kubectl run nginx --image=nginx --port=80
kubectl get pods
```

## Common Tasks

### View Infrastructure Outputs

```bash
cd infrastructure/terraform
terraform output
```

### Scale Nodes

```bash
# Edit environments/dev/terraform.tfvars
node_desired_size = 4

# Apply
terraform apply -var-file=environments/dev/terraform.tfvars
```

### Deploy to Staging/Production

```bash
# Staging
terraform apply -var-file=environments/staging/terraform.tfvars

# Production
terraform apply -var-file=environments/prod/terraform.tfvars
```

### Destroy Infrastructure

```bash
# CAUTION: This will delete everything
terraform destroy -var-file=environments/dev/terraform.tfvars
```

## Troubleshooting

### Issue: "terraform: command not found"
**Solution**: Install Terraform from https://www.terraform.io/downloads

### Issue: "Error: configuring Terraform AWS Provider: no valid credential sources"
**Solution**: Run `aws configure` and enter your credentials

### Issue: "Error: error creating EKS Cluster: LimitExceededException"
**Solution**: Request service limit increase or use smaller instance types

### Issue: kubectl connection fails
**Solution**: 
```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name accelerapp-dev-cluster
```

## Next Steps

1. ✅ Infrastructure deployed
2. 📝 Deploy applications: See `deployment/kubernetes/`
3. 🔍 Set up monitoring: Configure CloudWatch or Prometheus
4. 🚀 Configure CI/CD: Set up deployment pipelines
5. 🌐 Configure DNS: Set up Route53 and ingress

## Resources

- **Full Documentation**: [README.md](README.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Multi-Account Setup**: [docs/MULTI_ACCOUNT_SETUP.md](docs/MULTI_ACCOUNT_SETUP.md)
- **Phase 1 Summary**: [../PHASE1_INFRASTRUCTURE_SUMMARY.md](../PHASE1_INFRASTRUCTURE_SUMMARY.md)

## Support

- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: See README.md files in each directory

---

**Ready to deploy?** Run `./scripts/bootstrap.sh dev` to get started! 🚀
