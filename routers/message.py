import os
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool
from ..auth.dependencies import get_current_user
from ..config.database import get_db
from ..config.supabase import get_supabase
from ..schemas import message as MessageSchemas
from ..models.chat import Chat
from ..models.message import Message
from ..enums.chat_role import ChatRole
from .ai import rag_answer, vision_answer

router = APIRouter()


@router.post("/create", response_model=MessageSchemas.Message)
async def create(
    image: UploadFile | None = File(default=None),
    new_message: MessageSchemas.MessageCreate = Depends(MessageSchemas.chat_form),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not new_message.content and not image:
        raise HTTPException(status_code=400, detail="A message must have either content or an image.")

    user_id = current_user["user"].id
    chat = (
        db.query(Chat)
        .filter(Chat.id == new_message.chat_id)
        .filter(Chat.user_id == user_id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    image_path = None
    if image:
        contents = await image.read()

        image_ext = os.path.splitext(image.filename)[1]
        image_name = f"{uuid.uuid4()}{image_ext}"
        image_path = f"{user_id}/{image_name}"

        supabase = get_supabase()
        supabase.postgrest.auth(current_user["access_token"])
        supabase.storage.from_("leafchat").upload(image_path, contents)

    message = Message(
        chat_id=new_message.chat_id,
        role=ChatRole.USER,
        content=new_message.content,
        image_path=image_path,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # ponytail: single-turn. Pass chat history when multi-turn matters.
    # run_in_threadpool keeps the blocking Groq call off the event loop.
    if image:
        answer = await run_in_threadpool(vision_answer, contents, image.content_type, new_message.content)
    else:
        result = await run_in_threadpool(rag_answer, new_message.content)
        answer = result["answer"]

    reply = Message(
        chat_id=new_message.chat_id,
        role=ChatRole.ASSISTANT,
        content=answer,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@router.get("/list/{chat_id}", response_model=list[MessageSchemas.Message])
async def list(
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

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .all()
    )

    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this chat.")

    return messages


@router.delete("/delete/{chat_id}/{message_id}", response_model=dict)
async def delete(
    chat_id: UUID,
    message_id: UUID,
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

    message = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .filter(Message.id == message_id)
        .first()
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    db.delete(message)
    db.commit()
    return {"message": "Message deleted"}
