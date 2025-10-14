"""
Example: Using Accelerapp Infrastructure Module

This example demonstrates how to programmatically generate CloudFormation
templates for Phase 2 core services infrastructure.
"""

from accelerapp.infrastructure import (
    CoreServicesManager,
    RDSAuroraConfig,
    RedisClusterConfig,
    S3BucketConfig,
    CloudFrontConfig,
    SecretsManagerConfig,
)
import json


def example_basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("Basic Infrastructure Template Generation")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Generate RDS Aurora template
    rds_config = RDSAuroraConfig(
        cluster_name="myapp-db",
        database_name="myapp",
        instance_class="db.r6g.large",
    )
    rds_template = manager.generate_rds_aurora_template(rds_config)
    print(f"\n✓ Generated RDS Aurora template for '{rds_config.cluster_name}'")
    print(f"  Resources: {len(rds_template['Resources'])} components")
    
    # Generate Redis cluster template
    redis_config = RedisClusterConfig(
        cluster_name="myapp-cache",
        node_type="cache.r6g.large",
    )
    redis_template = manager.generate_redis_cluster_template(redis_config)
    print(f"\n✓ Generated Redis cluster template for '{redis_config.cluster_name}'")
    print(f"  Resources: {len(redis_template['Resources'])} components")


def example_customized_configuration():
    """Example with customized configuration."""
    print("\n" + "=" * 60)
    print("Customized Infrastructure Configuration")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Highly available database configuration
    rds_config = RDSAuroraConfig(
        cluster_name="production-db",
        engine="aurora-postgresql",
        engine_version="15.3",
        instance_class="db.r6g.xlarge",
        database_name="production",
        backup_retention_days=14,
        multi_az=True,
        storage_encrypted=True,
        deletion_protection=True,
    )
    
    print(f"\n✓ Configured RDS Aurora:")
    print(f"  Cluster: {rds_config.cluster_name}")
    print(f"  Engine: {rds_config.engine} {rds_config.engine_version}")
    print(f"  Instance: {rds_config.instance_class}")
    print(f"  Multi-AZ: {rds_config.multi_az}")
    print(f"  Encrypted: {rds_config.storage_encrypted}")
    print(f"  Backup Retention: {rds_config.backup_retention_days} days")
    
    # Enterprise Redis configuration
    redis_config = RedisClusterConfig(
        cluster_name="production-cache",
        node_type="cache.r6g.2xlarge",
        num_cache_nodes=3,
        engine_version="7.0",
        automatic_failover_enabled=True,
        multi_az_enabled=True,
        at_rest_encryption_enabled=True,
        transit_encryption_enabled=True,
        snapshot_retention_limit=7,
    )
    
    print(f"\n✓ Configured Redis Cluster:")
    print(f"  Cluster: {redis_config.cluster_name}")
    print(f"  Node Type: {redis_config.node_type}")
    print(f"  Nodes: {redis_config.num_cache_nodes}")
    print(f"  Multi-AZ: {redis_config.multi_az_enabled}")
    print(f"  Encryption (at rest): {redis_config.at_rest_encryption_enabled}")
    print(f"  Encryption (in transit): {redis_config.transit_encryption_enabled}")


def example_s3_with_lifecycle():
    """Example S3 bucket with lifecycle policies."""
    print("\n" + "=" * 60)
    print("S3 Bucket with Lifecycle Policies")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Configure S3 bucket with lifecycle rules
    s3_config = S3BucketConfig(
        bucket_name="myapp-data",
        versioning_enabled=True,
        encryption_enabled=True,
        lifecycle_rules=[
            {
                "Id": "TransitionOldVersions",
                "Status": "Enabled",
                "NoncurrentVersionTransitions": [
                    {
                        "NoncurrentDays": 30,
                        "StorageClass": "STANDARD_IA",
                    },
                    {
                        "NoncurrentDays": 90,
                        "StorageClass": "GLACIER",
                    },
                ],
                "NoncurrentVersionExpirationInDays": 365,
            },
            {
                "Id": "DeleteIncompleteUploads",
                "Status": "Enabled",
                "AbortIncompleteMultipartUpload": {
                    "DaysAfterInitiation": 7,
                },
            },
        ],
        cors_rules=[
            {
                "AllowedOrigins": ["https://myapp.com"],
                "AllowedMethods": ["GET", "HEAD"],
                "AllowedHeaders": ["*"],
                "MaxAge": 3600,
            }
        ],
        tags={"Environment": "production", "Application": "myapp"},
    )
    
    template = manager.generate_s3_bucket_template(s3_config)
    
    print(f"\n✓ Generated S3 bucket template for '{s3_config.bucket_name}'")
    print(f"  Versioning: {s3_config.versioning_enabled}")
    print(f"  Encryption: {s3_config.encryption_enabled}")
    print(f"  Lifecycle Rules: {len(s3_config.lifecycle_rules)}")
    print(f"  CORS Rules: {len(s3_config.cors_rules)}")
    print(f"  Tags: {len(s3_config.tags)}")


def example_cloudfront_cdn():
    """Example CloudFront CDN configuration."""
    print("\n" + "=" * 60)
    print("CloudFront CDN Configuration")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Configure CloudFront distribution
    cloudfront_config = CloudFrontConfig(
        distribution_name="myapp-cdn",
        origin_domain_name="myapp-assets.s3.amazonaws.com",
        price_class="PriceClass_100",  # North America and Europe
        enabled=True,
        default_root_object="index.html",
        compress=True,
        viewer_protocol_policy="redirect-to-https",
        allowed_methods=["GET", "HEAD", "OPTIONS"],
        cached_methods=["GET", "HEAD"],
        min_ttl=0,
        default_ttl=86400,  # 1 day
        max_ttl=31536000,   # 1 year
    )
    
    template = manager.generate_cloudfront_template(cloudfront_config)
    
    print(f"\n✓ Generated CloudFront distribution for '{cloudfront_config.distribution_name}'")
    print(f"  Origin: {cloudfront_config.origin_domain_name}")
    print(f"  Price Class: {cloudfront_config.price_class}")
    print(f"  HTTPS Only: {cloudfront_config.viewer_protocol_policy == 'redirect-to-https'}")
    print(f"  Compression: {cloudfront_config.compress}")
    print(f"  Default TTL: {cloudfront_config.default_ttl}s")


def example_secrets_management():
    """Example secrets management configuration."""
    print("\n" + "=" * 60)
    print("Secrets Manager Configuration")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Database credentials with rotation
    db_secret_config = SecretsManagerConfig(
        secret_name="myapp/database/credentials",
        description="Production database credentials",
        rotation_enabled=True,
        rotation_days=30,
        tags={
            "Environment": "production",
            "Application": "myapp",
            "Type": "database",
        },
    )
    
    db_template = manager.generate_secrets_manager_template(db_secret_config)
    
    print(f"\n✓ Database Credentials Secret:")
    print(f"  Name: {db_secret_config.secret_name}")
    print(f"  Rotation: {db_secret_config.rotation_enabled}")
    print(f"  Rotation Interval: {db_secret_config.rotation_days} days")
    
    # API keys without rotation
    api_secret_config = SecretsManagerConfig(
        secret_name="myapp/api/keys",
        description="Third-party API keys",
        rotation_enabled=False,
        tags={
            "Environment": "production",
            "Application": "myapp",
            "Type": "api-keys",
        },
    )
    
    api_template = manager.generate_secrets_manager_template(api_secret_config)
    
    print(f"\n✓ API Keys Secret:")
    print(f"  Name: {api_secret_config.secret_name}")
    print(f"  Rotation: {api_secret_config.rotation_enabled}")


def example_complete_infrastructure():
    """Example: Generate complete infrastructure for an application."""
    print("\n" + "=" * 60)
    print("Complete Infrastructure Stack")
    print("=" * 60)
    
    manager = CoreServicesManager()
    
    # Database
    rds_config = RDSAuroraConfig(
        cluster_name="myapp-production-db",
        database_name="myapp",
    )
    manager.generate_rds_aurora_template(rds_config)
    
    # Cache
    redis_config = RedisClusterConfig(
        cluster_name="myapp-production-cache",
    )
    manager.generate_redis_cluster_template(redis_config)
    
    # Storage
    assets_config = S3BucketConfig(
        bucket_name="myapp-production-assets",
        tags={"Purpose": "Assets"},
    )
    manager.generate_s3_bucket_template(assets_config)
    
    backups_config = S3BucketConfig(
        bucket_name="myapp-production-backups",
        tags={"Purpose": "Backups"},
    )
    manager.generate_s3_bucket_template(backups_config)
    
    # CDN
    cloudfront_config = CloudFrontConfig(
        distribution_name="myapp-production-cdn",
        origin_domain_name=f"{assets_config.bucket_name}.s3.amazonaws.com",
    )
    manager.generate_cloudfront_template(cloudfront_config)
    
    # Secrets
    db_secret_config = SecretsManagerConfig(
        secret_name="myapp/production/db-credentials",
        rotation_enabled=True,
    )
    manager.generate_secrets_manager_template(db_secret_config)
    
    api_secret_config = SecretsManagerConfig(
        secret_name="myapp/production/api-keys",
        rotation_enabled=False,
    )
    manager.generate_secrets_manager_template(api_secret_config)
    
    # Summary
    all_configs = manager.get_all_configs()
    
    print("\n✓ Complete infrastructure stack generated:")
    print(f"  RDS Clusters: {len(all_configs['rds'])}")
    print(f"  Redis Clusters: {len(all_configs['redis'])}")
    print(f"  S3 Buckets: {len(all_configs['s3'])}")
    print(f"  CloudFront Distributions: {len(all_configs['cloudfront'])}")
    print(f"  Secrets: {len(all_configs['secrets'])}")
    
    print("\n✓ Infrastructure components:")
    for rds_name in all_configs['rds'].keys():
        print(f"  - RDS: {rds_name}")
    for redis_name in all_configs['redis'].keys():
        print(f"  - Redis: {redis_name}")
    for s3_name in all_configs['s3'].keys():
        print(f"  - S3: {s3_name}")
    for cf_name in all_configs['cloudfront'].keys():
        print(f"  - CloudFront: {cf_name}")
    for secret_name in all_configs['secrets'].keys():
        print(f"  - Secret: {secret_name}")


def example_export_templates():
    """Example: Export templates to files."""
    print("\n" + "=" * 60)
    print("Export Templates to Files")
    print("=" * 60)
    
    import yaml
    from pathlib import Path
    import tempfile
    
    manager = CoreServicesManager()
    
    # Generate templates
    rds_config = RDSAuroraConfig(cluster_name="export-example-db")
    rds_template = manager.generate_rds_aurora_template(rds_config)
    
    # Export to temporary directory (in real use, export to actual directory)
    temp_dir = Path(tempfile.mkdtemp())
    
    # Export as YAML
    yaml_path = temp_dir / "rds-aurora.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(rds_template, f, default_flow_style=False, sort_keys=False)
    
    # Export as JSON
    json_path = temp_dir / "rds-aurora.json"
    with open(json_path, 'w') as f:
        json.dump(rds_template, f, indent=2)
    
    print(f"\n✓ Templates exported:")
    print(f"  YAML: {yaml_path}")
    print(f"  JSON: {json_path}")
    print(f"\n  Directory: {temp_dir}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Accelerapp Infrastructure Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_customized_configuration()
    example_s3_with_lifecycle()
    example_cloudfront_cdn()
    example_secrets_management()
    example_complete_infrastructure()
    example_export_templates()
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
    print("\nFor deployment instructions, see:")
    print("  deployment/infrastructure/aws/DEPLOYMENT_GUIDE.md")
    print("\n")


if __name__ == "__main__":
    main()
