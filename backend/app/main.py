import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db
from app.routers import sessions, chat, models, artifacts, skills, knowledge

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("lenny_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & pgvector tables on startup
    logger.info("Initializing database schemas and pgvector extension...")
    try:
        await init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down Lenny Growth Assistant backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Grounded AI Product & Growth Assistant powered by Lenny's Podcast transcripts with multi-model switching & Ship 30 essays",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"METHOD={request.method} PATH={request.url.path} STATUS={response.status_code} DURATION={duration:.3f}s"
    )
    return response

# Mount routers under /api/v1
app.include_router(sessions.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(artifacts.router, prefix=settings.API_V1_PREFIX)
app.include_router(skills.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "ai_provider": settings.AI_PROVIDER,
        "default_model": settings.DEFAULT_MODEL
    }

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to The Lenny Growth Assistant API",
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_PREFIX
    }
