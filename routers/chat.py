from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth.dependencies import get_current_user
from ..config.database import get_db
from ..models.chat import Chat
from ..schemas import chat as ChatSchemas

router = APIRouter()


@router.post("/create", response_model=ChatSchemas.Chat)
async def create(
    new_chat: ChatSchemas.ChatCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = Chat(
        plant_id=new_chat.plant_id,
        user_id=current_user["user"].id,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@router.get("/get/{chat_id}", response_model=ChatSchemas.Chat)
async def get(
    chat_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id)
        .filter(Chat.user_id == user_id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    return chat


@router.delete("/delete/{chat_id}", response_model=dict)
async def delete(
    chat_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user"].id
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id)
        .filter(Chat.user_id == user_id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted"}
