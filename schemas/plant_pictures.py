from uuid import UUID

from pydantic import BaseModel
from datetime import datetime

class PlantPicture(BaseModel):
    id: UUID
    plant_id: UUID
    image_path: str | None
    thumbnail_path: str | None
    created_at: datetime