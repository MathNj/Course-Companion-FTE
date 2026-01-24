"""
Content Seeding Script

Uploads chapter and quiz content to storage (local or Cloudflare R2).
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
CONTENT_DIR = Path(__file__).parent.parent / "content"
CHAPTERS_DIR = CONTENT_DIR / "chapters"
QUIZZES_DIR = CONTENT_DIR / "quizzes"

# Storage mode (set via environment variable)
STORAGE_MODE = os.getenv("CONTENT_STORAGE", "local")  # "local" or "r2"


async def validate_chapter(chapter_data: Dict[str, Any], chapter_id: str) -> bool:
    """
    Validate chapter JSON structure.

    Args:
        chapter_data: Chapter JSON data
        chapter_id: Expected chapter ID

    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "id", "title", "description", "access_tier",
        "estimated_time_minutes", "difficulty",
        "learning_objectives", "sections"
    ]

    for field in required_fields:
        if field not in chapter_data:
            logger.error(f"Chapter {chapter_id}: Missing required field '{field}'")
            return False

    if chapter_data["id"] != chapter_id:
        logger.error(f"Chapter {chapter_id}: ID mismatch in JSON")
        return False

    if not chapter_data["sections"]:
        logger.error(f"Chapter {chapter_id}: No sections defined")
        return False

    logger.info(f"✓ Chapter {chapter_id} validated successfully")
    return True


async def validate_quiz(quiz_data: Dict[str, Any], quiz_id: str) -> bool:
    """
    Validate quiz JSON structure.

    Args:
        quiz_data: Quiz JSON data
        quiz_id: Expected quiz ID

    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "id", "chapter_id", "title", "description",
        "total_questions", "passing_score", "questions"
    ]

    for field in required_fields:
        if field not in quiz_data:
            logger.error(f"Quiz {quiz_id}: Missing required field '{field}'")
            return False

    if quiz_data["id"] != quiz_id:
        logger.error(f"Quiz {quiz_id}: ID mismatch in JSON")
        return False

    if len(quiz_data["questions"]) != quiz_data["total_questions"]:
        logger.error(
            f"Quiz {quiz_id}: Question count mismatch "
            f"(expected {quiz_data['total_questions']}, found {len(quiz_data['questions'])})"
        )
        return False

    # Validate each question
    for question in quiz_data["questions"]:
        # Check answer_key OR keywords (for short_answer)
        if question["type"] == "short_answer":
            if "keywords" not in question:
                logger.error(f"Quiz {quiz_id}, Question {question['id']}: Missing keywords for short_answer")
                return False
        else:
            if "answer_key" not in question:
                logger.error(f"Quiz {quiz_id}, Question {question['id']}: Missing answer_key")
                return False

        if question["type"] == "multiple_choice" and "options" not in question:
            logger.error(f"Quiz {quiz_id}, Question {question['id']}: Missing options")
            return False

    logger.info(f"✓ Quiz {quiz_id} validated successfully")
    return True


async def seed_local_storage() -> Dict[str, Any]:
    """
    Seed content to local file storage.

    Content is already in the correct location, so this just validates it.

    Returns:
        Summary of seeding results
    """
    logger.info("📁 Seeding to local storage...")

    results = {
        "mode": "local",
        "chapters_seeded": 0,
        "quizzes_seeded": 0,
        "errors": []
    }

    # Validate chapters
    chapter_files = sorted(CHAPTERS_DIR.glob("chapter-*.json"))
    logger.info(f"Found {len(chapter_files)} chapter files")

    for chapter_file in chapter_files:
        chapter_id = chapter_file.stem

        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)

            if await validate_chapter(chapter_data, chapter_id):
                results["chapters_seeded"] += 1
                logger.info(f"✓ Seeded: {chapter_data['title']}")
            else:
                results["errors"].append(f"Validation failed for {chapter_id}")

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {chapter_file}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error processing {chapter_file}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    # Validate quizzes
    quiz_files = sorted(QUIZZES_DIR.glob("chapter-*-quiz.json"))
    logger.info(f"Found {len(quiz_files)} quiz files")

    for quiz_file in quiz_files:
        quiz_id = quiz_file.stem

        try:
            with open(quiz_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)

            if await validate_quiz(quiz_data, quiz_id):
                results["quizzes_seeded"] += 1
                logger.info(f"✓ Seeded: {quiz_data['title']} ({quiz_data['total_questions']} questions)")
            else:
                results["errors"].append(f"Validation failed for {quiz_id}")

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {quiz_file}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error processing {quiz_file}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    return results


async def seed_r2_storage() -> Dict[str, Any]:
    """
    Seed content to Cloudflare R2 storage.

    Uploads chapter and quiz JSON files to R2 bucket.

    Returns:
        Summary of seeding results
    """
    logger.info("☁️  Seeding to Cloudflare R2...")

    try:
        # Import R2 client
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from app.utils.storage import r2_client

        results = {
            "mode": "r2",
            "chapters_seeded": 0,
            "quizzes_seeded": 0,
            "errors": []
        }

        # Upload chapters
        chapter_files = sorted(CHAPTERS_DIR.glob("chapter-*.json"))

        for chapter_file in chapter_files:
            chapter_id = chapter_file.stem

            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)

                if not await validate_chapter(chapter_data, chapter_id):
                    results["errors"].append(f"Validation failed for {chapter_id}")
                    continue

                # Upload to R2
                object_key = f"chapters/{chapter_id}.json"
                success = await r2_client.upload_json(object_key, chapter_data)

                if success:
                    results["chapters_seeded"] += 1
                    logger.info(f"✓ Uploaded to R2: {chapter_data['title']}")
                else:
                    results["errors"].append(f"R2 upload failed for {chapter_id}")

            except Exception as e:
                error_msg = f"Error uploading {chapter_file}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Upload quizzes
        quiz_files = sorted(QUIZZES_DIR.glob("chapter-*-quiz.json"))

        for quiz_file in quiz_files:
            quiz_id = quiz_file.stem

            try:
                with open(quiz_file, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)

                if not await validate_quiz(quiz_data, quiz_id):
                    results["errors"].append(f"Validation failed for {quiz_id}")
                    continue

                # Upload to R2
                object_key = f"quizzes/{quiz_id}.json"
                success = await r2_client.upload_json(object_key, quiz_data)

                if success:
                    results["quizzes_seeded"] += 1
                    logger.info(f"✓ Uploaded to R2: {quiz_data['title']}")
                else:
                    results["errors"].append(f"R2 upload failed for {quiz_id}")

            except Exception as e:
                error_msg = f"Error uploading {quiz_file}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        return results

    except ImportError as e:
        logger.error(f"Failed to import R2 client: {e}")
        return {
            "mode": "r2",
            "chapters_seeded": 0,
            "quizzes_seeded": 0,
            "errors": [f"R2 client import failed: {e}"]
        }


async def main():
    """Main seeding orchestrator."""
    logger.info("=" * 60)
    logger.info("Content Seeding Script")
    logger.info("=" * 60)
    logger.info(f"Storage mode: {STORAGE_MODE}")
    logger.info(f"Content directory: {CONTENT_DIR}")
    logger.info("")

    # Check if content directories exist
    if not CHAPTERS_DIR.exists():
        logger.error(f"Chapters directory not found: {CHAPTERS_DIR}")
        return

    if not QUIZZES_DIR.exists():
        logger.error(f"Quizzes directory not found: {QUIZZES_DIR}")
        return

    # Run seeding based on storage mode
    if STORAGE_MODE == "local":
        results = await seed_local_storage()
    elif STORAGE_MODE == "r2":
        results = await seed_r2_storage()
    else:
        logger.error(f"Unknown storage mode: {STORAGE_MODE}")
        logger.error("Valid modes: 'local' or 'r2'")
        return

    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Seeding Summary")
    logger.info("=" * 60)
    logger.info(f"Mode: {results['mode']}")
    logger.info(f"Chapters seeded: {results['chapters_seeded']}")
    logger.info(f"Quizzes seeded: {results['quizzes_seeded']}")
    logger.info(f"Errors: {len(results['errors'])}")

    if results['errors']:
        logger.error("\nErrors encountered:")
        for error in results['errors']:
            logger.error(f"  - {error}")
        logger.info("\n❌ Seeding completed with errors")
    else:
        logger.info("\n✅ Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
