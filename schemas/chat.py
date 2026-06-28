from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ChatCreate(BaseModel):
    plant_id: str

class Chat(BaseModel):
    id: UUID
    plant_id: UUID | None
    user_id: UUID
    summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)