"""
Main FastAPI application for XYZ Plot Studio.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import router
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting XYZ Plot Studio backend...")

    settings = get_settings()

    # Create output directories
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    # Initialize services
    try:
        from app.services import get_enum_service

        enum_service = get_enum_service()
        await enum_service.initialize()
        logger.info("ComfyScript enums initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ComfyScript: {e}")
        logger.warning("Continuing without ComfyScript - some features will be unavailable")

    logger.info("XYZ Plot Studio backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down XYZ Plot Studio backend...")


# Create FastAPI app
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="XYZ Plot Studio API",
        description="API for systematic hyperparameter exploration in ComfyUI",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(router, prefix="/api/v1", tags=["api"])

    # Mount static files (for serving generated images)
    output_dir = Path(settings.output_dir)
    if output_dir.exists():
        app.mount("/outputs", StaticFiles(directory=str(output_dir)), name="outputs")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
