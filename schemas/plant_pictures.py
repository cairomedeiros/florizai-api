from uuid import UUID

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PlantPicture(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    plant_id: UUID
    image_path: str | None
    thumbnail_path: str | None
    created_at: datetime