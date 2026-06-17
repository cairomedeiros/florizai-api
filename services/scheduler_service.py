from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Inicia o scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler iniciado")
    
    def stop(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler parado")
    
    def add_watering_reminder(self, plant_id: str, user_id: str, frequency: str = "daily"):
        """
        Adiciona lembrete de rega
        
        Args:
            plant_id: ID da planta
            user_id: ID do usuário
            frequency: 'daily', 'weekly', 'biweekly', ou expressão cron customizada
        """
        
        # Mapear frequências para cron
        cron_map = {
            "daily": "0 8 * * *",      # 8h todo dia
            "weekly": "0 8 * * 1",      # 8h segunda-feira
            "biweekly": "0 8 1,15 * *"  # 8h dias 1 e 15
        }
        
        cron_expr = cron_map.get(frequency, frequency)

        job_id = f"watering_{plant_id}_{user_id}"

        try:
            self.scheduler.add_job(
                func=send_watering_notification,
                trigger=CronTrigger.from_crontab(cron_expr),
                id=job_id,
                args=[plant_id, user_id],
                replace_existing=True
            )
            logger.info(f"Lembrete de rega adicionado: {job_id}")
        except Exception as e:
            logger.error(f"Erro ao adicionar job: {e}")
    
    def remove_watering_reminder(self, plant_id: str, user_id: str):
        """Remove lembrete de rega"""
        job_id = f"watering_{plant_id}_{user_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Lembrete removido: {job_id}")
        except Exception as e:
            logger.error(f"Erro ao remover job: {e}")


# Função que será executada pelo scheduler (síncrono, compatível com BackgroundScheduler)
def send_watering_notification(plant_id: str, user_id: str):
    from ..config.database import SessionLocal
    from ..models.watering_event import WateringEvent

    logger.info(f"Scheduler: registrando rega automática para planta {plant_id}")

    db = SessionLocal()
    try:
        event = WateringEvent(
            plant_id=plant_id,
            watered_at=datetime.now(),
        )
        db.add(event)
        db.commit()
        logger.info(f"Rega automática salva no banco para planta {plant_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar rega automática: {e}")
    finally:
        db.close()


# Instância global
scheduler_service = SchedulerService()