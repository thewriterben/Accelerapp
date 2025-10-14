"""
AWS integration for Accelerapp.
"""

from typing import Dict, Any, List


class AWSIntegration:
    """
    AWS deployment and integration support.
    """

    def __init__(self):
        """Initialize AWS integration."""
        self.configurations: Dict[str, Any] = {}

    def generate_lambda_deployment(
        self, function_name: str, runtime: str = "python3.10"
    ) -> Dict[str, Any]:
        """
        Generate AWS Lambda deployment configuration.

        Args:
            function_name: Lambda function name
            runtime: Python runtime version

        Returns:
            Deployment configuration
        """
        config = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"Accelerapp {function_name} Lambda Function",
            "Resources": {
                "AccelerappLambdaFunction": {
                    "Type": "AWS::Lambda::Function",
                    "Properties": {
                        "FunctionName": function_name,
                        "Runtime": runtime,
                        "Handler": "lambda_function.lambda_handler",
                        "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                        "Code": {"ZipFile": "# Accelerapp Lambda Handler\n# Generated code here\n"},
                        "Timeout": 300,
                        "MemorySize": 512,
                        "Environment": {
                            "Variables": {
                                "ACCELERAPP_ENV": "production",
                            }
                        },
                    },
                },
                "LambdaExecutionRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"Service": "lambda.amazonaws.com"},
                                    "Action": "sts:AssumeRole",
                                }
                            ],
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                        ],
                    },
                },
            },
        }

        return config

    def generate_iot_core_integration(
        self, thing_name: str, platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Generate AWS IoT Core integration for hardware devices.

        Args:
            thing_name: IoT Thing name
            platforms: Target hardware platforms

        Returns:
            IoT Core configuration
        """
        config = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"AWS IoT Core configuration for {thing_name}",
            "Resources": {
                "IoTThing": {
                    "Type": "AWS::IoT::Thing",
                    "Properties": {
                        "ThingName": thing_name,
                        "AttributePayload": {
                            "Attributes": {
                                "platforms": ",".join(platforms),
                                "framework": "accelerapp",
                            }
                        },
                    },
                },
                "IoTPolicy": {
                    "Type": "AWS::IoT::Policy",
                    "Properties": {
                        "PolicyName": f"{thing_name}-policy",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iot:Connect",
                                        "iot:Publish",
                                        "iot:Subscribe",
                                        "iot:Receive",
                                    ],
                                    "Resource": "*",
                                }
                            ],
                        },
                    },
                },
            },
        }

        return config

    def generate_s3_storage_config(self, bucket_name: str) -> Dict[str, Any]:
        """
        Generate S3 storage configuration for firmware artifacts.

        Args:
            bucket_name: S3 bucket name

        Returns:
            S3 configuration
        """
        config = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                "FirmwareBucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": bucket_name,
                        "VersioningConfiguration": {"Status": "Enabled"},
                        "PublicAccessBlockConfiguration": {
                            "BlockPublicAcls": True,
                            "BlockPublicPolicy": True,
                            "IgnorePublicAcls": True,
                            "RestrictPublicBuckets": True,
                        },
                        "LifecycleConfiguration": {
                            "Rules": [
                                {
                                    "Id": "DeleteOldVersions",
                                    "Status": "Enabled",
                                    "NoncurrentVersionExpirationInDays": 90,
                                }
                            ]
                        },
                    },
                }
            },
        }

        return config

    def generate_marketplace_listing(self, app_name: str, description: str) -> Dict[str, Any]:
        """
        Generate AWS Marketplace listing configuration.

        Args:
            app_name: Application name
            description: Application description

        Returns:
            Marketplace configuration
        """
        config = {
            "ProductId": f"prod-accelerapp-{app_name.lower()}",
            "ProductTitle": f"Accelerapp - {app_name}",
            "ShortDescription": description[:120],
            "LongDescription": description,
            "ProductCategory": "Developer Tools",
            "SupportedRegions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            "PricingModel": "Free",
            "DeliveryMethods": ["CloudFormation", "Container"],
        }

        return config
