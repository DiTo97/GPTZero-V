"""FastAPI application and routes."""

import logging
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from gptzero_api import __version__
from gptzero_api.models import (
    ErrorResponse,
    HealthResponse,
    VerifyImageResponse,
)
from gptzero_api.service import VerificationService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def log_request(method: str, path: str, status: int, duration: float) -> None:
    """Log HTTP requests in a structured way.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: request path
        status: HTTP status code
        duration: request duration in milliseconds
    """
    log_details = {
        "method": method,
        "path": path,
        "status": status,
        "duration": round(duration, 2),
    }
    logger.info(str(log_details))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    logger.info("Starting GPTZero-V API service")
    yield
    logger.info("Shutting down GPTZero-V API service")


def make_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GPTZero-V API",
        description="API for image authenticity verification",
        version=__version__,
        lifespan=lifespan,
        redoc_url=None,
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=["*"],
    )

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Log HTTP requests with timing information."""
        start = time.perf_counter()

        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000

        log_request(
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration=duration,
        )

        response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        return response

    # Initialize service
    verification_service = VerificationService()

    @app.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(status="ok", version=__version__)

    @app.post(
        "/v1/verify",
        response_model=VerifyImageResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Bad request"},
            500: {"model": ErrorResponse, "description": "Internal server error"},
        },
    )
    async def verify_image(
        file: Annotated[UploadFile, File(description="Image file to verify")],
    ) -> VerifyImageResponse:
        """
        Verify image authenticity.

        Analyzes uploaded image for C2PA and EXIF metadata to determine
        authenticity probability.
        """
        # Validate content type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read file data
        try:
            file_data = await file.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise HTTPException(status_code=400, detail="Error reading file") from e

        # Verify image
        try:
            result = verification_service.verify_image(
                data=file_data,
                mime_type=file.content_type,
                filename=file.filename,
            )
            return result
        except Exception as e:
            logger.error(f"Error verifying image: {e}")
            raise HTTPException(status_code=500, detail="Error verifying image") from e

    return app


app = make_app()


def main() -> None:
    """Entry point for running the API with uvicorn."""
    import uvicorn

    uvicorn.run(
        "gptzero_api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
