from fastapi import APIRouter, Depends, HTTPException
from ..auth.dependencies import get_current_user
from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from ..config.database import get_db
from ..config.redis_client import get_redis_client
from ..services.cache_service import invalidate_cache
from ..models.plant import Plant
from ..schemas import plant as PlantsSchemas
import json

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

        invalidate_cache(user_id=current_user["user"].id)

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

        invalidate_cache(user_id=current_user["user"].id)

        return plant

@router.get("/plants/{plant_id}", response_model=PlantsSchemas.Plant)
async def get(plant_id: UUID, 
              current_user=Depends(get_current_user),
              db: Session = Depends(get_db)):

    user_id = current_user["user"].id

    plant = (
          db.query(Plant)
          .options(selectinload(Plant.pictures))
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
    #aqui tenho que implementar o redis para pegar as plantas do usuário, se não tiver no redis, ai sim eu busco no banco de dados e coloco no redis
    client = get_redis_client()
    user_id = current_user["user"].id
    cache_key = f"plants_user_{user_id}"
    plants_cache = client.get(cache_key)

    if plants_cache:
        plants_data = json.loads(plants_cache)
        return [PlantsSchemas.Plant.model_validate(plant) for plant in plants_data]

    
    plants = (
          db.query(Plant)
          .options(selectinload(Plant.pictures))
          .filter(Plant.user_id == user_id)
          .order_by(Plant.created_at.desc())
          .all()
    )
    print(plants)
    plants_list_dict = [PlantsSchemas.Plant.model_validate(plant).model_dump(mode="json") for plant in plants]
    # Armazena os resultados no Redis para futuras consultas
    client.set(cache_key, json.dumps(plants_list_dict), ex=3600)

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

    invalidate_cache(user_id=current_user["user"].id)

    return {"message": "Plant deleted"}