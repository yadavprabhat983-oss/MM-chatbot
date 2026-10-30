from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import AppBaseException
from app.db.session import init_db_schema
from app.api.routes import health, conversations, chat, documents, search

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Multimodal AI Assistant Backend...")
    # Initialize DB tables on startup
    init_db_schema()
    yield
    logger.info("Shutting down Multimodal AI Assistant Backend...")

app = FastAPI(
    title="Multimodal AI Personal Assistant API",
    description="Backend API supporting multimodal chat, RAG vector retrieval, web search, document management, and emotional support.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Domain Exception Handler
@app.exception_handler(AppBaseException)
async def app_base_exception_handler(request: Request, exc: AppBaseException):
    logger.warning(f"Domain exception on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "error_type": "InternalServerError"}
    )

# Include Routers
app.include_router(health.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(search.router)

@app.get("/")
def root():
    return {
        "name": "Multimodal AI Personal Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "provider": settings.AI_PROVIDER
    }
