from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth.dependencies import get_current_user
from ..config.database import get_db
from ..models.plant import Plant
from ..models.watering_event import WateringEvent
from ..schemas import watering_events as WateringSchemas

router = APIRouter()


@router.post("/create", response_model=WateringSchemas.WateringEvent)
async def create(
    watering_event: WateringSchemas.WateringEventCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    plant = (
        db.query(Plant)
        .filter(Plant.id == watering_event.plant_id)
        .filter(Plant.user_id == user_id)
        .first()
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    event = WateringEvent(**watering_event.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/list/{plant_id}", response_model=list[WateringSchemas.WateringEvent])
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

    events = (
        db.query(WateringEvent)
        .filter(WateringEvent.plant_id == plant_id)
        .order_by(WateringEvent.created_at.desc())
        .all()
    )

    if not events:
        raise HTTPException(status_code=404, detail="No watering events found for this plant.")

    return events


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

    events = db.query(WateringEvent).filter(WateringEvent.plant_id == plant_id).all()
    if not events:
        raise HTTPException(status_code=404, detail="No watering events found for this plant.")

    for event in events:
        db.delete(event)
    db.commit()

    return {"message": "Watering events deleted", "count": len(events)}
