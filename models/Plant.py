import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text, Text
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)