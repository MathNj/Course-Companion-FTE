"""
Simple R2 Content API for Testing
Standalone FastAPI app to test R2 integration without full backend
"""

import os
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Course Companion FTE - R2 Content API",
    description="Simple content delivery API for Generative AI Fundamentals",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# R2 Configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

# Initialize R2 client
if all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET]):
    s3_client = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    print("[OK] R2 client initialized successfully")
else:
    s3_client = None
    print("[ERROR] R2 credentials not configured")


# Response Models
class ChapterListResponse(BaseModel):
    total: int
    chapters: List[Dict]


class ChapterResponse(BaseModel):
    chapter_name: str
    content: str
    size_bytes: int
    content_type: str


class SearchResponse(BaseModel):
    query: str
    results: List[Dict]
    total: int


# Endpoints
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "operational",
        "service": "Course Companion FTE - R2 Content API",
        "course": "Generative AI Fundamentals",
        "r2_configured": s3_client is not None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not s3_client:
        raise HTTPException(status_code=503, detail="R2 client not configured")

    try:
        # Test R2 connection by listing bucket
        s3_client.list_objects_v2(Bucket=R2_BUCKET, MaxKeys=1)
        return {"status": "healthy", "r2_connected": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"R2 connection failed: {str(e)}")


@app.get("/chapters", response_model=ChapterListResponse)
async def list_chapters():
    """List all available chapters from R2"""
    if not s3_client:
        raise HTTPException(status_code=503, detail="R2 client not configured")

    try:
        response = s3_client.list_objects_v2(
            Bucket=R2_BUCKET,
            Prefix='Generative AI Fundamentals/'
        )

        if 'Contents' not in response:
            return ChapterListResponse(total=0, chapters=[])

        chapters = []
        for obj in response['Contents']:
            if obj['Key'].endswith('.md'):
                name = obj['Key'].replace('Generative AI Fundamentals/', '').replace('.md', '')
                chapters.append({
                    'name': name,
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })

        return ChapterListResponse(total=len(chapters), chapters=chapters)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chapters/{chapter_name}", response_model=ChapterResponse)
async def get_chapter(chapter_name: str):
    """Get specific chapter content from R2

    Supports:
    - Full name: "Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI"
    - Short name: "chapter-1"
    - Number: "1"
    """
    if not s3_client:
        raise HTTPException(status_code=503, detail="R2 client not configured")

    try:
        # First, list all chapters to find the match
        list_response = s3_client.list_objects_v2(
            Bucket=R2_BUCKET,
            Prefix='Generative AI Fundamentals/'
        )

        if 'Contents' not in list_response:
            raise HTTPException(status_code=404, detail="No chapters found")

        # Find matching chapter
        matched_key = None
        matched_name = None

        for obj in list_response['Contents']:
            if not obj['Key'].endswith('.md'):
                continue

            name = obj['Key'].replace('Generative AI Fundamentals/', '').replace('.md', '')

            # Try multiple matching strategies
            if (chapter_name.lower() == name.lower() or
                chapter_name.lower() in name.lower() or
                f"chapter {chapter_name}" in name.lower() or
                f"chapter-{chapter_name}" in name.lower() or
                chapter_name.replace('-', ' ') in name.lower()):

                matched_key = obj['Key']
                matched_name = name
                break

        if not matched_key:
            # List available chapters for error message
            available = [obj['Key'].replace('Generative AI Fundamentals/', '').replace('.md', '')
                        for obj in list_response['Contents'] if obj['Key'].endswith('.md')]
            raise HTTPException(
                status_code=404,
                detail=f"Chapter '{chapter_name}' not found. Available: {available}"
            )

        # Fetch the chapter content
        response = s3_client.get_object(Bucket=R2_BUCKET, Key=matched_key)
        content = response['Body'].read().decode('utf-8')

        return ChapterResponse(
            chapter_name=matched_name,
            content=content,
            size_bytes=len(content),
            content_type="text/markdown"
        )

    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", response_model=SearchResponse)
async def search_content(q: str, limit: int = 10):
    """Search for content across all chapters by keyword"""
    if not s3_client:
        raise HTTPException(status_code=503, detail="R2 client not configured")

    try:
        # List all chapters
        list_response = s3_client.list_objects_v2(
            Bucket=R2_BUCKET,
            Prefix='Generative AI Fundamentals/'
        )

        results = []

        if 'Contents' in list_response:
            for obj in list_response['Contents']:
                if obj['Key'].endswith('.md'):
                    # Get content
                    obj_response = s3_client.get_object(Bucket=R2_BUCKET, Key=obj['Key'])
                    content = obj_response['Body'].read().decode('utf-8')

                    # Simple keyword search (case-insensitive)
                    if q.lower() in content.lower():
                        # Extract preview around match
                        content_lower = content.lower()
                        match_pos = content_lower.find(q.lower())
                        start = max(0, match_pos - 200)
                        end = min(len(content), match_pos + 300)
                        preview = content[start:end]

                        # Add ellipsis if truncated
                        if start > 0:
                            preview = "..." + preview
                        if end < len(content):
                            preview = preview + "..."

                        name = obj['Key'].replace('Generative AI Fundamentals/', '').replace('.md', '')

                        results.append({
                            "chapter": name,
                            "preview": preview,
                            "match_count": content_lower.count(q.lower()),
                            "size": obj['Size']
                        })

        # Sort by match count (most relevant first)
        results.sort(key=lambda x: x['match_count'], reverse=True)

        return SearchResponse(
            query=q,
            results=results[:limit],
            total=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Course Companion FTE - R2 Content API")
    print("="*60)
    print(f"\nR2 Bucket: {R2_BUCKET}")
    print(f"R2 Endpoint: {R2_ENDPOINT}")
    print(f"R2 Configured: {s3_client is not None}\n")

    # Run without reload for simplicity
    uvicorn.run(app, host="0.0.0.0", port=8000)
