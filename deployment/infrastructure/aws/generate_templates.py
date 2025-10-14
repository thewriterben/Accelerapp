"""
Generate CloudFormation templates for Phase 2 core services.
"""

import json
import yaml
from pathlib import Path
from accelerapp.infrastructure import (
    CoreServicesManager,
    RDSAuroraConfig,
    RedisClusterConfig,
    S3BucketConfig,
    CloudFrontConfig,
    SecretsManagerConfig,
)


def generate_all_templates():
    """Generate all CloudFormation templates for core services."""
    manager = CoreServicesManager()
    
    # Create output directories
    output_dir = Path(__file__).parent
    (output_dir / "database").mkdir(exist_ok=True)
    (output_dir / "cache").mkdir(exist_ok=True)
    (output_dir / "storage").mkdir(exist_ok=True)
    (output_dir / "cdn").mkdir(exist_ok=True)
    (output_dir / "secrets").mkdir(exist_ok=True)
    
    # Generate RDS Aurora template
    rds_config = RDSAuroraConfig(
        cluster_name="accelerapp-db-cluster",
        engine="aurora-postgresql",
        engine_version="15.3",
        instance_class="db.r6g.large",
        database_name="accelerapp",
        master_username="admin",
        backup_retention_days=7,
        multi_az=True,
        storage_encrypted=True,
        deletion_protection=True,
    )
    rds_template = manager.generate_rds_aurora_template(rds_config)
    
    with open(output_dir / "database" / "rds-aurora.yaml", "w") as f:
        yaml.dump(rds_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "database" / "rds-aurora.json", "w") as f:
        json.dump(rds_template, f, indent=2)
    
    # Generate Redis cluster template
    redis_config = RedisClusterConfig(
        cluster_name="accelerapp-cache-cluster",
        node_type="cache.r6g.large",
        num_cache_nodes=2,
        engine_version="7.0",
        automatic_failover_enabled=True,
        multi_az_enabled=True,
        at_rest_encryption_enabled=True,
        transit_encryption_enabled=True,
    )
    redis_template = manager.generate_redis_cluster_template(redis_config)
    
    with open(output_dir / "cache" / "redis-cluster.yaml", "w") as f:
        yaml.dump(redis_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "cache" / "redis-cluster.json", "w") as f:
        json.dump(redis_template, f, indent=2)
    
    # Generate S3 buckets templates
    # Assets bucket
    assets_config = S3BucketConfig(
        bucket_name="accelerapp-assets",
        versioning_enabled=True,
        encryption_enabled=True,
        lifecycle_rules=[
            {
                "Id": "DeleteOldVersions",
                "Status": "Enabled",
                "NoncurrentVersionExpirationInDays": 90,
            }
        ],
        cors_rules=[
            {
                "AllowedOrigins": ["*"],
                "AllowedMethods": ["GET", "HEAD"],
                "AllowedHeaders": ["*"],
                "MaxAge": 3600,
            }
        ],
        tags={"Purpose": "Assets", "Environment": "production"},
    )
    assets_template = manager.generate_s3_bucket_template(assets_config)
    
    with open(output_dir / "storage" / "s3-assets.yaml", "w") as f:
        yaml.dump(assets_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "storage" / "s3-assets.json", "w") as f:
        json.dump(assets_template, f, indent=2)
    
    # Backups bucket
    backups_config = S3BucketConfig(
        bucket_name="accelerapp-backups",
        versioning_enabled=True,
        encryption_enabled=True,
        lifecycle_rules=[
            {
                "Id": "TransitionToGlacier",
                "Status": "Enabled",
                "Transitions": [
                    {
                        "Days": 30,
                        "StorageClass": "GLACIER",
                    }
                ],
                "ExpirationInDays": 365,
            }
        ],
        tags={"Purpose": "Backups", "Environment": "production"},
    )
    backups_template = manager.generate_s3_bucket_template(backups_config)
    
    with open(output_dir / "storage" / "s3-backups.yaml", "w") as f:
        yaml.dump(backups_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "storage" / "s3-backups.json", "w") as f:
        json.dump(backups_template, f, indent=2)
    
    # Generate CloudFront template
    cloudfront_config = CloudFrontConfig(
        distribution_name="accelerapp-cdn",
        origin_domain_name="accelerapp-assets.s3.amazonaws.com",
        price_class="PriceClass_100",
        compress=True,
        viewer_protocol_policy="redirect-to-https",
    )
    cloudfront_template = manager.generate_cloudfront_template(cloudfront_config)
    
    with open(output_dir / "cdn" / "cloudfront.yaml", "w") as f:
        yaml.dump(cloudfront_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "cdn" / "cloudfront.json", "w") as f:
        json.dump(cloudfront_template, f, indent=2)
    
    # Generate Secrets Manager templates
    db_secret_config = SecretsManagerConfig(
        secret_name="accelerapp/db/credentials",
        description="Database credentials for Accelerapp",
        rotation_enabled=True,
        rotation_days=30,
        tags={"Purpose": "Database", "Environment": "production"},
    )
    db_secret_template = manager.generate_secrets_manager_template(db_secret_config)
    
    with open(output_dir / "secrets" / "db-credentials.yaml", "w") as f:
        yaml.dump(db_secret_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "secrets" / "db-credentials.json", "w") as f:
        json.dump(db_secret_template, f, indent=2)
    
    # API keys secret
    api_secret_config = SecretsManagerConfig(
        secret_name="accelerapp/api/keys",
        description="API keys and tokens for Accelerapp",
        rotation_enabled=False,
        tags={"Purpose": "API", "Environment": "production"},
    )
    api_secret_template = manager.generate_secrets_manager_template(api_secret_config)
    
    with open(output_dir / "secrets" / "api-keys.yaml", "w") as f:
        yaml.dump(api_secret_template, f, default_flow_style=False, sort_keys=False)
    
    with open(output_dir / "secrets" / "api-keys.json", "w") as f:
        json.dump(api_secret_template, f, indent=2)
    
    print("✓ Generated RDS Aurora template")
    print("✓ Generated Redis cluster template")
    print("✓ Generated S3 assets bucket template")
    print("✓ Generated S3 backups bucket template")
    print("✓ Generated CloudFront distribution template")
    print("✓ Generated database credentials secret template")
    print("✓ Generated API keys secret template")
    print("\nAll CloudFormation templates generated successfully!")
    print(f"\nTemplates saved to: {output_dir}")


if __name__ == "__main__":
    generate_all_templates()
