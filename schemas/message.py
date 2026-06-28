from datetime import datetime
from uuid import UUID
from fastapi import Form
from pydantic import BaseModel, ConfigDict

class MessageCreate(BaseModel):
    chat_id: UUID  # form sends a str (coerced); DB column is UUID — keep them aligned
    content: str | None

class Message(MessageCreate):
    id: UUID
    role: str
    image_path: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

async def chat_form(
    chat_id: str = Form(...),
    content: str | None = Form(default=None),
) -> MessageCreate:
    return MessageCreate(
        chat_id=chat_id,
        content=content,
    )