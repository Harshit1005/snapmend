"""Assessment endpoints for pavement condition evaluation."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import AssessmentResponse, AssessmentSummary, PavementCondition
from app.gemini_service import GeminiAssessmentService
from app.database import get_db
from app.db_models import AssessmentRow
from datetime import datetime, timezone
from typing import List
import base64
import uuid

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def _row_to_response(row: AssessmentRow) -> AssessmentResponse:
    """Convert a DB row into the API response model."""
    condition = PavementCondition(
        severity_level=row.severity_level,
        damage_types=row.damage_types or [],
        repair_priority=row.repair_priority,
        estimated_cost=row.estimated_cost,
        estimated_cost_inr=row.estimated_cost_inr,
        repair_method=row.repair_method,
        detailed_assessment=row.detailed_assessment,
    )
    return AssessmentResponse(
        assessment_id=row.assessment_id,
        street_segment_id=row.street_segment_id,
        inspector_name=row.inspector_name,
        timestamp=row.timestamp,
        pavement_condition=condition,
        raw_assessment=row.raw_assessment or "",
        photo_urls=row.image_urls or [],
        gps_latitude=row.gps_latitude,
        gps_longitude=row.gps_longitude,
        notes=row.notes,
    )


def _row_to_summary(row: AssessmentRow) -> AssessmentSummary:
    """Convert a DB row into a lightweight summary."""
    return AssessmentSummary(
        assessment_id=row.assessment_id,
        street_segment_id=row.street_segment_id,
        inspector_name=row.inspector_name,
        timestamp=row.timestamp,
        severity_level=row.severity_level,
        repair_priority=row.repair_priority,
        estimated_cost_inr=row.estimated_cost_inr,
        damage_types=row.damage_types or [],
    )


@router.post("/evaluate", response_model=AssessmentResponse)
async def evaluate_pavement(
    street_segment_id: str = Form(...),
    inspector_name: str = Form(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...),
    notes: str = Form(default=""),
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate street pavement condition using Gemini Vision API.
    Accepts multipart form data with street info + image file(s).
    Results are saved to SQLite for persistence across restarts.
    """
    try:
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")

        import os
        import uuid

        assessment_id = str(uuid.uuid4())

        # Read, base64-encode, and save all uploaded images
        encoded_images = []
        image_urls = []
        for i, img in enumerate(images):
            content = await img.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"Image '{img.filename}' is empty")
            encoded = base64.b64encode(content).decode("utf-8")
            encoded_images.append(encoded)

            # Save to disk
            ext = os.path.splitext(img.filename)[1] if img.filename else ".jpg"
            if not ext: ext = ".jpg"
            filename = f"{assessment_id}_{i}{ext}"
            filepath = os.path.join("uploads", filename)
            with open(filepath, "wb") as out_file:
                out_file.write(content)
            image_urls.append(f"/uploads/{filename}")

        # Run Gemini assessment with real image data
        condition = await GeminiAssessmentService.assess_pavement(
            images=encoded_images,
            notes=notes,
            lat=gps_latitude,
            lon=gps_longitude,
        )

        if not any("pothole" in d.lower() for d in condition.damage_types):
            raise HTTPException(
                status_code=400,
                detail="This is not a pothole. Please try again after finding a pothole."
            )

        # Get raw assessment text for audit log
        raw_assessment = await GeminiAssessmentService.get_raw_assessment(
            images=encoded_images,
            notes=notes,
            lat=gps_latitude,
            lon=gps_longitude,
        )

        # Build and persist to SQLite
        now = datetime.now(timezone.utc)

        row = AssessmentRow(
            assessment_id=assessment_id,
            street_segment_id=street_segment_id,
            inspector_name=inspector_name,
            timestamp=now,
            severity_level=condition.severity_level,
            damage_types=condition.damage_types,
            image_urls=image_urls,
            repair_priority=condition.repair_priority,
            estimated_cost=condition.estimated_cost,
            estimated_cost_inr=condition.estimated_cost_inr,
            repair_method=condition.repair_method,
            detailed_assessment=condition.detailed_assessment,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            notes=notes or None,
            raw_assessment=raw_assessment,
        )
        db.add(row)
        await db.flush()

        return AssessmentResponse(
            assessment_id=assessment_id,
            street_segment_id=street_segment_id,
            inspector_name=inspector_name,
            timestamp=now,
            pavement_condition=condition,
            raw_assessment=raw_assessment,
            photo_urls=image_urls,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            notes=notes or None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/list", response_model=List[AssessmentSummary])
async def list_assessments(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    List all assessments (most recent first).
    Used by Dashboard to populate the recent assessments feed.
    """
    result = await db.execute(
        select(AssessmentRow).order_by(desc(AssessmentRow.timestamp)).limit(limit)
    )
    rows = result.scalars().all()
    return [_row_to_summary(r) for r in rows]


@router.get("/stats", response_model=dict)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Aggregate stats for Dashboard header cards.
    Returns total count, severity breakdown, average cost.
    """
    result = await db.execute(select(AssessmentRow))
    rows = result.scalars().all()

    if not rows:
        return {
            "total": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "avg_cost_inr": 0,
        }

    high = sum(1 for r in rows if r.severity_level == "HIGH")
    medium = sum(1 for r in rows if r.severity_level == "MEDIUM")
    low = sum(1 for r in rows if r.severity_level == "LOW")
    costs = [r.estimated_cost_inr for r in rows if r.estimated_cost_inr]
    avg_cost = round(sum(costs) / len(costs)) if costs else 0

    return {
        "total": len(rows),
        "high_severity": high,
        "medium_severity": medium,
        "low_severity": low,
        "avg_cost_inr": avg_cost,
    }


@router.get("/health", response_model=dict)
async def assessment_health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    result = await db.execute(select(AssessmentRow))
    count = len(result.scalars().all())
    return {
        "status": "healthy",
        "service": "assessment",
        "assessments_in_db": count,
    }


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single assessment by ID."""
    result = await db.execute(
        select(AssessmentRow).where(AssessmentRow.assessment_id == assessment_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found")
    return _row_to_response(row)
