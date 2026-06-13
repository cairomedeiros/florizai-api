from uuid import UUID
import datetime

from pydantic import BaseModel, ConfigDict

class PlantCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None

class PlantUpdate(PlantCreate):
    pass

class Plant(PlantCreate):
    id: UUID
    user_id: UUID
    created_at: datetime.datetime
    file_path: str | None = None