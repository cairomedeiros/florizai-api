from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth.dependencies import get_current_user
from ..config.database import get_db
from ..models.plant import Plant
from ..models.watering_event import WateringEvent
from ..schemas import watering_events as WateringSchemas
from ..services.scheduler_service import scheduler_service

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


@router.delete("/event/{event_id}", response_model=dict)
async def delete_event(
    event_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    event = (
        db.query(WateringEvent)
        .join(Plant, Plant.id == WateringEvent.plant_id)
        .filter(WateringEvent.id == event_id)
        .filter(Plant.user_id == user_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Watering event not found.")

    db.delete(event)
    db.commit()
    return {"message": "Watering event deleted", "id": str(event_id)}


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


# ===== REMINDERS (SCHEDULER) =====

@router.post("/reminders/{plant_id}")
async def create_watering_reminder(
    plant_id: str,
    reminder: WateringSchemas.WateringReminderCreate,
    current_user=Depends(get_current_user),
):
    """
    Cria lembrete automático de rega
    
    Body esperado:
    {
        "frequency": "daily"  # ou "weekly", "biweekly"
    }
    """
    user_id = str(current_user["user"].id)
    
    scheduler_service.add_watering_reminder(
        plant_id=plant_id,
        user_id=user_id,
        frequency=reminder.frequency
    )
    
    return {
        "message": "Lembrete de rega criado",
        "plant_id": plant_id,
        "frequency": reminder.frequency
    }


@router.delete("/reminders/{plant_id}")
async def delete_watering_reminder(
    plant_id: str,
    current_user=Depends(get_current_user),
):
    """Remove lembrete de rega"""
    user_id = str(current_user["user"].id)
    
    scheduler_service.remove_watering_reminder(plant_id, user_id)
    
    return {"message": "Lembrete removido"}


@router.get("/reminders")
async def list_watering_reminders(
    current_user=Depends(get_current_user),
):
    """Lista todos os lembretes do usuário"""
    jobs = scheduler_service.scheduler.get_jobs()
    
    user_id = str(current_user["user"].id)
    user_jobs = [
        {
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        }
        for job in jobs
        if user_id in job.id
    ]
    
    return user_jobs
