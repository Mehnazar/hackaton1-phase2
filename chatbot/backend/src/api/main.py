"""FastAPI application for RAG Chatbot backend."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from ..utils.qdrant_client import get_qdrant_client
from .middleware import error_handler_middleware, request_logger_middleware
from .routes import admin, auth, book, chat

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Handles:
    - Qdrant client initialization and health check
    - Collection creation/validation
    - Auth service database pool initialization
    - Graceful shutdown cleanup
    """
    # Startup
    logger.info("Starting RAG Chatbot backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Logging enabled: {settings.enable_logging}")

    # Initialize Qdrant client
    qdrant = get_qdrant_client()

    # Health check
    if not qdrant.health_check():
        logger.error("Qdrant health check failed - continuing with degraded service")
    else:
        # Ensure collection exists
        if not qdrant.ensure_collection():
            logger.error("Failed to ensure Qdrant collection - indexing may not work")

    logger.info("RAG Chatbot backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot backend...")
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="""
    **Retrieval-Augmented Generation (RAG) Chatbot for AI-Native Software Development Book**

    This API provides endpoints for:
    - Book-wide semantic search and question answering
    - Selected-text-only answering (no retrieval)
    - Deterministic refusal when evidence is insufficient
    - Full source citation and traceability

    ### Modes
    - **book-wide**: Searches entire book using semantic retrieval (Qdrant)
    - **selected-text**: Answers only from user-provided text (no retrieval)

    ### Constitutional Principles
    1. **Grounded Accuracy**: All answers derived from book content only
    2. **Faithful Retrieval**: Strict mode isolation
    3. **Transparency**: Full source citations for every answer
    4. **Academic Rigor**: CS-appropriate explanations
    5. **Deterministic Refusal**: Explicit refusal when evidence insufficient
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {settings.allowed_origins_list}")

# Add custom middleware
app.middleware("http")(request_logger_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(chat.router)


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.environment,
        "modes": ["book-wide", "selected-text"],
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Health status including Qdrant connectivity
    """
    qdrant = get_qdrant_client()
    qdrant_healthy = qdrant.health_check()
    collection_info = qdrant.get_collection_info()

    return {
        "status": "healthy" if qdrant_healthy else "degraded",
        "qdrant": {
            "connected": qdrant_healthy,
            "collection": collection_info if collection_info else "unavailable",
        },
    }
