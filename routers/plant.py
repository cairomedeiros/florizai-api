from fastapi import APIRouter, Depends, HTTPException
from ..auth.dependencies import get_current_user
from sqlalchemy.orm import Session
from uuid import UUID
from ..config.database import get_db
from ..models.plant import Plant
from ..schemas import plant as PlantsSchemas

router = APIRouter()

@router.post("/plants", response_model=PlantsSchemas.Plant)
async def create(new_plant: PlantsSchemas.PlantCreate, 
                 current_user = Depends(get_current_user),
                 db: Session = Depends(get_db)):
        plant = Plant(
            **new_plant.model_dump(),
            user_id=current_user["user"].id
        )
        db.add(plant)
        db.commit()
        db.refresh(plant)
        return plant

@router.patch("plants/{plant_id}", response_model=PlantsSchemas.Plant)
async def update(plant_id: UUID,
                 plant_data: PlantsSchemas.PlantUpdate,
                 current_user = Depends(get_current_user),
                 db: Session = Depends(get_db)):
        user_id = current_user["user"].id
        plant = (
            db.query(Plant)
            .filter(Plant.id == plant_id)
            .filter(Plant.user_id == user_id)
            .first()
        )
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found.")

        for key, value in plant_data.model_dump(exclude_unset=True).items():
            setattr(plant, key, value)

        db.commit()
        db.refresh(plant)
        return plant

@router.get("/plants/{plant_id}", response_model=PlantsSchemas.Plant)
async def get(plant_id: UUID, 
              current_user=Depends(get_current_user),
              db: Session = Depends(get_db)):

    user_id = current_user["user"].id

    plant = (
          db.query(Plant)
          .filter(Plant.id == plant_id)
          .filter(Plant.user_id == user_id)
          .first()
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    return plant

@router.get("/plants", response_model=list[PlantsSchemas.Plant])
async def list(current_user=Depends(get_current_user),
               db: Session = Depends(get_db)):
    user_id = current_user["user"].id
    plants = (
          db.query(Plant)
          .filter(Plant.user_id == user_id)
          .order_by(Plant.created_at.desc())
          .all()
    )

    return plants

@router.delete("/plants/{plant_id}")
async def delete(plant_id: UUID, 
                 current_user = Depends(get_current_user), 
                 db: Session = Depends(get_db)):
    user_id = current_user["user"].id
    plant = (
         db.query(Plant)
         .filter(Plant.id == plant_id)
         .filter(Plant.user_id == user_id)
         .first()
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return {"message": "Plant deleted"}