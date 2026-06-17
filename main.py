import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config.database import engine

logging.basicConfig(level=logging.INFO)
from .models.base import Base
from .routers import user, plant, chat, message, plant_pictures, watering_events
from .services.scheduler_service import scheduler_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler_service.start()
    print("Scheduler iniciado")
    yield
    scheduler_service.stop()
    print("Scheduler parado")

app = FastAPI(lifespan=lifespan)

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(plant.router, prefix="/plant", tags=["plant"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(message.router, prefix="/message", tags=["message"])
app.include_router(plant_pictures.router, prefix="/plant_pictures", tags=["plant_pictures"])
app.include_router(watering_events.router, prefix="/watering_events", tags=["watering_events"])

@app.get("/")
async def root():
			return {"message": "Hello World"}