# Accelerapp Infrastructure Architecture

## Overview

This document describes the architecture of Accelerapp's AWS infrastructure deployed using Terraform.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS Cloud (us-east-1)                            │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Management Account                            │   │
│  │  • AWS Organizations                                             │   │
│  │  • CloudTrail (Organization Trail)                               │   │
│  │  • Billing & Cost Management                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────┬─────────────────┬─────────────────────────────┐   │
│  │ Dev Account     │ Staging Account │ Production Account          │   │
│  └─────────────────┴─────────────────┴─────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## VPC Architecture (Per Environment)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Internet Gateway                              │  │
│  └────────────────────────────┬────────────────────────────────────────┘  │
│                                │                                            │
│  ┌─────────────────────────────┼────────────────────────────────────────┐  │
│  │          Availability Zone 1│      AZ 2              AZ 3            │  │
│  │                              │                                        │  │
│  │  ┌──────────────────────────▼─────────────────────────────────┐     │  │
│  │  │              Public Subnets (10.0.0.0/20)                   │     │  │
│  │  │  ┌──────────┐        ┌──────────┐        ┌──────────┐      │     │  │
│  │  │  │ Public-1 │        │ Public-2 │        │ Public-3 │      │     │  │
│  │  │  │10.0.0.0/2│        │10.0.16.0/│        │10.0.32.0/│      │     │  │
│  │  │  │    2     │        │    22    │        │    22    │      │     │  │
│  │  │  └────┬─────┘        └────┬─────┘        └────┬─────┘      │     │  │
│  │  │       │                   │                   │             │     │  │
│  │  │  ┌────▼─────┐        ┌────▼─────┐        ┌───▼──────┐     │     │  │
│  │  │  │   NAT    │        │   NAT    │        │   NAT    │     │     │  │
│  │  │  │ Gateway  │        │ Gateway  │        │ Gateway  │     │     │  │
│  │  │  └────┬─────┘        └────┬─────┘        └────┬─────┘     │     │  │
│  │  └───────┼───────────────────┼───────────────────┼──────────────────┘  │
│  │          │                   │                   │                      │
│  │  ┌───────▼───────────────────▼───────────────────▼──────────────────┐  │
│  │  │             Private Subnets (10.0.48.0/20)                        │  │
│  │  │  ┌──────────┐        ┌──────────┐        ┌──────────┐            │  │
│  │  │  │Private-1 │        │Private-2 │        │Private-3 │            │  │
│  │  │  │10.0.48.0/│        │10.0.64.0/│        │10.0.80.0/│            │  │
│  │  │  │    22    │        │    22    │        │    22    │            │  │
│  │  │  └────┬─────┘        └────┬─────┘        └────┬─────┘            │  │
│  │  │       │                   │                   │                   │  │
│  │  │  ┌────▼──────────────────┬▼──────────────────┬▼──────────┐       │  │
│  │  │  │        EKS Worker Nodes (Auto Scaling)                  │       │  │
│  │  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │       │  │
│  │  │  │  │Node-1│  │Node-2│  │Node-3│  │Node-4│  │Node-5│    │       │  │
│  │  │  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘    │       │  │
│  │  │  └──────────────────────────────────────────────────────┘       │  │
│  │  └────────────────────────────────────────────────────────────────┘  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    EKS Control Plane (Managed by AWS)                │  │
│  │  • API Server          • Controller Manager    • Scheduler           │  │
│  │  • etcd (encrypted)    • CloudWatch Logs       • OIDC Provider       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         Security Layers                                     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Layer 1: Network Security                                            │  │
│  │  • VPC Isolation                  • Security Groups                  │  │
│  │  • Private Subnets               • Network ACLs                      │  │
│  │  • VPC Flow Logs                 • NAT Gateways                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Layer 2: Identity & Access Management                                │  │
│  │  • IAM Roles (Cluster, Node, Admin)  • Least Privilege Policies     │  │
│  │  • OIDC Provider for Pod IAM          • Cross-Account Roles          │  │
│  │  • Service Accounts                   • MFA Enforcement              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Layer 3: Data Encryption                                             │  │
│  │  • KMS for EKS Secrets            • S3 Bucket Encryption             │  │
│  │  • EBS Volume Encryption          • TLS for All Traffic              │  │
│  │  • DynamoDB Encryption            • Encrypted Backups                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Layer 4: Monitoring & Logging                                        │  │
│  │  • CloudWatch Logs                • VPC Flow Logs                    │  │
│  │  • EKS Control Plane Logs         • CloudTrail (API Audit)           │  │
│  │  • Container Insights             • Resource Tagging                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Terraform State Management

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    Terraform State Backend Architecture                     │
│                                                                              │
│  Developer Workstation                                                       │
│  ┌──────────────────┐                                                        │
│  │  Terraform CLI   │                                                        │
│  └────────┬─────────┘                                                        │
│           │                                                                  │
│           ├─────────────────┐                                                │
│           │                 │                                                │
│           ▼                 ▼                                                │
│  ┌────────────────┐  ┌────────────────┐                                    │
│  │ S3 Bucket      │  │ DynamoDB Table │                                    │
│  │ (State File)   │  │ (State Lock)   │                                    │
│  │                │  │                │                                    │
│  │ • Versioning   │  │ • LockID key   │                                    │
│  │ • Encryption   │  │ • TTL disabled │                                    │
│  │ • Logging      │  │ • Encryption   │                                    │
│  │ • Lifecycle    │  │ • Point-in-time│                                    │
│  │   policies     │  │   recovery     │                                    │
│  └────────────────┘  └────────────────┘                                    │
│                                                                              │
│  Benefits:                                                                   │
│  ✓ Concurrent access prevention      ✓ State history & versioning          │
│  ✓ Encryption at rest & in transit   ✓ Multi-user collaboration            │
│  ✓ Automatic backups                 ✓ Audit trail via CloudTrail          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## EKS Cluster Components

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        EKS Cluster Architecture                             │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Control Plane (Managed by AWS)                    │  │
│  │                                                                        │  │
│  │  ┌───────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │  │
│  │  │    API    │  │  Controller  │  │ Scheduler │  │     etcd     │  │  │
│  │  │  Server   │  │   Manager    │  │           │  │  (encrypted) │  │  │
│  │  └─────┬─────┘  └──────┬───────┘  └─────┬─────┘  └──────────────┘  │  │
│  │        │               │                 │                           │  │
│  └────────┼───────────────┼─────────────────┼───────────────────────────┘  │
│           │               │                 │                              │
│           ▼               ▼                 ▼                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Data Plane (Worker Nodes)                     │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │  │
│  │  │  Node Group 1   │  │  Node Group 2   │  │  Node Group 3   │     │  │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │     │  │
│  │  │  │  kubelet  │  │  │  │  kubelet  │  │  │  │  kubelet  │  │     │  │
│  │  │  ├───────────┤  │  │  ├───────────┤  │  │  ├───────────┤  │     │  │
│  │  │  │kube-proxy │  │  │  │kube-proxy │  │  │  │kube-proxy │  │     │  │
│  │  │  ├───────────┤  │  │  ├───────────┤  │  │  ├───────────┤  │     │  │
│  │  │  │  VPC CNI  │  │  │  │  VPC CNI  │  │  │  │  VPC CNI  │  │     │  │
│  │  │  ├───────────┤  │  │  ├───────────┤  │  │  ├───────────┤  │     │  │
│  │  │  │  Pods...  │  │  │  │  Pods...  │  │  │  │  Pods...  │  │     │  │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │     │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         EKS Add-ons                                   │  │
│  │  • VPC CNI (Networking)       • CoreDNS (DNS)                        │  │
│  │  • kube-proxy (Networking)    • EBS CSI (Storage)                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## IAM Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         IAM Roles & Policies                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ EKS Cluster Role                                                      │  │
│  │  • Trust Policy: eks.amazonaws.com                                   │  │
│  │  • Managed Policies:                                                 │  │
│  │    - AmazonEKSClusterPolicy                                          │  │
│  │    - AmazonEKSVPCResourceController                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ EKS Node Role                                                         │  │
│  │  • Trust Policy: ec2.amazonaws.com                                   │  │
│  │  • Managed Policies:                                                 │  │
│  │    - AmazonEKSWorkerNodePolicy                                       │  │
│  │    - AmazonEKS_CNI_Policy                                            │  │
│  │    - AmazonEC2ContainerRegistryReadOnly                              │  │
│  │  • Custom Policies:                                                  │  │
│  │    - CloudWatch Logs                                                 │  │
│  │    - EBS CSI Driver                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ EKS Admin Role                                                        │  │
│  │  • Trust Policy: Account root                                        │  │
│  │  • Custom Policies:                                                  │  │
│  │    - Full EKS access                                                 │  │
│  │    - kubectl permissions                                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ OIDC Provider                                                         │  │
│  │  • Enables IAM roles for service accounts (IRSA)                     │  │
│  │  • Pod-level IAM permissions                                         │  │
│  │  • Eliminates need for node-level permissions                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### User Request Flow

```
User → Internet → Internet Gateway → Public Subnet → ALB/NLB 
→ Private Subnet → EKS Worker Nodes → Pods → Application
```

### Pod Egress Flow

```
Pod → VPC CNI → Private Subnet → NAT Gateway 
→ Public Subnet → Internet Gateway → Internet
```

### Logging Flow

```
EKS Control Plane → CloudWatch Logs Group
VPC → Flow Logs → CloudWatch Logs Group
Applications → Container Logs → CloudWatch Logs Group
```

## Scalability Features

### Horizontal Scaling
- **Node Auto-Scaling**: Configurable min/max nodes (2-10)
- **Pod Auto-Scaling**: Horizontal Pod Autoscaler (HPA) support
- **Cluster Auto-Scaler**: Automatic node provisioning based on demand

### Vertical Scaling
- **Instance Types**: Configurable per environment
  - Dev: t3.medium (2 vCPU, 4GB RAM)
  - Staging: t3.large (2 vCPU, 8GB RAM)
  - Prod: t3.xlarge (4 vCPU, 16GB RAM)

## High Availability

### Multi-AZ Deployment
- Control Plane: Automatically distributed across 3 AZs by AWS
- Worker Nodes: Distributed across 3 AZs
- NAT Gateways: One per AZ (staging/prod)
- Data Stores: Multi-AZ by default

### Failure Recovery
- Node failures: Auto-replacement by node group
- AZ failure: Traffic automatically routed to healthy AZs
- Control plane: Managed by AWS with SLA guarantee

## Cost Optimization

### Per Environment

**Development** (~$300/month)
- Single NAT Gateway
- Smaller instances (t3.medium)
- Fewer nodes (2-4)
- On-demand pricing

**Staging** (~$600/month)
- Multi-AZ NAT Gateways
- Medium instances (t3.large)
- Moderate nodes (3-6)
- On-demand pricing

**Production** (~$1,200/month base)
- Multi-AZ NAT Gateways
- Large instances (t3.xlarge)
- More nodes (5-10)
- Reserved Instances recommended

### Cost Reduction Strategies
- Use Reserved Instances for production (30-70% savings)
- Use Spot Instances for non-critical workloads (50-90% savings)
- Implement cluster autoscaler to scale down during low usage
- Right-size based on actual metrics
- Use Savings Plans for flexible compute

## Network Flow Details

### Inbound Traffic
```
Internet → IGW → Public Subnet → Load Balancer 
→ Private Subnet → Security Group → Pods
```

### Outbound Traffic
```
Pods → Security Group → Private Subnet → NAT Gateway 
→ Public Subnet → IGW → Internet
```

### Internal Traffic
```
Pod A → VPC CNI → Internal Routing → Pod B
(Traffic never leaves VPC)
```

## Monitoring Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    CloudWatch Monitoring                            │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │ Control Plane    │  │  VPC Flow Logs   │  │ Application     │  │
│  │ Logs             │  │                  │  │ Logs            │  │
│  │ • API            │  │ • Accept/Reject  │  │ • Container     │  │
│  │ • Audit          │  │ • Source/Dest    │  │   stdout/stderr │  │
│  │ • Authenticator  │  │ • Protocol/Port  │  │ • Application   │  │
│  │ • Controller     │  │ • Bytes/Packets  │  │   logs          │  │
│  │ • Scheduler      │  │                  │  │                 │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     CloudWatch Metrics                        │  │
│  │  • CPU Utilization    • Memory Usage      • Network I/O      │  │
│  │  • Disk I/O          • Pod Count         • Node Health       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     CloudWatch Alarms                         │  │
│  │  • High CPU/Memory    • Node failures     • Pod crashes      │  │
│  │  • API errors         • Network issues    • Cost thresholds  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Terraform Module Relationships

```
main.tf
  │
  ├─→ module.s3_backend
  │     └─→ S3 Bucket (State)
  │     └─→ DynamoDB Table (Locking)
  │
  ├─→ module.vpc
  │     └─→ VPC, Subnets, NAT, IGW, Routes
  │
  ├─→ module.iam
  │     └─→ EKS Cluster Role
  │     └─→ EKS Node Role
  │     └─→ EKS Admin Role
  │
  └─→ module.eks (depends on vpc, iam)
        └─→ EKS Cluster
        └─→ Node Groups
        └─→ Add-ons
        └─→ OIDC Provider
```

## Summary

This architecture provides:

✅ **Secure**: Multi-layer security with encryption, IAM, and network isolation  
✅ **Scalable**: Auto-scaling at cluster and pod level  
✅ **Highly Available**: Multi-AZ deployment with redundancy  
✅ **Cost-Optimized**: Environment-specific sizing and optimization options  
✅ **Production-Ready**: Battle-tested AWS services with managed control plane  
✅ **Observable**: Comprehensive logging and monitoring with CloudWatch  
✅ **Maintainable**: Infrastructure as Code with modular Terraform design  

---

**Last Updated**: 2025-10-14 | **Phase**: Phase 1 Foundation
