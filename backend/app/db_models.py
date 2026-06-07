"""SQLAlchemy ORM models for SnapMend database tables."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class AssessmentRow(Base):
    """Persisted pavement assessment record."""
    __tablename__ = "assessments"

    assessment_id = Column(String, primary_key=True, index=True)
    street_segment_id = Column(String, nullable=False, index=True)
    inspector_name = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Pavement condition fields
    severity_level = Column(String, nullable=False)
    damage_types = Column(JSON, nullable=False, default=list)  # stored as JSON array
    image_urls = Column(JSON, nullable=True, default=list)
    repair_priority = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=True)
    estimated_cost_inr = Column(Float, nullable=True)
    repair_method = Column(Text, nullable=True)
    detailed_assessment = Column(Text, nullable=True)

    # Location
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    # Raw Gemini output for audit
    raw_assessment = Column(Text, nullable=True)


class WorkOrderRow(Base):
    """Persisted work order record."""
    __tablename__ = "work_orders"

    work_order_id = Column(String, primary_key=True, index=True)
    street_segment_id = Column(String, nullable=False, index=True)
    priority_level = Column(String, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    estimated_cost_inr = Column(Float, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_crew = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    assessment_id = Column(String, nullable=True, index=True)
    notes = Column(Text, nullable=True)
