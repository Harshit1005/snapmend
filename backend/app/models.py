from pydantic import BaseModel, Field, model_validator
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


class DistressDimensions(BaseModel):
    """Estimated dimensions of the distress."""
    length_m: Optional[float] = Field(None, description="Length of damage in meters")
    width_m: Optional[float] = Field(None, description="Width of damage in meters")
    depth_cm: Optional[float] = Field(None, description="Depth of damage in centimeters")


class DetectedDistress(BaseModel):
    """Pavement distress object detected in the image."""
    type: str = Field(description="pothole, cracking, rutting, raveling, etc.")
    severity: str = Field(description="LOW, MEDIUM, or HIGH")
    box_2d: List[float] = Field(description="Bounding box coordinates [ymin, xmin, ymax, xmax] normalized to [0, 1000]")
    confidence: float = Field(description="Detection confidence score between 0 and 1")
    estimated_dimensions: Optional[DistressDimensions] = None


class CostBreakdown(BaseModel):
    """Detailed repair cost breakdown in USD and INR."""
    materials: float = Field(description="Materials cost in USD")
    labor: float = Field(description="Labor cost in USD")
    machinery: float = Field(description="Machinery cost in USD")
    total: float = Field(description="Total cost in USD")
    materials_inr: Optional[float] = None
    labor_inr: Optional[float] = None
    machinery_inr: Optional[float] = None
    total_inr: Optional[float] = None


class EngineeringJustification(BaseModel):
    """Detailed engineering justification for the repair decision."""
    observed_defects: str = Field(description="Description of the defects observed in the image")
    base_failure_risk: str = Field(description="Assessment of risk to the road base structure")
    traffic_impact: str = Field(description="Potential impact on local traffic and safety hazard")


class PavementCondition(BaseModel):
    """Pavement condition assessment result from Gemini."""
    severity_level: str = Field(description="LOW, MEDIUM, or HIGH")
    damage_types: List[str] = Field(description="List of damage types detected")
    repair_priority: int = Field(description="Priority score 1-10")
    estimated_cost: Optional[float] = Field(None, description="Estimated repair cost in USD")
    estimated_cost_inr: Optional[float] = Field(None, description="Estimated repair cost in INR")
    repair_method: Optional[str] = Field(None, description="Recommended repair method")
    detailed_assessment: Optional[str] = Field(None, description="Full Gemini assessment text")
    
    # New fields for advanced AI pipeline
    detected_distresses: Optional[List[DetectedDistress]] = None
    cost_breakdown: Optional[CostBreakdown] = None
    engineering_justification: Optional[EngineeringJustification] = None
    step_by_step_plan: Optional[List[str]] = None

    @model_validator(mode='after')
    def reconcile_and_validate(self) -> 'PavementCondition':
        # 1. Bounding box coordinates and confidence validation
        valid_distresses = []
        if self.detected_distresses:
            for distress in self.detected_distresses:
                # check box_2d has length 4
                if not distress.box_2d or len(distress.box_2d) != 4:
                    continue
                ymin, xmin, ymax, xmax = distress.box_2d
                # check bounds [0, 1000]
                if not (0 <= ymin <= 1000 and 0 <= xmin <= 1000 and 0 <= ymax <= 1000 and 0 <= xmax <= 1000):
                    continue
                # check orientation
                if ymin >= ymax or xmin >= xmax:
                    continue
                # check confidence
                if not (0.0 <= distress.confidence <= 1.0):
                    distress.confidence = max(0.0, min(1.0, distress.confidence))
                valid_distresses.append(distress)
            self.detected_distresses = valid_distresses

        # 2. Cost breakdown validation and reconciliation
        if self.cost_breakdown:
            cb = self.cost_breakdown
            # If total is not provided or 0, calculate it
            if cb.total <= 0:
                cb.total = cb.materials + cb.labor + cb.machinery
            
            # If materials + labor + machinery != total, adjust total to be the exact sum of parts
            sum_parts = cb.materials + cb.labor + cb.machinery
            if abs(sum_parts - cb.total) > 0.01:
                cb.total = sum_parts

            # Set self.estimated_cost to match the total in cost_breakdown
            self.estimated_cost = cb.total

        # 3. Ensure INR cost matching
        if self.estimated_cost is not None:
            self.estimated_cost_inr = round(self.estimated_cost * 83.5, 2)
            if self.cost_breakdown:
                cb = self.cost_breakdown
                cb.materials_inr = round(cb.materials * 83.5, 2)
                cb.labor_inr = round(cb.labor * 83.5, 2)
                cb.machinery_inr = round(cb.machinery * 83.5, 2)
                cb.total_inr = self.estimated_cost_inr

        return self


class AssessmentResponse(BaseModel):
    """Complete assessment response."""
    assessment_id: str
    street_segment_id: str
    inspector_name: str
    timestamp: datetime
    pavement_condition: PavementCondition
    raw_assessment: str = Field(..., description="Full Gemini assessment JSON text")
    photo_urls: Optional[List[str]] = Field(None, description="Uploaded photo URLs")
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    notes: Optional[str] = None


class AssessmentSummary(BaseModel):
    """Lightweight summary for listing assessments on Dashboard."""
    assessment_id: str
    street_segment_id: str
    inspector_name: str
    timestamp: datetime
    severity_level: str
    repair_priority: int
    estimated_cost_inr: Optional[float] = None
    damage_types: List[str] = []


class RepairHistoryEntry(BaseModel):
    """Historical repair record."""
    repair_id: str
    street_segment_id: str
    date_completed: str
    repair_type: str
    cost: float
    contractor: str
    notes: Optional[str] = None


class NearbyStreets(BaseModel):
    """Nearby streets from geospatial query."""
    street_id: str
    street_name: str
    distance_meters: float
    last_inspection_date: Optional[str] = None
    condition_status: Optional[str] = None


class WorkOrderCreate(BaseModel):
    """Request body for creating a work order."""
    street_segment_id: str
    priority_level: str
    estimated_cost: float
    assessment_id: Optional[str] = None
    notes: Optional[str] = None


class WorkOrder(BaseModel):
    """Work order for repair scheduling."""
    work_order_id: str
    street_segment_id: str
    priority_level: str
    estimated_cost: float
    estimated_cost_inr: Optional[float] = None
    created_date: datetime
    assigned_crew: Optional[str] = None
    status: str = "PENDING"
    assessment_id: Optional[str] = None
    notes: Optional[str] = None
