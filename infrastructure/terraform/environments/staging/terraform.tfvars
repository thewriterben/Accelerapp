# Staging Environment Configuration

project_name = "accelerapp"
environment  = "staging"
aws_region   = "us-east-1"

# VPC Configuration
vpc_cidr           = "10.1.0.0/16"
enable_nat_gateway = true
single_nat_gateway = false  # High availability

# EKS Configuration
eks_cluster_name    = "accelerapp-staging-cluster"
eks_cluster_version = "1.28"

# Node Group Configuration
node_desired_size  = 3
node_min_size      = 2
node_max_size      = 6
node_instance_types = ["t3.large"]
