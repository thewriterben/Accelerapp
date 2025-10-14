"""
Tests for Phase 2 core services infrastructure.
"""

import pytest
from accelerapp.infrastructure import (
    CoreServicesManager,
    RDSAuroraConfig,
    RedisClusterConfig,
    S3BucketConfig,
    CloudFrontConfig,
    SecretsManagerConfig,
)


class TestRDSAuroraConfiguration:
    """Tests for RDS Aurora configuration."""
    
    def test_rds_config_creation(self):
        """Test RDS Aurora configuration creation."""
        config = RDSAuroraConfig(
            cluster_name="test-cluster",
            engine="aurora-postgresql",
            database_name="testdb",
        )
        
        assert config.cluster_name == "test-cluster"
        assert config.engine == "aurora-postgresql"
        assert config.database_name == "testdb"
        assert config.multi_az is True
        assert config.storage_encrypted is True
    
    def test_rds_template_generation(self):
        """Test RDS Aurora CloudFormation template generation."""
        manager = CoreServicesManager()
        config = RDSAuroraConfig(
            cluster_name="test-cluster",
            database_name="testdb",
        )
        
        template = manager.generate_rds_aurora_template(config)
        
        assert "AWSTemplateFormatVersion" in template
        assert template["AWSTemplateFormatVersion"] == "2010-09-09"
        assert "Resources" in template
        assert "DBCluster" in template["Resources"]
        assert "DBInstance1" in template["Resources"]
        assert "DBInstance2" in template["Resources"]
        assert "DBSecurityGroup" in template["Resources"]
        assert "DBEncryptionKey" in template["Resources"]
    
    def test_rds_template_parameters(self):
        """Test RDS template has required parameters."""
        manager = CoreServicesManager()
        config = RDSAuroraConfig(cluster_name="test-cluster")
        
        template = manager.generate_rds_aurora_template(config)
        
        assert "Parameters" in template
        assert "VpcId" in template["Parameters"]
        assert "PrivateSubnetIds" in template["Parameters"]
        assert "AppSecurityGroup" in template["Parameters"]
        assert "DBMasterPassword" in template["Parameters"]
    
    def test_rds_template_outputs(self):
        """Test RDS template has required outputs."""
        manager = CoreServicesManager()
        config = RDSAuroraConfig(cluster_name="test-cluster")
        
        template = manager.generate_rds_aurora_template(config)
        
        assert "Outputs" in template
        assert "DBClusterEndpoint" in template["Outputs"]
        assert "DBClusterReadEndpoint" in template["Outputs"]
        assert "DBClusterPort" in template["Outputs"]
    
    def test_rds_security_settings(self):
        """Test RDS template has proper security settings."""
        manager = CoreServicesManager()
        config = RDSAuroraConfig(
            cluster_name="test-cluster",
            storage_encrypted=True,
            deletion_protection=True,
        )
        
        template = manager.generate_rds_aurora_template(config)
        cluster_props = template["Resources"]["DBCluster"]["Properties"]
        
        assert cluster_props["StorageEncrypted"] is True
        assert cluster_props["DeletionProtection"] is True
        assert "KmsKeyId" in cluster_props


class TestRedisClusterConfiguration:
    """Tests for Redis cluster configuration."""
    
    def test_redis_config_creation(self):
        """Test Redis cluster configuration creation."""
        config = RedisClusterConfig(
            cluster_name="test-cache",
            node_type="cache.t3.micro",
            num_cache_nodes=2,
        )
        
        assert config.cluster_name == "test-cache"
        assert config.node_type == "cache.t3.micro"
        assert config.num_cache_nodes == 2
        assert config.automatic_failover_enabled is True
        assert config.multi_az_enabled is True
    
    def test_redis_template_generation(self):
        """Test Redis CloudFormation template generation."""
        manager = CoreServicesManager()
        config = RedisClusterConfig(cluster_name="test-cache")
        
        template = manager.generate_redis_cluster_template(config)
        
        assert "AWSTemplateFormatVersion" in template
        assert "Resources" in template
        assert "CacheReplicationGroup" in template["Resources"]
        assert "CacheSubnetGroup" in template["Resources"]
        assert "CacheParameterGroup" in template["Resources"]
        assert "CacheSecurityGroup" in template["Resources"]
    
    def test_redis_template_encryption(self):
        """Test Redis template has encryption enabled."""
        manager = CoreServicesManager()
        config = RedisClusterConfig(
            cluster_name="test-cache",
            at_rest_encryption_enabled=True,
            transit_encryption_enabled=True,
        )
        
        template = manager.generate_redis_cluster_template(config)
        cache_props = template["Resources"]["CacheReplicationGroup"]["Properties"]
        
        assert cache_props["AtRestEncryptionEnabled"] is True
        assert cache_props["TransitEncryptionEnabled"] is True
    
    def test_redis_template_outputs(self):
        """Test Redis template has required outputs."""
        manager = CoreServicesManager()
        config = RedisClusterConfig(cluster_name="test-cache")
        
        template = manager.generate_redis_cluster_template(config)
        
        assert "Outputs" in template
        assert "CacheEndpoint" in template["Outputs"]
        assert "CachePort" in template["Outputs"]
        assert "CacheReaderEndpoint" in template["Outputs"]


class TestS3BucketConfiguration:
    """Tests for S3 bucket configuration."""
    
    def test_s3_config_creation(self):
        """Test S3 bucket configuration creation."""
        config = S3BucketConfig(
            bucket_name="test-bucket",
            versioning_enabled=True,
            encryption_enabled=True,
        )
        
        assert config.bucket_name == "test-bucket"
        assert config.versioning_enabled is True
        assert config.encryption_enabled is True
        assert config.public_access_block is True
    
    def test_s3_template_generation(self):
        """Test S3 CloudFormation template generation."""
        manager = CoreServicesManager()
        config = S3BucketConfig(bucket_name="test-bucket")
        
        template = manager.generate_s3_bucket_template(config)
        
        assert "AWSTemplateFormatVersion" in template
        assert "Resources" in template
        assert "S3Bucket" in template["Resources"]
        assert "BucketPolicy" in template["Resources"]
    
    def test_s3_template_security(self):
        """Test S3 template has proper security settings."""
        manager = CoreServicesManager()
        config = S3BucketConfig(
            bucket_name="test-bucket",
            encryption_enabled=True,
            public_access_block=True,
        )
        
        template = manager.generate_s3_bucket_template(config)
        bucket_props = template["Resources"]["S3Bucket"]["Properties"]
        
        assert "BucketEncryption" in bucket_props
        assert "PublicAccessBlockConfiguration" in bucket_props
        
        public_access = bucket_props["PublicAccessBlockConfiguration"]
        assert public_access["BlockPublicAcls"] is True
        assert public_access["BlockPublicPolicy"] is True
    
    def test_s3_template_lifecycle(self):
        """Test S3 template with lifecycle rules."""
        manager = CoreServicesManager()
        config = S3BucketConfig(
            bucket_name="test-bucket",
            lifecycle_rules=[
                {
                    "Id": "DeleteOldVersions",
                    "Status": "Enabled",
                    "NoncurrentVersionExpirationInDays": 90,
                }
            ],
        )
        
        template = manager.generate_s3_bucket_template(config)
        bucket_props = template["Resources"]["S3Bucket"]["Properties"]
        
        assert "LifecycleConfiguration" in bucket_props
        assert len(bucket_props["LifecycleConfiguration"]["Rules"]) == 1
    
    def test_s3_template_cors(self):
        """Test S3 template with CORS rules."""
        manager = CoreServicesManager()
        config = S3BucketConfig(
            bucket_name="test-bucket",
            cors_rules=[
                {
                    "AllowedOrigins": ["*"],
                    "AllowedMethods": ["GET", "HEAD"],
                    "AllowedHeaders": ["*"],
                }
            ],
        )
        
        template = manager.generate_s3_bucket_template(config)
        bucket_props = template["Resources"]["S3Bucket"]["Properties"]
        
        assert "CorsConfiguration" in bucket_props
        assert len(bucket_props["CorsConfiguration"]["CorsRules"]) == 1
    
    def test_s3_template_outputs(self):
        """Test S3 template has required outputs."""
        manager = CoreServicesManager()
        config = S3BucketConfig(bucket_name="test-bucket")
        
        template = manager.generate_s3_bucket_template(config)
        
        assert "Outputs" in template
        assert "BucketName" in template["Outputs"]
        assert "BucketArn" in template["Outputs"]
        assert "BucketDomainName" in template["Outputs"]


class TestCloudFrontConfiguration:
    """Tests for CloudFront configuration."""
    
    def test_cloudfront_config_creation(self):
        """Test CloudFront configuration creation."""
        config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test-bucket.s3.amazonaws.com",
        )
        
        assert config.distribution_name == "test-cdn"
        assert config.origin_domain_name == "test-bucket.s3.amazonaws.com"
        assert config.enabled is True
        assert config.compress is True
    
    def test_cloudfront_template_generation(self):
        """Test CloudFront CloudFormation template generation."""
        manager = CoreServicesManager()
        config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test-bucket.s3.amazonaws.com",
        )
        
        template = manager.generate_cloudfront_template(config)
        
        assert "AWSTemplateFormatVersion" in template
        assert "Resources" in template
        assert "CloudFrontDistribution" in template["Resources"]
        assert "CloudFrontOriginAccessIdentity" in template["Resources"]
    
    def test_cloudfront_template_ssl(self):
        """Test CloudFront template has SSL/TLS configuration."""
        manager = CoreServicesManager()
        config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test-bucket.s3.amazonaws.com",
            viewer_protocol_policy="redirect-to-https",
        )
        
        template = manager.generate_cloudfront_template(config)
        dist_config = template["Resources"]["CloudFrontDistribution"]["Properties"]["DistributionConfig"]
        
        assert dist_config["DefaultCacheBehavior"]["ViewerProtocolPolicy"] == "redirect-to-https"
        assert "ViewerCertificate" in dist_config
    
    def test_cloudfront_template_caching(self):
        """Test CloudFront template has caching configuration."""
        manager = CoreServicesManager()
        config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test-bucket.s3.amazonaws.com",
            min_ttl=0,
            default_ttl=86400,
            max_ttl=31536000,
        )
        
        template = manager.generate_cloudfront_template(config)
        cache_behavior = template["Resources"]["CloudFrontDistribution"]["Properties"]["DistributionConfig"]["DefaultCacheBehavior"]
        
        assert cache_behavior["MinTTL"] == 0
        assert cache_behavior["DefaultTTL"] == 86400
        assert cache_behavior["MaxTTL"] == 31536000
    
    def test_cloudfront_template_outputs(self):
        """Test CloudFront template has required outputs."""
        manager = CoreServicesManager()
        config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test-bucket.s3.amazonaws.com",
        )
        
        template = manager.generate_cloudfront_template(config)
        
        assert "Outputs" in template
        assert "DistributionId" in template["Outputs"]
        assert "DistributionDomainName" in template["Outputs"]


class TestSecretsManagerConfiguration:
    """Tests for Secrets Manager configuration."""
    
    def test_secrets_config_creation(self):
        """Test Secrets Manager configuration creation."""
        config = SecretsManagerConfig(
            secret_name="test-secret",
            description="Test secret",
            rotation_enabled=True,
        )
        
        assert config.secret_name == "test-secret"
        assert config.description == "Test secret"
        assert config.rotation_enabled is True
        assert config.rotation_days == 30
    
    def test_secrets_template_generation(self):
        """Test Secrets Manager CloudFormation template generation."""
        manager = CoreServicesManager()
        config = SecretsManagerConfig(
            secret_name="test-secret",
            rotation_enabled=False,
        )
        
        template = manager.generate_secrets_manager_template(config)
        
        assert "AWSTemplateFormatVersion" in template
        assert "Resources" in template
        assert "Secret" in template["Resources"]
    
    def test_secrets_template_rotation(self):
        """Test Secrets Manager template with rotation."""
        manager = CoreServicesManager()
        config = SecretsManagerConfig(
            secret_name="test-secret",
            rotation_enabled=True,
            rotation_days=30,
        )
        
        template = manager.generate_secrets_manager_template(config)
        
        assert "RotationSchedule" in template["Resources"]
        assert "Parameters" in template
        assert "RotationLambdaArn" in template["Parameters"]
    
    def test_secrets_template_without_rotation(self):
        """Test Secrets Manager template without rotation."""
        manager = CoreServicesManager()
        config = SecretsManagerConfig(
            secret_name="test-secret",
            rotation_enabled=False,
        )
        
        template = manager.generate_secrets_manager_template(config)
        
        assert "RotationSchedule" not in template["Resources"]
        assert "Parameters" not in template
    
    def test_secrets_template_outputs(self):
        """Test Secrets Manager template has required outputs."""
        manager = CoreServicesManager()
        config = SecretsManagerConfig(secret_name="test-secret")
        
        template = manager.generate_secrets_manager_template(config)
        
        assert "Outputs" in template
        assert "SecretArn" in template["Outputs"]
        assert "SecretName" in template["Outputs"]


class TestCoreServicesManager:
    """Tests for CoreServicesManager."""
    
    def test_manager_initialization(self):
        """Test CoreServicesManager initialization."""
        manager = CoreServicesManager()
        
        assert manager is not None
        assert len(manager.rds_configs) == 0
        assert len(manager.redis_configs) == 0
        assert len(manager.s3_configs) == 0
        assert len(manager.cloudfront_configs) == 0
        assert len(manager.secrets_configs) == 0
    
    def test_manager_stores_configs(self):
        """Test that manager stores generated configurations."""
        manager = CoreServicesManager()
        
        rds_config = RDSAuroraConfig(cluster_name="test-db")
        manager.generate_rds_aurora_template(rds_config)
        
        redis_config = RedisClusterConfig(cluster_name="test-cache")
        manager.generate_redis_cluster_template(redis_config)
        
        s3_config = S3BucketConfig(bucket_name="test-bucket")
        manager.generate_s3_bucket_template(s3_config)
        
        cloudfront_config = CloudFrontConfig(
            distribution_name="test-cdn",
            origin_domain_name="test.s3.amazonaws.com",
        )
        manager.generate_cloudfront_template(cloudfront_config)
        
        secrets_config = SecretsManagerConfig(secret_name="test-secret")
        manager.generate_secrets_manager_template(secrets_config)
        
        assert len(manager.rds_configs) == 1
        assert len(manager.redis_configs) == 1
        assert len(manager.s3_configs) == 1
        assert len(manager.cloudfront_configs) == 1
        assert len(manager.secrets_configs) == 1
    
    def test_manager_get_all_configs(self):
        """Test getting all configurations from manager."""
        manager = CoreServicesManager()
        
        rds_config = RDSAuroraConfig(cluster_name="test-db")
        manager.generate_rds_aurora_template(rds_config)
        
        all_configs = manager.get_all_configs()
        
        assert "rds" in all_configs
        assert "redis" in all_configs
        assert "s3" in all_configs
        assert "cloudfront" in all_configs
        assert "secrets" in all_configs
        assert "test-db" in all_configs["rds"]


class TestIntegrationScenarios:
    """Integration tests for complete infrastructure scenarios."""
    
    def test_complete_infrastructure_setup(self):
        """Test generating complete infrastructure for production."""
        manager = CoreServicesManager()
        
        # Database
        rds_config = RDSAuroraConfig(
            cluster_name="accelerapp-db",
            database_name="accelerapp",
            multi_az=True,
            storage_encrypted=True,
        )
        rds_template = manager.generate_rds_aurora_template(rds_config)
        assert "DBCluster" in rds_template["Resources"]
        
        # Cache
        redis_config = RedisClusterConfig(
            cluster_name="accelerapp-cache",
            multi_az_enabled=True,
            at_rest_encryption_enabled=True,
        )
        redis_template = manager.generate_redis_cluster_template(redis_config)
        assert "CacheReplicationGroup" in redis_template["Resources"]
        
        # Storage
        s3_config = S3BucketConfig(
            bucket_name="accelerapp-assets",
            versioning_enabled=True,
            encryption_enabled=True,
        )
        s3_template = manager.generate_s3_bucket_template(s3_config)
        assert "S3Bucket" in s3_template["Resources"]
        
        # CDN
        cloudfront_config = CloudFrontConfig(
            distribution_name="accelerapp-cdn",
            origin_domain_name="accelerapp-assets.s3.amazonaws.com",
        )
        cloudfront_template = manager.generate_cloudfront_template(cloudfront_config)
        assert "CloudFrontDistribution" in cloudfront_template["Resources"]
        
        # Secrets
        secrets_config = SecretsManagerConfig(
            secret_name="accelerapp/db/credentials",
            rotation_enabled=True,
        )
        secrets_template = manager.generate_secrets_manager_template(secrets_config)
        assert "Secret" in secrets_template["Resources"]
        
        # Verify all configs are stored
        all_configs = manager.get_all_configs()
        assert len(all_configs["rds"]) == 1
        assert len(all_configs["redis"]) == 1
        assert len(all_configs["s3"]) == 1
        assert len(all_configs["cloudfront"]) == 1
        assert len(all_configs["secrets"]) == 1
