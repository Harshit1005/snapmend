"""Repair history and work order endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import RepairHistoryEntry, NearbyStreets, WorkOrder, WorkOrderCreate
from app.database import get_db
from app.db_models import WorkOrderRow
from datetime import datetime, timezone
from typing import List
import uuid

router = APIRouter(prefix="/api/repair", tags=["repair"])


def _row_to_work_order(row: WorkOrderRow) -> WorkOrder:
    return WorkOrder(
        work_order_id=row.work_order_id,
        street_segment_id=row.street_segment_id,
        priority_level=row.priority_level,
        estimated_cost=row.estimated_cost,
        estimated_cost_inr=row.estimated_cost_inr,
        created_date=row.created_date,
        assigned_crew=row.assigned_crew,
        status=row.status,
        assessment_id=row.assessment_id,
        notes=row.notes,
    )


@router.get("/history/{street_segment_id}", response_model=List[RepairHistoryEntry])
async def get_repair_history(
    street_segment_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get repair history for a street segment.
    Returns work orders that have been created for this segment.
    """
    try:
        result = await db.execute(
            select(WorkOrderRow)
            .where(WorkOrderRow.street_segment_id == street_segment_id)
            .order_by(desc(WorkOrderRow.created_date))
            .limit(limit)
        )
        rows = result.scalars().all()

        return [
            RepairHistoryEntry(
                repair_id=row.work_order_id,
                street_segment_id=row.street_segment_id,
                date_completed=row.created_date.strftime("%Y-%m-%d"),
                repair_type="work_order",
                cost=row.estimated_cost,
                contractor="Assigned Crew" if row.assigned_crew else "Unassigned",
                notes=row.notes,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get nearby streets with work orders.
    Simplified — returns unique street segments from work orders.
    """
    try:
        result = await db.execute(
            select(WorkOrderRow).order_by(desc(WorkOrderRow.created_date))
        )
        rows = result.scalars().all()

        seen = set()
        results = []
        for row in rows:
            if row.street_segment_id not in seen:
                seen.add(row.street_segment_id)
                results.append(
                    NearbyStreets(
                        street_id=row.street_segment_id,
                        street_name=row.street_segment_id,
                        distance_meters=100.0,
                        condition_status=row.priority_level,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Create a work order for street repair.
    Saved to SQLite — persists across restarts.
    """
    try:
        work_order_id = (
            "WO-"
            + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            + "-"
            + str(uuid.uuid4())[:4].upper()
        )
        now = datetime.now(timezone.utc)
        inr_cost = round(payload.estimated_cost * 83.5, 2)

        row = WorkOrderRow(
            work_order_id=work_order_id,
            street_segment_id=payload.street_segment_id,
            priority_level=payload.priority_level,
            estimated_cost=payload.estimated_cost,
            estimated_cost_inr=inr_cost,
            created_date=now,
            status="PENDING",
            assessment_id=payload.assessment_id,
            notes=payload.notes,
        )
        db.add(row)
        await db.flush()

        return _row_to_work_order(row)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create work order: {str(e)}")


@router.get("/work-orders", response_model=List[WorkOrder])
async def list_work_orders(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all work orders, most recent first."""
    result = await db.execute(
        select(WorkOrderRow).order_by(desc(WorkOrderRow.created_date)).limit(limit)
    )
    rows = result.scalars().all()
    return [_row_to_work_order(r) for r in rows]


@router.get("/health", response_model=dict)
async def repair_health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    result = await db.execute(select(WorkOrderRow))
    count = len(result.scalars().all())
    return {
        "status": "healthy",
        "service": "repair",
        "work_orders_in_db": count,
    }
