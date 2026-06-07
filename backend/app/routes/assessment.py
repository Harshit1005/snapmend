"""Assessment endpoints for pavement condition evaluation."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models import AssessmentResponse, AssessmentSummary, PavementCondition
from app.gemini_service import GeminiAssessmentService
from datetime import datetime
from typing import List, Optional
import base64
import uuid

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

# ── In-memory store (session-scoped, resets on server restart) ──
# Dict[assessment_id -> AssessmentResponse]
_assessments: dict = {}


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
    Evaluate street pavement condition using Gemini Vision API.
    Accepts multipart form data with street info + image file(s).
    """
    try:
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")

        # Read and base64-encode all uploaded images
        encoded_images = []
        for img in images:
            content = await img.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"Image '{img.filename}' is empty")
            encoded = base64.b64encode(content).decode("utf-8")
            encoded_images.append(encoded)

        # Run Gemini assessment with real image data
        condition = await GeminiAssessmentService.assess_pavement(
            images=encoded_images,
            notes=notes,
        )

        # Get raw assessment text for audit log
        raw_assessment = await GeminiAssessmentService.get_raw_assessment(
            images=encoded_images,
            notes=notes,
        )

        # Build response
        assessment_id = str(uuid.uuid4())
        response = AssessmentResponse(
            assessment_id=assessment_id,
            street_segment_id=street_segment_id,
            inspector_name=inspector_name,
            timestamp=datetime.utcnow(),
            pavement_condition=condition,
            raw_assessment=raw_assessment,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            notes=notes or None,
        )

        # Persist to in-memory store
        _assessments[assessment_id] = response

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/list", response_model=List[AssessmentSummary])
async def list_assessments(limit: int = 20):
    """
    List all assessments (most recent first).
    Used by Dashboard to populate the recent assessments feed.
    """
    all_assessments = list(_assessments.values())
    # Sort newest first
    all_assessments.sort(key=lambda a: a.timestamp, reverse=True)
    # Return summaries
    summaries = [
        AssessmentSummary(
            assessment_id=a.assessment_id,
            street_segment_id=a.street_segment_id,
            inspector_name=a.inspector_name,
            timestamp=a.timestamp,
            severity_level=a.pavement_condition.severity_level,
            repair_priority=a.pavement_condition.repair_priority,
            estimated_cost_inr=a.pavement_condition.estimated_cost_inr,
            damage_types=a.pavement_condition.damage_types,
        )
        for a in all_assessments[:limit]
    ]
    return summaries


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: str):
    """Get a single assessment by ID."""
    if assessment_id not in _assessments:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found")
    return _assessments[assessment_id]


@router.get("/health", response_model=dict)
async def assessment_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "assessment",
        "assessments_in_memory": len(_assessments),
    }
