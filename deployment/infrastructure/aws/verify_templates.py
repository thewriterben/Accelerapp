#!/usr/bin/env python3
"""
Verify CloudFormation templates for Phase 2 infrastructure.

This script validates all generated CloudFormation templates to ensure
they are syntactically correct and contain required components.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_template(file_path: Path) -> Dict[str, Any]:
    """Load CloudFormation template from YAML or JSON file."""
    with open(file_path, 'r') as f:
        if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
            return yaml.safe_load(f)
        elif file_path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")


def verify_template_structure(template: Dict[str, Any], template_name: str) -> List[str]:
    """Verify basic CloudFormation template structure."""
    issues = []
    
    # Check for required top-level keys
    if "AWSTemplateFormatVersion" not in template:
        issues.append(f"Missing AWSTemplateFormatVersion in {template_name}")
    
    if "Resources" not in template:
        issues.append(f"Missing Resources section in {template_name}")
    elif not template["Resources"]:
        issues.append(f"Resources section is empty in {template_name}")
    
    return issues


def verify_rds_template(template: Dict[str, Any]) -> List[str]:
    """Verify RDS Aurora template."""
    issues = []
    resources = template.get("Resources", {})
    
    # Check for required resources
    required_resources = ["DBCluster", "DBInstance1", "DBInstance2", "DBSecurityGroup"]
    for resource in required_resources:
        if resource not in resources:
            issues.append(f"Missing required resource: {resource}")
    
    # Verify DBCluster properties
    if "DBCluster" in resources:
        cluster = resources["DBCluster"]
        if cluster.get("Type") != "AWS::RDS::DBCluster":
            issues.append("DBCluster has incorrect type")
        
        props = cluster.get("Properties", {})
        if not props.get("StorageEncrypted"):
            issues.append("Storage encryption not enabled for DBCluster")
        if not props.get("DeletionProtection"):
            issues.append("Deletion protection not enabled for DBCluster")
    
    # Check outputs
    outputs = template.get("Outputs", {})
    required_outputs = ["DBClusterEndpoint", "DBClusterReadEndpoint"]
    for output in required_outputs:
        if output not in outputs:
            issues.append(f"Missing required output: {output}")
    
    return issues


def verify_redis_template(template: Dict[str, Any]) -> List[str]:
    """Verify Redis cluster template."""
    issues = []
    resources = template.get("Resources", {})
    
    # Check for required resources
    required_resources = ["CacheReplicationGroup", "CacheSubnetGroup", "CacheSecurityGroup"]
    for resource in required_resources:
        if resource not in resources:
            issues.append(f"Missing required resource: {resource}")
    
    # Verify encryption settings
    if "CacheReplicationGroup" in resources:
        cache = resources["CacheReplicationGroup"]
        props = cache.get("Properties", {})
        if not props.get("AtRestEncryptionEnabled"):
            issues.append("At-rest encryption not enabled for Redis")
        if not props.get("TransitEncryptionEnabled"):
            issues.append("Transit encryption not enabled for Redis")
        if not props.get("AutomaticFailoverEnabled"):
            issues.append("Automatic failover not enabled for Redis")
    
    return issues


def verify_s3_template(template: Dict[str, Any]) -> List[str]:
    """Verify S3 bucket template."""
    issues = []
    resources = template.get("Resources", {})
    
    # Check for required resources
    if "S3Bucket" not in resources:
        issues.append("Missing S3Bucket resource")
    
    if "BucketPolicy" not in resources:
        issues.append("Missing BucketPolicy resource")
    
    # Verify bucket security settings
    if "S3Bucket" in resources:
        bucket = resources["S3Bucket"]
        props = bucket.get("Properties", {})
        
        if "BucketEncryption" not in props:
            issues.append("Bucket encryption not configured")
        
        if "VersioningConfiguration" not in props:
            issues.append("Versioning not configured")
        
        public_access = props.get("PublicAccessBlockConfiguration", {})
        if not all([
            public_access.get("BlockPublicAcls"),
            public_access.get("BlockPublicPolicy"),
            public_access.get("IgnorePublicAcls"),
            public_access.get("RestrictPublicBuckets"),
        ]):
            issues.append("Public access not fully blocked")
    
    return issues


def verify_cloudfront_template(template: Dict[str, Any]) -> List[str]:
    """Verify CloudFront distribution template."""
    issues = []
    resources = template.get("Resources", {})
    
    # Check for required resources
    if "CloudFrontDistribution" not in resources:
        issues.append("Missing CloudFrontDistribution resource")
    
    if "CloudFrontOriginAccessIdentity" not in resources:
        issues.append("Missing CloudFrontOriginAccessIdentity resource")
    
    # Verify HTTPS enforcement
    if "CloudFrontDistribution" in resources:
        dist = resources["CloudFrontDistribution"]
        props = dist.get("Properties", {})
        dist_config = props.get("DistributionConfig", {})
        
        default_behavior = dist_config.get("DefaultCacheBehavior", {})
        if default_behavior.get("ViewerProtocolPolicy") != "redirect-to-https":
            issues.append("HTTPS not enforced (should be redirect-to-https)")
    
    return issues


def verify_secrets_template(template: Dict[str, Any]) -> List[str]:
    """Verify Secrets Manager template."""
    issues = []
    resources = template.get("Resources", {})
    
    # Check for required resources
    if "Secret" not in resources:
        issues.append("Missing Secret resource")
    
    return issues


def main():
    """Main verification function."""
    print("=" * 60)
    print("CloudFormation Template Verification")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    all_issues = []
    verified_count = 0
    
    # Verify RDS templates
    print("\n📊 Verifying RDS Aurora templates...")
    for template_file in (base_dir / "database").glob("rds-aurora.*"):
        print(f"  Checking {template_file.name}...")
        template = load_template(template_file)
        issues = verify_template_structure(template, template_file.name)
        issues.extend(verify_rds_template(template))
        
        if issues:
            all_issues.extend([(template_file.name, issue) for issue in issues])
            print(f"    ✗ Found {len(issues)} issue(s)")
        else:
            print(f"    ✓ Valid")
            verified_count += 1
    
    # Verify Redis templates
    print("\n📊 Verifying Redis cluster templates...")
    for template_file in (base_dir / "cache").glob("redis-cluster.*"):
        print(f"  Checking {template_file.name}...")
        template = load_template(template_file)
        issues = verify_template_structure(template, template_file.name)
        issues.extend(verify_redis_template(template))
        
        if issues:
            all_issues.extend([(template_file.name, issue) for issue in issues])
            print(f"    ✗ Found {len(issues)} issue(s)")
        else:
            print(f"    ✓ Valid")
            verified_count += 1
    
    # Verify S3 templates
    print("\n📊 Verifying S3 bucket templates...")
    for template_file in (base_dir / "storage").glob("s3-*.*"):
        print(f"  Checking {template_file.name}...")
        template = load_template(template_file)
        issues = verify_template_structure(template, template_file.name)
        issues.extend(verify_s3_template(template))
        
        if issues:
            all_issues.extend([(template_file.name, issue) for issue in issues])
            print(f"    ✗ Found {len(issues)} issue(s)")
        else:
            print(f"    ✓ Valid")
            verified_count += 1
    
    # Verify CloudFront templates
    print("\n📊 Verifying CloudFront distribution templates...")
    for template_file in (base_dir / "cdn").glob("cloudfront.*"):
        print(f"  Checking {template_file.name}...")
        template = load_template(template_file)
        issues = verify_template_structure(template, template_file.name)
        issues.extend(verify_cloudfront_template(template))
        
        if issues:
            all_issues.extend([(template_file.name, issue) for issue in issues])
            print(f"    ✗ Found {len(issues)} issue(s)")
        else:
            print(f"    ✓ Valid")
            verified_count += 1
    
    # Verify Secrets Manager templates
    print("\n📊 Verifying Secrets Manager templates...")
    for template_file in (base_dir / "secrets").glob("*.yaml"):
        print(f"  Checking {template_file.name}...")
        template = load_template(template_file)
        issues = verify_template_structure(template, template_file.name)
        issues.extend(verify_secrets_template(template))
        
        if issues:
            all_issues.extend([(template_file.name, issue) for issue in issues])
            print(f"    ✗ Found {len(issues)} issue(s)")
        else:
            print(f"    ✓ Valid")
            verified_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    if all_issues:
        print(f"\n❌ Verification failed with {len(all_issues)} issue(s):\n")
        for template_name, issue in all_issues:
            print(f"  - [{template_name}] {issue}")
        return 1
    else:
        print(f"\n✓ All {verified_count} templates verified successfully!")
        print("\n✓ Templates are ready for deployment")
        return 0


if __name__ == "__main__":
    exit(main())
