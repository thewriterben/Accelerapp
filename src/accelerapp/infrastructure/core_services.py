"""
Core services infrastructure for Phase 2: Database, Caching, and CDN.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RDSAuroraConfig:
    """Configuration for RDS Aurora database."""
    
    cluster_name: str
    engine: str = "aurora-postgresql"
    engine_version: str = "15.3"
    instance_class: str = "db.r6g.large"
    database_name: str = "accelerapp"
    master_username: str = "admin"
    backup_retention_days: int = 7
    preferred_backup_window: str = "03:00-04:00"
    preferred_maintenance_window: str = "mon:04:00-mon:05:00"
    multi_az: bool = True
    storage_encrypted: bool = True
    deletion_protection: bool = True
    min_capacity: int = 2
    max_capacity: int = 16
    auto_pause: bool = False


@dataclass
class RedisClusterConfig:
    """Configuration for Redis cache cluster."""
    
    cluster_name: str
    node_type: str = "cache.r6g.large"
    num_cache_nodes: int = 2
    engine_version: str = "7.0"
    port: int = 6379
    parameter_group_family: str = "redis7"
    automatic_failover_enabled: bool = True
    multi_az_enabled: bool = True
    at_rest_encryption_enabled: bool = True
    transit_encryption_enabled: bool = True
    snapshot_retention_limit: int = 5
    snapshot_window: str = "03:00-05:00"
    maintenance_window: str = "mon:05:00-mon:07:00"


@dataclass
class S3BucketConfig:
    """Configuration for S3 bucket."""
    
    bucket_name: str
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    lifecycle_rules: List[Dict[str, Any]] = field(default_factory=list)
    cors_rules: List[Dict[str, Any]] = field(default_factory=list)
    public_access_block: bool = True
    replication_enabled: bool = False
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CloudFrontConfig:
    """Configuration for CloudFront CDN."""
    
    distribution_name: str
    origin_domain_name: str
    price_class: str = "PriceClass_100"
    enabled: bool = True
    default_root_object: str = "index.html"
    compress: bool = True
    viewer_protocol_policy: str = "redirect-to-https"
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD", "OPTIONS"])
    cached_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD"])
    min_ttl: int = 0
    default_ttl: int = 86400
    max_ttl: int = 31536000
    ssl_support_method: str = "sni-only"
    minimum_protocol_version: str = "TLSv1.2_2021"


@dataclass
class SecretsManagerConfig:
    """Configuration for AWS Secrets Manager."""
    
    secret_name: str
    description: str = ""
    kms_key_id: Optional[str] = None
    rotation_enabled: bool = True
    rotation_days: int = 30
    tags: Dict[str, str] = field(default_factory=dict)


class CoreServicesManager:
    """
    Manager for Phase 2 core services infrastructure.
    Handles RDS Aurora, Redis, S3, CloudFront, and Secrets Manager.
    """
    
    def __init__(self):
        """Initialize core services manager."""
        self.rds_configs: Dict[str, RDSAuroraConfig] = {}
        self.redis_configs: Dict[str, RedisClusterConfig] = {}
        self.s3_configs: Dict[str, S3BucketConfig] = {}
        self.cloudfront_configs: Dict[str, CloudFrontConfig] = {}
        self.secrets_configs: Dict[str, SecretsManagerConfig] = {}
    
    def generate_rds_aurora_template(self, config: RDSAuroraConfig) -> Dict[str, Any]:
        """
        Generate CloudFormation template for RDS Aurora database.
        
        Args:
            config: RDS Aurora configuration
            
        Returns:
            CloudFormation template as dictionary
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"RDS Aurora PostgreSQL cluster for {config.cluster_name}",
            "Resources": {
                "DBSubnetGroup": {
                    "Type": "AWS::RDS::DBSubnetGroup",
                    "Properties": {
                        "DBSubnetGroupDescription": f"Subnet group for {config.cluster_name}",
                        "SubnetIds": {"Ref": "PrivateSubnetIds"},
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-subnet-group"},
                            {"Key": "Environment", "Value": "production"},
                        ],
                    },
                },
                "DBClusterParameterGroup": {
                    "Type": "AWS::RDS::DBClusterParameterGroup",
                    "Properties": {
                        "Description": f"Cluster parameter group for {config.cluster_name}",
                        "Family": f"{config.engine}-{config.engine_version.split('.')[0]}",
                        "Parameters": {
                            "shared_preload_libraries": "pg_stat_statements",
                            "log_statement": "all",
                            "log_min_duration_statement": "1000",
                        },
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-cluster-params"},
                        ],
                    },
                },
                "DBCluster": {
                    "Type": "AWS::RDS::DBCluster",
                    "Properties": {
                        "Engine": config.engine,
                        "EngineVersion": config.engine_version,
                        "DatabaseName": config.database_name,
                        "MasterUsername": config.master_username,
                        "MasterUserPassword": {"Ref": "DBMasterPassword"},
                        "DBSubnetGroupName": {"Ref": "DBSubnetGroup"},
                        "VpcSecurityGroupIds": [{"Ref": "DBSecurityGroup"}],
                        "BackupRetentionPeriod": config.backup_retention_days,
                        "PreferredBackupWindow": config.preferred_backup_window,
                        "PreferredMaintenanceWindow": config.preferred_maintenance_window,
                        "StorageEncrypted": config.storage_encrypted,
                        "KmsKeyId": {"Ref": "DBEncryptionKey"},
                        "DeletionProtection": config.deletion_protection,
                        "DBClusterParameterGroupName": {"Ref": "DBClusterParameterGroup"},
                        "EnableCloudwatchLogsExports": ["postgresql"],
                        "Tags": [
                            {"Key": "Name", "Value": config.cluster_name},
                            {"Key": "Environment", "Value": "production"},
                            {"Key": "ManagedBy", "Value": "accelerapp"},
                        ],
                    },
                },
                "DBInstance1": {
                    "Type": "AWS::RDS::DBInstance",
                    "Properties": {
                        "DBClusterIdentifier": {"Ref": "DBCluster"},
                        "DBInstanceClass": config.instance_class,
                        "Engine": config.engine,
                        "PubliclyAccessible": False,
                        "EnablePerformanceInsights": True,
                        "PerformanceInsightsRetentionPeriod": 7,
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-instance-1"},
                        ],
                    },
                },
                "DBInstance2": {
                    "Type": "AWS::RDS::DBInstance",
                    "Properties": {
                        "DBClusterIdentifier": {"Ref": "DBCluster"},
                        "DBInstanceClass": config.instance_class,
                        "Engine": config.engine,
                        "PubliclyAccessible": False,
                        "EnablePerformanceInsights": True,
                        "PerformanceInsightsRetentionPeriod": 7,
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-instance-2"},
                        ],
                    },
                },
                "DBSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": f"Security group for {config.cluster_name}",
                        "VpcId": {"Ref": "VpcId"},
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 5432,
                                "ToPort": 5432,
                                "SourceSecurityGroupId": {"Ref": "AppSecurityGroup"},
                            }
                        ],
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-sg"},
                        ],
                    },
                },
                "DBEncryptionKey": {
                    "Type": "AWS::KMS::Key",
                    "Properties": {
                        "Description": f"Encryption key for {config.cluster_name}",
                        "KeyPolicy": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "Enable IAM User Permissions",
                                    "Effect": "Allow",
                                    "Principal": {"AWS": {"Fn::Sub": "arn:aws:iam::${AWS::AccountId}:root"}},
                                    "Action": "kms:*",
                                    "Resource": "*",
                                }
                            ],
                        },
                    },
                },
            },
            "Parameters": {
                "VpcId": {
                    "Type": "AWS::EC2::VPC::Id",
                    "Description": "VPC ID for the database",
                },
                "PrivateSubnetIds": {
                    "Type": "List<AWS::EC2::Subnet::Id>",
                    "Description": "Private subnet IDs for the database",
                },
                "AppSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup::Id",
                    "Description": "Security group of application instances",
                },
                "DBMasterPassword": {
                    "Type": "String",
                    "NoEcho": True,
                    "Description": "Master password for the database",
                    "MinLength": 8,
                },
            },
            "Outputs": {
                "DBClusterEndpoint": {
                    "Description": "Database cluster endpoint",
                    "Value": {"Fn::GetAtt": ["DBCluster", "Endpoint.Address"]},
                    "Export": {"Name": f"{config.cluster_name}-endpoint"},
                },
                "DBClusterReadEndpoint": {
                    "Description": "Database cluster read endpoint",
                    "Value": {"Fn::GetAtt": ["DBCluster", "ReadEndpoint.Address"]},
                    "Export": {"Name": f"{config.cluster_name}-read-endpoint"},
                },
                "DBClusterPort": {
                    "Description": "Database port",
                    "Value": {"Fn::GetAtt": ["DBCluster", "Endpoint.Port"]},
                },
            },
        }
        
        self.rds_configs[config.cluster_name] = config
        return template
    
    def generate_redis_cluster_template(self, config: RedisClusterConfig) -> Dict[str, Any]:
        """
        Generate CloudFormation template for Redis cache cluster.
        
        Args:
            config: Redis cluster configuration
            
        Returns:
            CloudFormation template as dictionary
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"ElastiCache Redis cluster for {config.cluster_name}",
            "Resources": {
                "CacheSubnetGroup": {
                    "Type": "AWS::ElastiCache::SubnetGroup",
                    "Properties": {
                        "Description": f"Subnet group for {config.cluster_name}",
                        "SubnetIds": {"Ref": "PrivateSubnetIds"},
                        "CacheSubnetGroupName": f"{config.cluster_name}-subnet-group",
                    },
                },
                "CacheParameterGroup": {
                    "Type": "AWS::ElastiCache::ParameterGroup",
                    "Properties": {
                        "CacheParameterGroupFamily": config.parameter_group_family,
                        "Description": f"Parameter group for {config.cluster_name}",
                        "Properties": {
                            "maxmemory-policy": "allkeys-lru",
                            "timeout": "300",
                        },
                    },
                },
                "CacheReplicationGroup": {
                    "Type": "AWS::ElastiCache::ReplicationGroup",
                    "Properties": {
                        "ReplicationGroupId": config.cluster_name,
                        "ReplicationGroupDescription": f"Redis cluster for Accelerapp",
                        "Engine": "redis",
                        "EngineVersion": config.engine_version,
                        "CacheNodeType": config.node_type,
                        "NumCacheClusters": config.num_cache_nodes,
                        "Port": config.port,
                        "CacheParameterGroupName": {"Ref": "CacheParameterGroup"},
                        "CacheSubnetGroupName": {"Ref": "CacheSubnetGroup"},
                        "SecurityGroupIds": [{"Ref": "CacheSecurityGroup"}],
                        "AutomaticFailoverEnabled": config.automatic_failover_enabled,
                        "MultiAZEnabled": config.multi_az_enabled,
                        "AtRestEncryptionEnabled": config.at_rest_encryption_enabled,
                        "TransitEncryptionEnabled": config.transit_encryption_enabled,
                        "SnapshotRetentionLimit": config.snapshot_retention_limit,
                        "SnapshotWindow": config.snapshot_window,
                        "PreferredMaintenanceWindow": config.maintenance_window,
                        "AutoMinorVersionUpgrade": True,
                        "Tags": [
                            {"Key": "Name", "Value": config.cluster_name},
                            {"Key": "Environment", "Value": "production"},
                            {"Key": "ManagedBy", "Value": "accelerapp"},
                        ],
                    },
                },
                "CacheSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": f"Security group for {config.cluster_name}",
                        "VpcId": {"Ref": "VpcId"},
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": config.port,
                                "ToPort": config.port,
                                "SourceSecurityGroupId": {"Ref": "AppSecurityGroup"},
                            }
                        ],
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.cluster_name}-sg"},
                        ],
                    },
                },
            },
            "Parameters": {
                "VpcId": {
                    "Type": "AWS::EC2::VPC::Id",
                    "Description": "VPC ID for the cache cluster",
                },
                "PrivateSubnetIds": {
                    "Type": "List<AWS::EC2::Subnet::Id>",
                    "Description": "Private subnet IDs for the cache cluster",
                },
                "AppSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup::Id",
                    "Description": "Security group of application instances",
                },
            },
            "Outputs": {
                "CacheEndpoint": {
                    "Description": "Cache cluster primary endpoint",
                    "Value": {"Fn::GetAtt": ["CacheReplicationGroup", "PrimaryEndPoint.Address"]},
                    "Export": {"Name": f"{config.cluster_name}-endpoint"},
                },
                "CachePort": {
                    "Description": "Cache cluster port",
                    "Value": {"Fn::GetAtt": ["CacheReplicationGroup", "PrimaryEndPoint.Port"]},
                },
                "CacheReaderEndpoint": {
                    "Description": "Cache cluster reader endpoint",
                    "Value": {"Fn::GetAtt": ["CacheReplicationGroup", "ReaderEndPoint.Address"]},
                    "Export": {"Name": f"{config.cluster_name}-reader-endpoint"},
                },
            },
        }
        
        self.redis_configs[config.cluster_name] = config
        return template
    
    def generate_s3_bucket_template(self, config: S3BucketConfig) -> Dict[str, Any]:
        """
        Generate CloudFormation template for S3 bucket.
        
        Args:
            config: S3 bucket configuration
            
        Returns:
            CloudFormation template as dictionary
        """
        bucket_properties: Dict[str, Any] = {
            "BucketName": config.bucket_name,
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [
                    {
                        "ServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            } if config.encryption_enabled else None,
            "VersioningConfiguration": {
                "Status": "Enabled" if config.versioning_enabled else "Suspended"
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            } if config.public_access_block else None,
            "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()] + [
                {"Key": "ManagedBy", "Value": "accelerapp"},
            ],
        }
        
        # Remove None values
        bucket_properties = {k: v for k, v in bucket_properties.items() if v is not None}
        
        if config.lifecycle_rules:
            bucket_properties["LifecycleConfiguration"] = {
                "Rules": config.lifecycle_rules
            }
        
        if config.cors_rules:
            bucket_properties["CorsConfiguration"] = {
                "CorsRules": config.cors_rules
            }
        
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"S3 bucket for {config.bucket_name}",
            "Resources": {
                "S3Bucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": bucket_properties,
                },
                "BucketPolicy": {
                    "Type": "AWS::S3::BucketPolicy",
                    "Properties": {
                        "Bucket": {"Ref": "S3Bucket"},
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "DenyInsecureConnections",
                                    "Effect": "Deny",
                                    "Principal": "*",
                                    "Action": "s3:*",
                                    "Resource": [
                                        {"Fn::GetAtt": ["S3Bucket", "Arn"]},
                                        {"Fn::Join": ["", [{"Fn::GetAtt": ["S3Bucket", "Arn"]}, "/*"]]},
                                    ],
                                    "Condition": {
                                        "Bool": {"aws:SecureTransport": "false"}
                                    },
                                }
                            ],
                        },
                    },
                },
            },
            "Outputs": {
                "BucketName": {
                    "Description": "Name of the S3 bucket",
                    "Value": {"Ref": "S3Bucket"},
                    "Export": {"Name": f"{config.bucket_name}-name"},
                },
                "BucketArn": {
                    "Description": "ARN of the S3 bucket",
                    "Value": {"Fn::GetAtt": ["S3Bucket", "Arn"]},
                    "Export": {"Name": f"{config.bucket_name}-arn"},
                },
                "BucketDomainName": {
                    "Description": "Domain name of the S3 bucket",
                    "Value": {"Fn::GetAtt": ["S3Bucket", "DomainName"]},
                },
            },
        }
        
        self.s3_configs[config.bucket_name] = config
        return template
    
    def generate_cloudfront_template(self, config: CloudFrontConfig) -> Dict[str, Any]:
        """
        Generate CloudFormation template for CloudFront distribution.
        
        Args:
            config: CloudFront configuration
            
        Returns:
            CloudFormation template as dictionary
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"CloudFront distribution for {config.distribution_name}",
            "Resources": {
                "CloudFrontDistribution": {
                    "Type": "AWS::CloudFront::Distribution",
                    "Properties": {
                        "DistributionConfig": {
                            "Comment": config.distribution_name,
                            "Enabled": config.enabled,
                            "DefaultRootObject": config.default_root_object,
                            "PriceClass": config.price_class,
                            "Origins": [
                                {
                                    "Id": "S3Origin",
                                    "DomainName": config.origin_domain_name,
                                    "S3OriginConfig": {
                                        "OriginAccessIdentity": {
                                            "Fn::Sub": "origin-access-identity/cloudfront/${CloudFrontOriginAccessIdentity}"
                                        }
                                    },
                                }
                            ],
                            "DefaultCacheBehavior": {
                                "TargetOriginId": "S3Origin",
                                "ViewerProtocolPolicy": config.viewer_protocol_policy,
                                "AllowedMethods": config.allowed_methods,
                                "CachedMethods": config.cached_methods,
                                "Compress": config.compress,
                                "ForwardedValues": {
                                    "QueryString": False,
                                    "Cookies": {"Forward": "none"},
                                },
                                "MinTTL": config.min_ttl,
                                "DefaultTTL": config.default_ttl,
                                "MaxTTL": config.max_ttl,
                            },
                            "ViewerCertificate": {
                                "CloudFrontDefaultCertificate": True,
                                "MinimumProtocolVersion": config.minimum_protocol_version,
                                "SslSupportMethod": config.ssl_support_method,
                            },
                        },
                        "Tags": [
                            {"Key": "Name", "Value": config.distribution_name},
                            {"Key": "Environment", "Value": "production"},
                            {"Key": "ManagedBy", "Value": "accelerapp"},
                        ],
                    },
                },
                "CloudFrontOriginAccessIdentity": {
                    "Type": "AWS::CloudFront::CloudFrontOriginAccessIdentity",
                    "Properties": {
                        "CloudFrontOriginAccessIdentityConfig": {
                            "Comment": f"OAI for {config.distribution_name}",
                        }
                    },
                },
            },
            "Outputs": {
                "DistributionId": {
                    "Description": "CloudFront distribution ID",
                    "Value": {"Ref": "CloudFrontDistribution"},
                    "Export": {"Name": f"{config.distribution_name}-id"},
                },
                "DistributionDomainName": {
                    "Description": "CloudFront distribution domain name",
                    "Value": {"Fn::GetAtt": ["CloudFrontDistribution", "DomainName"]},
                    "Export": {"Name": f"{config.distribution_name}-domain"},
                },
            },
        }
        
        self.cloudfront_configs[config.distribution_name] = config
        return template
    
    def generate_secrets_manager_template(self, config: SecretsManagerConfig) -> Dict[str, Any]:
        """
        Generate CloudFormation template for AWS Secrets Manager.
        
        Args:
            config: Secrets Manager configuration
            
        Returns:
            CloudFormation template as dictionary
        """
        secret_properties: Dict[str, Any] = {
            "Name": config.secret_name,
            "Description": config.description or f"Secrets for {config.secret_name}",
            "Tags": [{"Key": k, "Value": v} for k, v in config.tags.items()] + [
                {"Key": "ManagedBy", "Value": "accelerapp"},
            ],
        }
        
        if config.kms_key_id:
            secret_properties["KmsKeyId"] = config.kms_key_id
        
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"Secrets Manager secret for {config.secret_name}",
            "Resources": {
                "Secret": {
                    "Type": "AWS::SecretsManager::Secret",
                    "Properties": secret_properties,
                },
            },
            "Outputs": {
                "SecretArn": {
                    "Description": "ARN of the secret",
                    "Value": {"Ref": "Secret"},
                    "Export": {"Name": f"{config.secret_name}-arn"},
                },
                "SecretName": {
                    "Description": "Name of the secret",
                    "Value": config.secret_name,
                },
            },
        }
        
        if config.rotation_enabled:
            template["Resources"]["RotationSchedule"] = {
                "Type": "AWS::SecretsManager::RotationSchedule",
                "Properties": {
                    "SecretId": {"Ref": "Secret"},
                    "RotationLambdaARN": {"Ref": "RotationLambdaArn"},
                    "RotationRules": {
                        "AutomaticallyAfterDays": config.rotation_days,
                    },
                },
            }
            
            template["Parameters"] = {
                "RotationLambdaArn": {
                    "Type": "String",
                    "Description": "ARN of the rotation Lambda function",
                }
            }
        
        self.secrets_configs[config.secret_name] = config
        return template
    
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all stored configurations.
        
        Returns:
            Dictionary of all configurations by service type
        """
        return {
            "rds": self.rds_configs,
            "redis": self.redis_configs,
            "s3": self.s3_configs,
            "cloudfront": self.cloudfront_configs,
            "secrets": self.secrets_configs,
        }
