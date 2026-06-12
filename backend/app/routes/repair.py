"""Repair history and work order endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import RepairHistoryEntry, NearbyStreets, WorkOrder, WorkOrderCreate
from app.database import get_supabase
from datetime import datetime, timezone
from typing import List
import uuid

router = APIRouter(prefix="/api/repair", tags=["repair"])


def _dict_to_work_order(data: dict) -> WorkOrder:
    created_date = data.get("created_date")
    if isinstance(created_date, str):
        try:
            created_date = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
        except ValueError:
            created_date = datetime.now(timezone.utc)
    else:
        created_date = datetime.now(timezone.utc)
        
    return WorkOrder(
        work_order_id=data.get("work_order_id"),
        street_segment_id=data.get("street_segment_id"),
        priority_level=data.get("priority_level"),
        estimated_cost=data.get("estimated_cost"),
        estimated_cost_inr=data.get("estimated_cost_inr"),
        created_date=created_date,
        assigned_crew=data.get("assigned_crew"),
        status=data.get("status", "PENDING"),
        assessment_id=data.get("assessment_id"),
        notes=data.get("notes"),
    )


@router.get("/history/{street_segment_id}", response_model=List[RepairHistoryEntry])
async def get_repair_history(
    street_segment_id: str,
    limit: int = Query(10, ge=1, le=100),
    supabase = Depends(get_supabase),
):
    """
    Get repair history for a street segment.
    Returns work orders that have been created for this segment.
    """
    try:
        response = supabase.table("work_orders").select("*").eq("street_segment_id", street_segment_id).order("created_date", desc=True).limit(limit).execute()
        rows = response.data

        return [
            RepairHistoryEntry(
                repair_id=row.get("work_order_id"),
                street_segment_id=row.get("street_segment_id"),
                date_completed=row.get("created_date")[:10] if row.get("created_date") else "Unknown",
                repair_type="work_order",
                cost=row.get("estimated_cost"),
                contractor="Assigned Crew" if row.get("assigned_crew") else "Unassigned",
                notes=row.get("notes"),
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/nearby", response_model=List[NearbyStreets])
async def get_nearby_streets(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_meters: int = Query(500, ge=100, le=5000),
    limit: int = Query(10, ge=1, le=50),
    supabase = Depends(get_supabase),
):
    """
    Get nearby streets with work orders.
    Simplified — returns unique street segments from work orders.
    """
    try:
        response = supabase.table("work_orders").select("*").order("created_date", desc=True).execute()
        rows = response.data

        seen = set()
        results = []
        for row in rows:
            seg_id = row.get("street_segment_id")
            if seg_id not in seen:
                seen.add(seg_id)
                results.append(
                    NearbyStreets(
                        street_id=seg_id,
                        street_name=seg_id,
                        distance_meters=100.0,
                        condition_status=row.get("priority_level"),
                    )
                )
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nearby streets: {str(e)}")


@router.post("/work-order", response_model=WorkOrder)
async def create_work_order(
    payload: WorkOrderCreate,
    supabase = Depends(get_supabase),
):
    """
    Create a work order for street repair.
    Saved to Supabase.
    """
    try:
        work_order_id = (
            "WO-"
            + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            + "-"
            + str(uuid.uuid4())[:4].upper()
        )
        now = datetime.now(timezone.utc).isoformat()
        inr_cost = round(payload.estimated_cost * 83.5, 2)

        row_data = {
            "work_order_id": work_order_id,
            "street_segment_id": payload.street_segment_id,
            "priority_level": payload.priority_level,
            "estimated_cost": payload.estimated_cost,
            "estimated_cost_inr": inr_cost,
            "created_date": now,
            "status": "PENDING",
            "assessment_id": payload.assessment_id,
            "notes": payload.notes,
            "assigned_crew": "Pending Assignment",
        }
        
        response = supabase.table("work_orders").insert(row_data).execute()
        if not response.data:
            raise Exception("Failed to insert work order to Supabase")

        return _dict_to_work_order(response.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create work order: {str(e)}")


@router.get("/work-orders", response_model=List[WorkOrder])
async def list_work_orders(
    limit: int = Query(50, ge=1, le=200),
    supabase = Depends(get_supabase),
):
    """List all work orders, most recent first."""
    response = supabase.table("work_orders").select("*").order("created_date", desc=True).limit(limit).execute()
    return [_dict_to_work_order(r) for r in response.data]


@router.get("/health", response_model=dict)
async def repair_health(supabase = Depends(get_supabase)):
    """Health check endpoint."""
    response = supabase.table("work_orders").select("work_order_id", count="exact").limit(1).execute()
    return {
        "status": "healthy",
        "service": "repair",
        "work_orders_in_db": response.count if hasattr(response, 'count') else 0,
    }
