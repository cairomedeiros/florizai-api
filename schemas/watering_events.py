from uuid import UUID
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

WateringFrequency = Literal["daily", "weekly", "biweekly"]

class WateringEventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    plant_id: UUID
    watered_at: datetime

class WateringEvent(WateringEventCreate):
    id: UUID
    created_at: datetime

class WateringReminderCreate(BaseModel):
    frequency: WateringFrequency