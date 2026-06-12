"""SnapMend Backend API - Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import assessment, repair



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    await init_db()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="SnapMend API",
    description="Municipal street pavement assessment and repair management system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Mount static directory for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Include route modules
app.include_router(assessment.router)
app.include_router(repair.router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "SnapMend Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "assessment": "/api/assessment/evaluate",
            "assessment_list": "/api/assessment/list",
            "assessment_stats": "/api/assessment/stats",
            "repair_history": "/api/repair/history/{street_segment_id}",
            "nearby_streets": "/api/repair/nearby",
            "work_orders": "/api/repair/work-order",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "snapmend-backend",
        "gemini_api_configured": bool(settings.gemini_api_key),
        "database": "supabase",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

