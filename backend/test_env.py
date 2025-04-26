#!/usr/bin/env python3
"""
Simple test script to verify that environment variables are being read correctly.
This can be used to test if your AWS credentials are properly configured.
"""

import os
import boto3
import sys

def test_env_variables():
    """Test if AWS environment variables are set and can be read."""
    print("Testing environment variables...")
    
    # Check for AWS credentials in environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    print(f"AWS_REGION: {'Set to ' + aws_region if aws_region else 'Not set, will use default'}")
    print(f"AWS_ACCESS_KEY_ID: {'Set' if aws_access_key else 'Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret_key else 'Not set'}")
    
    # Try to initialize a boto3 client
    try:
        print("\nAttempting to initialize boto3 client...")
        if aws_access_key and aws_secret_key:
            client = boto3.client(
                'sts',  # Using STS as it's a lightweight service for testing
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            client = boto3.client('sts', region_name=aws_region)
        
        # Try to make a simple API call
        response = client.get_caller_identity()
        print("Successfully connected to AWS!")
        print(f"Account ID: {response['Account']}")
        print(f"User ID: {response['UserId']}")
        print(f"ARN: {response['Arn']}")
        return True
    except Exception as e:
        print(f"Error connecting to AWS: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_env_variables()
    sys.exit(0 if success else 1)