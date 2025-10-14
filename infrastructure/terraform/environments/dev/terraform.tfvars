# Development Environment Configuration

project_name = "accelerapp"
environment  = "dev"
aws_region   = "us-east-1"

# VPC Configuration
vpc_cidr           = "10.0.0.0/16"
enable_nat_gateway = true
single_nat_gateway = true  # Cost savings for dev

# EKS Configuration
eks_cluster_name    = "accelerapp-dev-cluster"
eks_cluster_version = "1.28"

# Node Group Configuration
node_desired_size  = 2
node_min_size      = 1
node_max_size      = 4
node_instance_types = ["t3.medium"]
