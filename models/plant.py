import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), index=True)
    description = Column(Text, nullable=True)
    # LLM-suggested watering cadence (days). Null until inferred; front falls back to 7.
    watering_interval_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)
    # cascade so deleting a plant removes its owned rows (no DB-level ON DELETE CASCADE needed)
    pictures = relationship("PlantPicture", back_populates="plant", order_by="PlantPicture.created_at",
                            cascade="all, delete-orphan")
    watering_events = relationship("WateringEvent", cascade="all, delete-orphan")
    chats = relationship("Chat", cascade="all, delete-orphan")