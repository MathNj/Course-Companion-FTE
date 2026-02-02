"""
Upload content to R2 storage

Simple script to upload chapter and quiz content from local files to Cloudflare R2.
"""

import os
import json
import boto3
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# R2 Configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

# Paths
CONTENT_DIR = Path(__file__).parent / "content"
CHAPTERS_DIR = CONTENT_DIR / "chapters"
QUIZZES_DIR = CONTENT_DIR / "quizzes"

logger.info("R2 Upload Script")
logger.info("=" * 50)
logger.info(f"Bucket: {R2_BUCKET_NAME}")
logger.info(f"Chapters: {CHAPTERS_DIR}")
logger.info(f"Quizzes: {QUIZZES_DIR}")
logger.info("=" * 50)

# Initialize R2/S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'
)

def upload_file_to_r2(file_path: Path, s3_key: str):
    """Upload a single file to R2"""
    try:
        logger.info(f"Uploading: {s3_key}")

        with open(file_path, 'rb') as f:
            s3_client.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=s3_key,
                Body=f,
                ContentType='application/json'
            )

        logger.info(f"✅ Successfully uploaded: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"❌ Error uploading {file_path.name}: {e}")
        return False

def upload_chapters():
    """Upload all chapter JSON files to R2"""
    logger.info("\n📚 Uploading Chapters...")

    chapter_files = list(CHAPTERS_DIR.glob("*.json"))
    logger.info(f"Found {len(chapter_files)} chapter files")

    success_count = 0
    for chapter_file in chapter_files:
        s3_key = f"content/chapters/{chapter_file.name}"
        if upload_file_to_r2(chapter_file, s3_key):
            success_count += 1

    logger.info(f"✅ Chapters uploaded: {success_count}/{len(chapter_files)}")
    return success_count > 0

def upload_quizzes():
    """Upload all quiz JSON files to R2"""
    logger.info("\n📝 Uploading Quizzes...")

    if not QUIZZES_DIR.exists():
        logger.warning("No quizzes directory found, skipping...")
        return True

    quiz_files = list(QUIZZES_DIR.glob("*.json"))
    logger.info(f"Found {len(quiz_files)} quiz files")

    success_count = 0
    for quiz_file in quiz_files:
        s3_key = f"content/quizzes/{quiz_file.name}"
        if upload_file_to_r2(quiz_file, s3_key):
            success_count += 1

    logger.info(f"✅ Quizzes uploaded: {success_count}/{len(quiz_files)}")
    return success_count >= 0

def list_r2_content():
    """List what's currently in R2"""
    logger.info("\n📋 Current R2 Content:")

    try:
        # List chapters
        response = s3_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix='content/chapters/'
        )

        chapters = response.get('Contents', [])
        logger.info(f"Chapters in R2: {len(chapters)}")
        for obj in chapters[:5]:  # Show first 5
            logger.info(f"  - {obj['Key']}")

        if len(chapters) > 5:
            logger.info(f"  ... and {len(chapters) - 5} more")

    except Exception as e:
        logger.error(f"Error listing R2 content: {e}")

if __name__ == "__main__":
    logger.info("Starting upload to R2...")
    logger.info("")

    # Check if directories exist
    if not CHAPTERS_DIR.exists():
        logger.error(f"❌ Chapters directory not found: {CHAPTERS_DIR}")
        logger.info("Please ensure content files exist before running this script.")
        exit(1)

    # Upload content
    chapters_uploaded = upload_chapters()
    quizzes_uploaded = upload_quizzes()

    # List what's in R2 now
    list_r2_content()

    logger.info("")
    logger.info("=" * 50)
    if chapters_uploaded or quizzes_uploaded:
        logger.info("✅ Upload complete!")
        logger.info(f"  Chapters: {chapters_uploaded}")
        logger.info(f"  Quizzes: {quizzes_uploaded}")
        logger.info("")
        logger.info("Your content is now available on R2! 🎉")
    else:
        logger.error("❌ Upload failed. Please check:")
        logger.error("  1. R2 credentials in .env")
        logger.error("  2. Bucket exists in R2")
        logger.error("  3. Write permissions for bucket")
        logger.error("  4. Network connection")
