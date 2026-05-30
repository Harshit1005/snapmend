"""Data models for SnapMend API."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AssessmentRequest(BaseModel):
    """Street inspection assessment request."""

    street_segment_id: str = Field(..., description="Unique identifier for street segment")
    images: List[str] = Field(..., description="Base64-encoded street images")
    inspector_name: str = Field(..., description="Name of inspector")
    gps_latitude: float = Field(..., description="GPS latitude of assessment")
    gps_longitude: float = Field(..., description="GPS longitude of assessment")
    notes: Optional[str] = Field(None, description="Additional inspection notes")


class PavementCondition(BaseModel):
    """Pavement condition assessment result."""

    severity_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    damage_types: List[str] = Field(..., description="List of damage types detected")
    repair_priority: int = Field(..., description="Priority score 1-10")
    estimated_cost: Optional[float] = Field(None, description="Estimated repair cost in USD")
    repair_method: Optional[str] = Field(None, description="Recommended repair method")


class AssessmentResponse(BaseModel):
    """Complete assessment response."""

    assessment_id: str
    street_segment_id: str
    timestamp: datetime
    pavement_condition: PavementCondition
    raw_assessment: str = Field(..., description="Full Gemini assessment text")
    photo_urls: Optional[List[str]] = Field(None, description="Uploaded photo URLs in GCS")


class RepairHistoryEntry(BaseModel):
    """Historical repair record from BigQuery."""

    repair_id: str
    street_segment_id: str
    date_completed: str
    repair_type: str
    cost: float
    contractor: str
    notes: Optional[str] = None


class NearbyStreets(BaseModel):
    """Nearby streets from BigQuery geospatial query."""

    street_id: str
    street_name: str
    distance_meters: float
    last_inspection_date: Optional[str] = None
    condition_status: Optional[str] = None


class WorkOrder(BaseModel):
    """Work order for repair scheduling."""

    work_order_id: str
    street_segment_id: str
    priority_level: str
    estimated_cost: float
    created_date: datetime
    assigned_crew: Optional[str] = None
    status: str = "PENDING"
