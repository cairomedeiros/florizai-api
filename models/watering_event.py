import uuid
from sqlalchemy import Column, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class WateringEvent(Base):
    __tablename__ = "watering_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.id"), index=True, nullable=False)
    watered_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)