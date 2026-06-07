"""Repair history and work order endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.models import RepairHistoryEntry, NearbyStreets, WorkOrder, WorkOrderCreate
from datetime import datetime
from typing import List
import uuid

router = APIRouter(prefix="/api/repair", tags=["repair"])

# ── In-memory store for work orders ──
# Dict[work_order_id -> WorkOrder]
_work_orders: dict = {}


@router.get("/history/{street_segment_id}", response_model=List[RepairHistoryEntry])
async def get_repair_history(street_segment_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get repair history for a street segment.
    Returns real work orders for the segment if any exist, otherwise sample data.
    """
    try:
        # Filter work orders that match this street segment
        matching = [
            wo for wo in _work_orders.values()
            if wo.street_segment_id == street_segment_id
        ]

        if matching:
            # Convert work orders to repair history entries
            return [
                RepairHistoryEntry(
                    repair_id=wo.work_order_id,
                    street_segment_id=wo.street_segment_id,
                    date_completed=wo.created_date.strftime("%Y-%m-%d"),
                    repair_type="work_order",
                    cost=wo.estimated_cost,
                    contractor="Assigned Crew" if wo.assigned_crew else "Unassigned",
                    notes=wo.notes,
                )
                for wo in matching[:limit]
            ]

        # Return empty list — no dummy data
        return []
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
    Get nearby streets within radius.
    Returns streets from work orders that have been logged.
    """
    try:
        # Return streets that have work orders (simplified — no actual geospatial calc)
        seen = set()
        results = []
        for wo in _work_orders.values():
            if wo.street_segment_id not in seen:
                seen.add(wo.street_segment_id)
                results.append(
                    NearbyStreets(
                        street_id=wo.street_segment_id,
                        street_name=wo.street_segment_id,
                        distance_meters=100.0,
                        condition_status=wo.priority_level,
                    )
                )
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nearby streets: {str(e)}")


@router.post("/work-order", response_model=WorkOrder)
async def create_work_order(payload: WorkOrderCreate):
    """
    Create a work order for street repair.
    Accepts JSON body with street_segment_id, priority_level, estimated_cost.
    """
    try:
        work_order_id = "WO-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:4].upper()

        work_order = WorkOrder(
            work_order_id=work_order_id,
            street_segment_id=payload.street_segment_id,
            priority_level=payload.priority_level,
            estimated_cost=payload.estimated_cost,
            estimated_cost_inr=round(payload.estimated_cost * 83.5, 2),
            created_date=datetime.utcnow(),
            status="PENDING",
            assessment_id=payload.assessment_id,
            notes=payload.notes,
        )

        # Persist
        _work_orders[work_order_id] = work_order
        return work_order

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create work order: {str(e)}")


@router.get("/work-orders", response_model=List[WorkOrder])
async def list_work_orders(limit: int = Query(50, ge=1, le=200)):
    """List all work orders, most recent first."""
    all_wo = list(_work_orders.values())
    all_wo.sort(key=lambda w: w.created_date, reverse=True)
    return all_wo[:limit]


@router.get("/health", response_model=dict)
async def repair_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "repair",
        "work_orders_in_memory": len(_work_orders),
    }
