import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class PlantPicture(Base):
    __tablename__ = "plant_pictures"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.id"), index=True)
    image_path = Column(String(400), nullable=True)
    created_at = Column(DateTime, server_default=text('now()'))