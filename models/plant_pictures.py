import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class PlantPicture(Base):
    __tablename__ = "plant_pictures"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.id"), index=True)
    image_path = Column(String(255), nullable=True)
    thumbnail_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=text('now()'))
    plant = relationship("Plant", back_populates="pictures")