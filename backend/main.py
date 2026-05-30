"""SnapMend Backend API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import assessment, repair

# Initialize FastAPI app
app = FastAPI(
    title="SnapMend API",
    description="Municipal street pavement assessment and repair management system",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "gcp_project": settings.gcp_project_id,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
