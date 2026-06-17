from PIL import Image
import os
from pathlib import Path
from io import BytesIO
import logging
from sqlalchemy.orm import Session
from ..config.supabase import get_supabase
from ..config.database import SessionLocal
from ..models.plant_pictures import PlantPicture

logger = logging.getLogger(__name__)

def generate_thumbnail(image_path: str, thumbnail_size: tuple = (150, 150)) -> str:
    """
    Gera thumbnail de uma imagem
    
    Args:
        image_path: caminho da imagem original
        thumbnail_size: tamanho do thumbnail (largura, altura)
    
    Returns:
        caminho do thumbnail gerado
    """
    try:
        # Abrir imagem
        img = Image.open(image_path)
        
        # Criar pasta de thumbnails se não existir
        thumb_dir = Path(image_path).parent / "thumbnails"
        thumb_dir.mkdir(exist_ok=True)
        
        # Definir caminho do thumbnail
        thumb_path = thumb_dir / f"thumb_{Path(image_path).name}"
        
        # Redimensionar e salvar
        img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        img.save(thumb_path)
        
        return str(thumb_path)
    
    except Exception as e:
        print(f"Erro ao gerar thumbnail: {e}")
        return None


async def generate_and_upload_thumbnail(
    image_bytes: bytes, 
    image_path: str, 
    access_token: str,
    user_id: str,
    plant_picture_id: str,
    thumbnail_size: tuple = (150, 150)
) -> str | None:
    """
    Gera thumbnail em memória e faz upload pro Supabase Storage
    
    Args:
        image_bytes: conteúdo da imagem em bytes
        image_path: path original da imagem no Storage (ex: user_id/uuid.jpg)
        access_token: token de autenticação do Supabase
        user_id: ID do usuário
        thumbnail_size: tamanho do thumbnail (largura, altura)
    
    Returns:
        path do thumbnail no Storage, ou None se falhar
    """
    try:
        # Abrir imagem do bytes
        img = Image.open(BytesIO(image_bytes))
        
        # Redimensionar
        img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        
        # Salvar em memória
        thumb_buffer = BytesIO()
        img.save(thumb_buffer, format="JPEG", quality=80)
        thumb_buffer.seek(0)
        
        # Gerar path do thumbnail
        original_filename = image_path.split("/")[-1]
        thumbnail_path = f"{user_id}/thumbnails/thumb_{original_filename}"
        
        # Upload pro Supabase Storage
        supabase = get_supabase()
        supabase.postgrest.auth(access_token)
        supabase.storage.from_("leafchat").upload(
            thumbnail_path,
            thumb_buffer.read(),
            {"content-type": "image/jpeg"}
        )

        db: Session = SessionLocal()
        try:
            plant_picture = db.query(PlantPicture).filter(
                PlantPicture.id == plant_picture_id
            ).first()
            
            if plant_picture:
                plant_picture.thumbnail_path = thumbnail_path
                db.commit()
                logger.info(f"Thumbnail salvo no banco: {thumbnail_path}")
            else:
                logger.error(f"PlantPicture {plant_picture_id} não encontrado")
                
        except Exception as db_error:
            db.rollback()
            logger.error(f"Erro ao salvar thumbnail no banco: {db_error}")
        finally:
            db.close()
        
        return thumbnail_path
    
    except Exception as e:
        logger.error(f"Erro ao gerar thumbnail: {e}")
        return None