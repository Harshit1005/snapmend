"""Repair history and work order endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.models import RepairHistoryEntry, NearbyStreets, WorkOrder
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/repair", tags=["repair"])


@router.get("/history/{street_segment_id}", response_model=List[RepairHistoryEntry])
async def get_repair_history(street_segment_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get repair history for a street segment from BigQuery.

    Args:
        street_segment_id: Street segment identifier
        limit: Maximum number of records to return

    Returns:
        List of repair history entries
    """
    try:
        # TODO: Query BigQuery repair_history table
        # For now, return sample data
        return [
            RepairHistoryEntry(
                repair_id="REP001",
                street_segment_id=street_segment_id,
                date_completed="2023-06-15",
                repair_type="pothole_patching",
                cost=450.00,
                contractor="City Public Works",
                notes="Filled 3 potholes on segment",
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/nearby", response_model=List[NearbyStreets])
async def get_nearby_streets(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_meters: int = Query(500, ge=100, le=5000),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get nearby streets within radius using BigQuery geospatial queries.

    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius_meters: Search radius in meters
        limit: Maximum number of results

    Returns:
        List of nearby streets with condition status
    """
    try:
        # TODO: Query BigQuery with ST_DISTANCE for geospatial proximity
        # For now, return sample data
        return [
            NearbyStreets(
                street_id="STR001",
                street_name="Main Street",
                distance_meters=250,
                last_inspection_date="2024-05-15",
                condition_status="MEDIUM",
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nearby streets: {str(e)}")


@router.post("/work-order", response_model=WorkOrder)
async def create_work_order(
    street_segment_id: str,
    priority_level: str,
    estimated_cost: float,
):
    """
    Create a work order for street repair.

    Args:
        street_segment_id: Street segment to repair
        priority_level: URGENT, HIGH, MEDIUM, LOW
        estimated_cost: Estimated repair cost

    Returns:
        Created work order with ID
    """
    try:
        # TODO: Insert into BigQuery work_orders table
        # For now, return sample data
        work_order = WorkOrder(
            work_order_id="WO" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            street_segment_id=street_segment_id,
            priority_level=priority_level,
            estimated_cost=estimated_cost,
            created_date=datetime.utcnow(),
            status="PENDING",
        )
        return work_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create work order: {str(e)}")


@router.get("/health")
async def repair_health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "repair"}
