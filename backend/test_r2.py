"""
Test R2 Connection
"""
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

print("="*60)
print("R2 Connection Test")
print("="*60)
print(f"\nAccount ID: {R2_ACCOUNT_ID}")
print(f"Bucket: {R2_BUCKET}")
print(f"Endpoint: {R2_ENDPOINT}")

# Initialize R2 client
try:
    s3_client = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    print("\n[OK] R2 client initialized")
except Exception as e:
    print(f"\n[ERROR] Failed to initialize R2 client: {e}")
    exit(1)

# Test connection by listing objects
try:
    print("\n[TEST] Listing objects in bucket...")
    response = s3_client.list_objects_v2(
        Bucket=R2_BUCKET,
        Prefix='Generative AI Fundamentals/',
        MaxKeys=10
    )

    if 'Contents' in response:
        print(f"[OK] Found {len(response['Contents'])} objects:\n")
        for obj in response['Contents']:
            name = obj['Key'].replace('Generative AI Fundamentals/', '')
            size_mb = obj['Size'] / (1024*1024)
            print(f"  - {name}")
            print(f"    Size: {size_mb:.2f} MB")
            print(f"    Last Modified: {obj['LastModified']}\n")
    else:
        print("[WARNING] No objects found in bucket")

    # Test fetching a chapter
    print("[TEST] Fetching Chapter 1...")
    response = s3_client.get_object(
        Bucket=R2_BUCKET,
        Key='Generative AI Fundamentals/Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI.md'
    )

    content = response['Body'].read().decode('utf-8')
    print(f"[OK] Fetched Chapter 1")
    print(f"    Content length: {len(content)} characters")
    print(f"    First 200 chars:\n{content[:200]}...\n")

    print("="*60)
    print("SUCCESS: R2 connection is working!")
    print("="*60)

except Exception as e:
    print(f"\n[ERROR] R2 connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
