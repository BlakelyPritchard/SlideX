"""
SlideX - AI-Powered Slide Repository
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import init_db
from app.api import slides, tags, search

# Create FastAPI app
app = FastAPI(
    title="SlideX API",
    description="AI-powered slide repository for sales teams",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.SLIDES_DIR, exist_ok=True)
os.makedirs(settings.THUMBNAILS_DIR, exist_ok=True)

# Mount static files for serving images
app.mount("/slides", StaticFiles(directory=settings.SLIDES_DIR), name="slides")
app.mount("/thumbnails", StaticFiles(directory=settings.THUMBNAILS_DIR), name="thumbnails")

# Include routers
app.include_router(slides.router, prefix="/api/slides", tags=["slides"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(search.router, prefix="/api/search", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"🚀 SlideX API running on http://{settings.HOST}:{settings.PORT}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SlideX API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Made with Bob
