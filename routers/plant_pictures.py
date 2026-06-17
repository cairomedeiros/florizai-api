import os
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from ..auth.dependencies import get_current_user
from ..config.database import get_db
from ..config.supabase import get_supabase
from ..models.plant import Plant
from ..models.plant_pictures import PlantPicture
from ..schemas import plant_pictures as PlantPictureSchemas
from ..services.image_service import generate_and_upload_thumbnail

router = APIRouter()


@router.post("/create", response_model=PlantPictureSchemas.PlantPicture)
async def create(
    background_tasks: BackgroundTasks,
    image: UploadFile | None = File(default=None),
    plant_id: UUID | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not image or not plant_id:
        raise HTTPException(status_code=400, detail="Image and plant_id are required.")

    user_id = current_user["user"].id
    plant = (
        db.query(Plant)
        .filter(Plant.id == plant_id)
        .filter(Plant.user_id == user_id)
        .first()
    )
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    contents = await image.read()
    image_ext = os.path.splitext(image.filename)[1]
    image_name = f"{uuid.uuid4()}{image_ext}"
    image_path = f"{user_id}/{image_name}"

    supabase = get_supabase()
    supabase.postgrest.auth(current_user["access_token"])
    supabase.storage.from_("leafchat").upload(image_path, contents)

    plant_picture = PlantPicture(
        plant_id=plant_id,
        image_path=image_path,
        thumbnail_path=None,
    )
    db.add(plant_picture)
    db.commit()
    db.refresh(plant_picture)

    # Agendar geração de thumbnail em background
    background_tasks.add_task(
        generate_and_upload_thumbnail,
        contents,
        image_path,
        current_user["access_token"],
        str(user_id),
        str(plant_picture.id)
    )

    return plant_picture


@router.get("/list/{plant_id}", response_model=list[PlantPictureSchemas.PlantPicture])
async def list(
    plant_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    plant = (
        db.query(Plant)
        .filter(Plant.id == plant_id)
        .filter(Plant.user_id == user_id)
        .first()
    )
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    pictures = (
        db.query(PlantPicture)
        .filter(PlantPicture.plant_id == plant_id)
        .order_by(PlantPicture.created_at.desc())
        .all()
    )

    if not pictures:
        raise HTTPException(status_code=404, detail="No pictures found for this plant.")

    return pictures


@router.delete("/delete/{plant_id}", response_model=dict)
async def delete(
    plant_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    plant = (
        db.query(Plant)
        .filter(Plant.id == plant_id)
        .filter(Plant.user_id == user_id)
        .first()
    )
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    pictures = db.query(PlantPicture).filter(PlantPicture.plant_id == plant_id).all()
    if not pictures:
        raise HTTPException(status_code=404, detail="No pictures found for this plant.")

    for picture in pictures:
        db.delete(picture)
    db.commit()

    return {"message": "Plant pictures deleted", "count": len(pictures)}
