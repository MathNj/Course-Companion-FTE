"""
Simple R2 Content API - No Authentication Required
Serves content directly from Cloudflare R2 storage

This is a lightweight API that delivers course content from R2
without requiring database or authentication.
"""

import os
import boto3
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Course Companion - R2 Content API",
    description="Direct content delivery from Cloudflare R2 storage",
    version="1.0.0"
)

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# R2 Configuration from environment
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

logger.info(f"R2 Configuration:")
logger.info(f"  Account ID: {R2_ACCOUNT_ID[:10]}...")
logger.info(f"  Bucket: {R2_BUCKET_NAME}")
logger.info(f"  Endpoint: {R2_ENDPOINT}")

# Initialize S3 client for R2
if all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_ENDPOINT]):
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name='auto'
        )
        logger.info("✅ R2 client initialized successfully")

        # Test connection by listing bucket
        try:
            test_response = s3_client.list_objects_v2(
                Bucket=R2_BUCKET_NAME,
                MaxKeys=1
            )
            logger.info(f"✅ R2 connection test successful. Bucket has objects.")
        except Exception as e:
            logger.warning(f"⚠️  R2 connection test warning: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize R2 client: {e}")
        s3_client = None
else:
    logger.error("❌ R2 configuration incomplete. Please check environment variables.")
    s3_client = None


def get_chapter_from_r2(chapter_id: str) -> Optional[Dict]:
    """Fetch chapter content from R2 storage"""
    if not s3_client:
        raise HTTPException(
            status_code=503,
            detail="R2 storage is not configured. Please check R2 credentials."
        )

    try:
        # R2 stores chapters as: content/chapters/chapter-1.json
        key = f'content/chapters/{chapter_id}.json'

        logger.info(f"Fetching from R2: {key}")

        # Get object from R2
        response = s3_client.get_object(Bucket=R2_BUCKET_NAME, Key=key)

        # Parse JSON content
        content = response['Body'].read().decode('utf-8')
        chapter_data = json.loads(content)

        logger.info(f"✅ Successfully loaded {chapter_id} from R2")
        return chapter_data

    except s3_client.exceptions.NoSuchKey:
        logger.error(f"❌ Chapter not found in R2: {chapter_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Chapter '{chapter_id}' not found in R2 storage"
        )
    except Exception as e:
        logger.error(f"❌ Error fetching from R2: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading chapter from R2: {str(e)}"
        )


def list_all_chapters_from_r2() -> List[Dict]:
    """List all available chapters from R2"""
    if not s3_client:
        raise HTTPException(
            status_code=503,
            detail="R2 storage is not configured. Please check R2 credentials."
        )

    try:
        logger.info(f"Listing chapters in R2 bucket: {R2_BUCKET_NAME}/content/chapters/")

        # List all objects in content/chapters/
        response = s3_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix='content/chapters/'
        )

        chapters = []
        for obj in response.get('Contents', []):
            key = obj['Key']

            # Only process .json files
            if key.endswith('.json'):
                logger.info(f"Found chapter: {key}")

                try:
                    # Get the file content
                    file_obj = s3_client.get_object(Bucket=R2_BUCKET_NAME, Key=key)
                    content = file_obj['Body'].read().decode('utf-8')
                    chapter_data = json.loads(content)
                    chapters.append(chapter_data)
                    logger.info(f"✅ Loaded chapter: {chapter_data.get('id', 'unknown')}")
                except Exception as e:
                    logger.error(f"❌ Error loading chapter {key}: {e}")
                    continue

        logger.info(f"✅ Successfully loaded {len(chapters)} chapters from R2")
        return chapters

    except Exception as e:
        logger.error(f"❌ Error listing R2 objects: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing chapters from R2: {str(e)}"
        )


# ============================
# API Endpoints
# ============================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Course Companion - R2 Content API",
        "version": "1.0.0",
        "status": "operational",
        "r2_bucket": R2_BUCKET_NAME,
        "endpoints": {
            "GET /chapters": "List all chapters",
            "GET /chapters/{id}": "Get specific chapter",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if s3_client:
        return {
            "status": "healthy",
            "r2_connected": True,
            "bucket": R2_BUCKET_NAME
        }
    else:
        return {
            "status": "degraded",
            "r2_connected": False,
            "message": "R2 storage not configured"
        }


@app.get("/chapters")
async def get_all_chapters():
    """
    Get all chapters from R2 storage

    Returns:
        List of chapter objects with all sections and content
    """
    logger.info("API: GET /chapters - Fetching all chapters from R2")

    chapters = list_all_chapters_from_r2()

    return {
        "chapters": chapters,
        "count": len(chapters),
        "source": "R2 Storage"
    }


@app.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    """
    Get specific chapter from R2 storage

    Parameters:
        chapter_id: Chapter ID (e.g., "chapter-1")

    Returns:
        Full chapter object with sections and content
    """
    logger.info(f"API: GET /chapters/{chapter_id} - Fetching from R2")

    chapter = get_chapter_from_r2(chapter_id)

    return {
        "chapter": chapter,
        "source": "R2 Storage",
        "chapter_id": chapter_id
    }


@app.get("/content/{chapter_id}")
async def get_chapter_content(chapter_id: str):
    """
    Alias endpoint for getting chapter content
    Same as /chapters/{id}
    """
    logger.info(f"API: GET /content/{chapter_id} - Fetching from R2")
    return await get_chapter(chapter_id)


# ============================
# Startup Information
# ============================

if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting R2 Content API Server...")
    logger.info("=" * 60)
    logger.info(f"Environment: {os.getenv('APP_ENV', 'development')}")
    logger.info(f"R2 Bucket: {R2_BUCKET_NAME}")
    logger.info(f"R2 Endpoint: {R2_ENDPOINT}")
    logger.info("")
    logger.info("Server will be available at:")
    logger.info("  → http://localhost:8001")
    logger.info("  → http://localhost:8001/docs")
    logger.info("  → http://localhost:8001/chapters")
    logger.info("  → http://localhost:8001/health")
    logger.info("")
    logger.info("Ready to serve content from Cloudflare R2! 🚀")
    logger.info("=" * 60)

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
