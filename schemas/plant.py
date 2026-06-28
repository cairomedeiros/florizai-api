from uuid import UUID
import datetime

from pydantic import BaseModel, ConfigDict

class PlantCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None

class PlantUpdate(PlantCreate):
    pass

class PlantPictureNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    image_path: str | None
    thumbnail_path: str | None
    created_at: datetime.datetime

class Plant(PlantCreate):
    id: UUID
    user_id: UUID
    created_at: datetime.datetime
    watering_interval_days: int | None = None
    file_path: str | None = None
    pictures: list[PlantPictureNested] = []