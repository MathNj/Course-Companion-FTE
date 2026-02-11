"""
Course Companion FTE - Main Application

FastAPI application entry point for Phase 1 (Zero-Backend-LLM).
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth_router
from app.routers.chapters import router as chapters_router
from app.routers.quizzes import router as quizzes_router
from app.routers.progress import router as progress_router
from app.routers.payments import router as payments_router
from app.routers.chat import router as chat_router
from app.routers.milestones import router as milestones_router
from app.utils.cache import cache_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for database connections,
    cache initialization, and cleanup.
    """
    # Startup
    logger.info("Starting Course Companion FTE backend...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"API Version: v1")

    # Initialize Redis cache
    await cache_client.connect()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Disconnect Redis cache
    await cache_client.disconnect()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=(
        "Digital Full-Time Equivalent Educational Tutor for Generative AI Fundamentals. "
        "Phase 1: Zero-Backend-LLM architecture with dual-frontend support (ChatGPT App + Web App)."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    servers=[
        {
            "url": "https://course-companion-fte.fly.dev",
            "description": "Production server"
        }
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "phase": "Phase 1 - Zero-Backend-LLM",
        "environment": settings.app_env,
        "docs": "/api/docs",
        "health": "/health",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns application health status and component availability.
    """
    health_status = {
        "status": "healthy",
        "environment": settings.app_env,
        "components": {
            "api": "operational",
            "cache": "operational" if cache_client.is_connected() else "degraded",
        }
    }

    # Determine overall status
    # API is operational even if optional cache is degraded
    if health_status["components"]["cache"] == "degraded":
        health_status["status"] = "degraded"
        # But still return 200 OK since API is working
        # Cache is optional for functionality
        status_code = 200
    else:
        status_code = 200

    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


# Include routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(chapters_router, prefix=settings.api_v1_prefix)
app.include_router(quizzes_router, prefix=settings.api_v1_prefix)
app.include_router(progress_router, prefix=settings.api_v1_prefix)
app.include_router(milestones_router, prefix=settings.api_v1_prefix)
app.include_router(payments_router, prefix=settings.api_v1_prefix)
app.include_router(chat_router, prefix="/api/v1/chat")
from app.api.v1.bookmarks import router as bookmarks_router
app.include_router(bookmarks_router, prefix=settings.api_v1_prefix)

# Phase 2: Hybrid Intelligence (v2 routers)
from app.api.v2.adaptive import router as adaptive_router
from app.api.v2.teacher import router as teacher_router
from app.api.v2.usage import router as usage_router
from app.api.v2.assessments import router as assessments_router
# from app.api.v2.access import router as access_router  # TODO: Create access router
app.include_router(adaptive_router, prefix="/api/v2")
app.include_router(teacher_router, prefix="/api/v2")
app.include_router(usage_router, prefix="/api/v2")
app.include_router(assessments_router, prefix="/api/v2")
# app.include_router(access_router, prefix="/api/v2")  # TODO: Create access router


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Logs errors and returns a generic 500 response in production.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # In development, return detailed error
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )

    # In production, return generic error
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
