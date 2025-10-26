import time
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from dto import AccessData
from dto import MessageCreate, MessageResponse
from dto import MessageConverter
from services import ChatService
from utils.auth_utils import get_access_data

chat_router = APIRouter(prefix="/chat")

@chat_router.get("/chats")
async def get_user_chats(limit: int = Query(50, ge=1, le=100),
                         offset: int = Query(0, ge=0),
                         current_user: AccessData = Depends(get_access_data),
                         chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    chats = await chat_service.get_user_chats(current_user.sub, limit, offset)
    return JSONResponse(content=jsonable_encoder(chats, exclude_none=True))

@chat_router.post("/new")
async def create_chat(current_user: AccessData = Depends(get_access_data),
                      chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    chat = await chat_service.create(current_user.sub)
    return JSONResponse(content=jsonable_encoder(chat, exclude_none=True))


@chat_router.get("/tasks")
async def get_task_types(current_user: AccessData = Depends(get_access_data),
                        chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    task_types = chat_service.get_task_types()
    return JSONResponse(content=jsonable_encoder(task_types, exclude_none=True))


@chat_router.get("/{chat_id}/status")
async def get_chat_status(chat_id: int,
                         current_user: AccessData = Depends(get_access_data),
                         chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:    
    is_pending = await chat_service.is_chat_pending(chat_id)
    
    return JSONResponse(content={"is_pending": is_pending})

@chat_router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: int,
                            limit: int = Query(50, ge=1, le=100),
                            offset: int = Query(0, ge=0),
                            current_user: AccessData = Depends(get_access_data),
                            chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    await chat_service.verify_chat_ownership(chat_id, current_user.sub)
    messages = await chat_service.get_chat_messages(chat_id, limit, offset)
    return JSONResponse(content=jsonable_encoder(messages, exclude_none=True))

@chat_router.post("/{chat_id}/message/new")
async def process_message(message_create: MessageCreate,
                          current_user: AccessData = Depends(get_access_data),
                          chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    message = MessageConverter.from_pydantic_to_entity(message_create)
    response, new_balance = await chat_service.process_user_message(current_user.sub, message)
    return JSONResponse(
        content=jsonable_encoder(
            MessageResponse(message=response, remaining_credits=new_balance),
            exclude_none=True
        )
    )

@chat_router.post("/{chat_id}/message/new/{task_name}")
async def process_message_task(message_create: MessageCreate,
                               task_name: str,
                               current_user: AccessData = Depends(get_access_data),
                               chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    message = MessageConverter.from_pydantic_to_entity(message_create)
    response, new_balance = await chat_service.process_user_message(current_user.sub, message, task_name)
    return JSONResponse(
        content=jsonable_encoder(
            MessageResponse(message=response, remaining_credits=new_balance),
            exclude_none=True
        )
    )

@chat_router.get("/{chat_id}")
async def get_chat(chat_id: int,
                   current_user: AccessData = Depends(get_access_data),
                   chat_service: ChatService = Depends(ChatService.get_instance)) -> JSONResponse:
    await chat_service.verify_chat_ownership(chat_id, current_user.sub)
    chat = await chat_service.get_by_id(chat_id)
    return JSONResponse(content=jsonable_encoder(chat, exclude_none=True))