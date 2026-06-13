import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Enum as SQLAlchemyEnum,
    Text,
    DateTime,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from ..enums.chat_role import ChatRole

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), index=True)
    role = Column(
        SQLAlchemyEnum(ChatRole, name="chat_role_enum"),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=True)
    image_path = Column(String(400), nullable=True)
    created_at = Column(DateTime, server_default=text('now()'))