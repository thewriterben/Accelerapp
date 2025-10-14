# Main Terraform configuration for Accelerapp Infrastructure
# Phase 1: Foundation - Infrastructure Setup

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure after creating the S3 bucket and DynamoDB table
  # backend "s3" {
  #   bucket         = "accelerapp-terraform-state"
  #   key            = "infrastructure/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "accelerapp-terraform-locks"
  # }
}

# AWS Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Accelerapp"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Phase       = "Phase1-Foundation"
    }
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name        = var.project_name
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = data.aws_availability_zones.available.names
  enable_nat_gateway  = var.enable_nat_gateway
  single_nat_gateway  = var.single_nat_gateway
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  eks_cluster_name = var.eks_cluster_name
}

# EKS Module
module "eks" {
  source = "./modules/eks"

  project_name         = var.project_name
  environment          = var.environment
  cluster_name         = var.eks_cluster_name
  cluster_version      = var.eks_cluster_version
  vpc_id               = module.vpc.vpc_id
  subnet_ids           = module.vpc.private_subnet_ids
  cluster_role_arn     = module.iam.eks_cluster_role_arn
  node_role_arn        = module.iam.eks_node_role_arn
  desired_size         = var.node_desired_size
  min_size             = var.node_min_size
  max_size             = var.node_max_size
  instance_types       = var.node_instance_types
}

# S3 Module for Terraform state backend (bootstrap)
module "s3_backend" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}
