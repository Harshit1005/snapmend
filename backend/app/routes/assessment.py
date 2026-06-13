"""Assessment endpoints for pavement condition evaluation."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from app.models import AssessmentResponse, AssessmentSummary, PavementCondition
from app.gemini_service import GeminiAssessmentService
from app.database import get_firestore
from google.cloud import firestore
from datetime import datetime, timezone
from typing import List
import base64
import uuid

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def _dict_to_response(data: dict) -> AssessmentResponse:
    """Convert a Supabase row dict into the API response model."""
    import json
    raw_str = data.get("raw_assessment", "")
    new_fields = {}
    if raw_str:
        try:
            raw_data = json.loads(raw_str)
            
            # Map box_2d coordinate from native [0, 1000] scale to percentage [0, 100] scale
            distresses = raw_data.get("detected_distresses")
            if distresses:
                mapped_distresses = []
                for distress in distresses:
                    box = distress.get("box_2d")
                    if box and len(box) == 4:
                        # Convert coordinates from 0-1000 to 0-100 percent
                        mapped_box = [round(coord / 10.0, 2) for coord in box]
                        # Create a copy to avoid mutating cache/original object
                        distress_copy = dict(distress)
                        distress_copy["box_2d"] = mapped_box
                        mapped_distresses.append(distress_copy)
                    else:
                        mapped_distresses.append(distress)
                new_fields["detected_distresses"] = mapped_distresses
            else:
                new_fields["detected_distresses"] = []

            new_fields["cost_breakdown"] = raw_data.get("cost_breakdown")
            new_fields["engineering_justification"] = raw_data.get("engineering_justification")
            new_fields["step_by_step_plan"] = raw_data.get("step_by_step_plan")
        except Exception as e:
            print("Warning: failed to parse raw_assessment fields:", e)

    condition = PavementCondition(
        severity_level=data.get("severity_level", "LOW"),
        damage_types=data.get("damage_types", []),
        repair_priority=data.get("repair_priority", 1),
        estimated_cost=data.get("estimated_cost"),
        estimated_cost_inr=data.get("estimated_cost_inr"),
        repair_method=data.get("repair_method"),
        detailed_assessment=data.get("detailed_assessment"),
        **new_fields
    )
    # Supabase timestamp format parsing can vary, safely pass it
    timestamp = data.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            timestamp = datetime.now(timezone.utc)
    else:
        timestamp = datetime.now(timezone.utc)
        
    return AssessmentResponse(
        assessment_id=data.get("assessment_id"),
        street_segment_id=data.get("street_segment_id"),
        inspector_name=data.get("inspector_name"),
        timestamp=timestamp,
        pavement_condition=condition,
        raw_assessment=raw_str,
        photo_urls=data.get("image_urls", []),
        gps_latitude=data.get("gps_latitude"),
        gps_longitude=data.get("gps_longitude"),
        notes=data.get("notes"),
    )


def _dict_to_summary(data: dict) -> AssessmentSummary:
    """Convert a Supabase row dict into a lightweight summary."""
    timestamp = data.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            timestamp = datetime.now(timezone.utc)
    else:
        timestamp = datetime.now(timezone.utc)
        
    return AssessmentSummary(
        assessment_id=data.get("assessment_id"),
        street_segment_id=data.get("street_segment_id"),
        inspector_name=data.get("inspector_name"),
        timestamp=timestamp,
        severity_level=data.get("severity_level", "LOW"),
        repair_priority=data.get("repair_priority", 1),
        estimated_cost_inr=data.get("estimated_cost_inr"),
        damage_types=data.get("damage_types", []),
    )


@router.post("/evaluate", response_model=AssessmentResponse)
async def evaluate_pavement(
    street_segment_id: str = Form(...),
    inspector_name: str = Form(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...),
    notes: str = Form(default=""),
    images: List[UploadFile] = File(...),
    db = Depends(get_firestore),
):
    """
    Evaluate street pavement condition using Gemini Vision API.
    Results are saved to Firestore for persistence.
    """
    try:
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")

        import os

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

            # Save to local disk for now (could be moved to Supabase Storage)
            ext = os.path.splitext(img.filename)[1] if img.filename else ".jpg"
            if not ext: ext = ".jpg"
            filename = f"{assessment_id}_{i}{ext}"
            filepath = os.path.join("uploads", filename)
            with open(filepath, "wb") as out_file:
                out_file.write(content)
            image_urls.append(f"/uploads/{filename}")

        # Run grounding research step exactly once per request
        research_report = await GeminiAssessmentService._run_research_step(gps_latitude, gps_longitude)

        # Run Gemini assessment exactly once to get the raw JSON
        raw_assessment = await GeminiAssessmentService.get_raw_assessment(
            images=encoded_images,
            notes=notes,
            research_report=research_report,
        )
        
        # Parse it locally into the Pydantic model
        condition = GeminiAssessmentService.parse_response(raw_assessment)

        now = datetime.now(timezone.utc).isoformat()

        row_data = {
            "assessment_id": assessment_id,
            "street_segment_id": street_segment_id,
            "inspector_name": inspector_name,
            "timestamp": now,
            "severity_level": condition.severity_level,
            "damage_types": condition.damage_types,
            "image_urls": image_urls,
            "repair_priority": condition.repair_priority,
            "estimated_cost": condition.estimated_cost,
            "estimated_cost_inr": condition.estimated_cost_inr,
            "repair_method": condition.repair_method,
            "detailed_assessment": condition.detailed_assessment,
            "gps_latitude": gps_latitude,
            "gps_longitude": gps_longitude,
            "notes": notes or None,
            "raw_assessment": raw_assessment,
        }
        
        db.collection("assessments").document(assessment_id).set(row_data)

        return _dict_to_response(row_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/list", response_model=List[AssessmentSummary])
async def list_assessments(
    limit: int = 20,
    db = Depends(get_firestore),
):
    """List all assessments (most recent first)."""
    docs = db.collection("assessments").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [_dict_to_summary(doc.to_dict()) for doc in docs]


@router.get("/stats", response_model=dict)
async def get_stats(db = Depends(get_firestore)):
    """Aggregate stats for Dashboard header cards."""
    docs = db.collection("assessments").stream()
    rows = [doc.to_dict() for doc in docs]

    if not rows:
        return {
            "total": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "avg_cost_inr": 0,
        }

    high = sum(1 for r in rows if r.get("severity_level") == "HIGH")
    medium = sum(1 for r in rows if r.get("severity_level") == "MEDIUM")
    low = sum(1 for r in rows if r.get("severity_level") == "LOW")
    costs = [r.get("estimated_cost_inr") for r in rows if r.get("estimated_cost_inr")]
    avg_cost = round(sum(costs) / len(costs)) if costs else 0

    return {
        "total": len(rows),
        "high_severity": high,
        "medium_severity": medium,
        "low_severity": low,
        "avg_cost_inr": avg_cost,
    }


@router.get("/health", response_model=dict)
async def assessment_health(db = Depends(get_firestore)):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "assessment",
        "database": "firestore connected",
    }


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    db = Depends(get_firestore),
):
    """Get a single assessment by ID."""
    doc = db.collection("assessments").document(assessment_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found")
    return _dict_to_response(doc.to_dict())
