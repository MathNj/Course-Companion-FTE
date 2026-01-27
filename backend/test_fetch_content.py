"""
Fetch sample content from Chapter 1 for testing
"""
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'
)

# Fetch Chapter 1
response = s3_client.get_object(
    Bucket=R2_BUCKET,
    Key='Generative AI Fundamentals/Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI.md'
)

content = response['Body'].read().decode('utf-8')

# Extract first ~1500 characters for testing
sample = content[:1500]

print("="*60)
print("SAMPLE CONTENT FROM CHAPTER 1")
print("="*60)
print(sample)
print("...")
print("="*60)
print(f"\nTotal content length: {len(content)} characters")
print(f"This sample: {len(sample)} characters")
