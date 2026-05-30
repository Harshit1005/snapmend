"""Assessment endpoints for pavement condition evaluation."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models import AssessmentRequest, AssessmentResponse, PavementCondition
from app.gemini_service import GeminiAssessmentService
from datetime import datetime
import base64
from typing import List
import uuid

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.post("/evaluate", response_model=AssessmentResponse)
async def evaluate_pavement(
    street_segment_id: str = Form(...),
    inspector_name: str = Form(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...),
    notes: str = Form(default=""),
    images: List[UploadFile] = File(...),
):
    """
    Evaluate street pavement condition using Gemini API.

    Args:
        street_segment_id: Unique street segment identifier
        inspector_name: Name of inspecting officer
        gps_latitude: GPS latitude coordinate
        gps_longitude: GPS longitude coordinate
        notes: Optional inspection notes
        images: List of pavement photographs

    Returns:
        AssessmentResponse with condition analysis
    """
    try:
        # Validate inputs
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image required")

        # Read and encode images
        encoded_images = []
        for img in images:
            content = await img.read()
            encoded = base64.b64encode(content).decode("utf-8")
            encoded_images.append(encoded)

        # Get assessment from Gemini
        condition = await GeminiAssessmentService.assess_pavement(
            images=encoded_images, notes=notes
        )

        # Get raw assessment for logging
        raw_assessment = await GeminiAssessmentService.get_raw_assessment(
            images=encoded_images, notes=notes
        )

        # Create response
        assessment_id = str(uuid.uuid4())
        response = AssessmentResponse(
            assessment_id=assessment_id,
            street_segment_id=street_segment_id,
            timestamp=datetime.utcnow(),
            pavement_condition=condition,
            raw_assessment=raw_assessment,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/health")
async def assessment_health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "assessment"}
