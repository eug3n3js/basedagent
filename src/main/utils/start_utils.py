import os
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

from .db_helper import DatabaseHelper
from clients import RedisClient, EmailClient, IndexerClient
from services import AuthService, UserService, ChatService, NotificationService, IndexerService
from persistence import UserDAO, ChatDAO, MessageDAO

_db_helper: DatabaseHelper | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    await startup()
    yield
    await shutdown()


async def startup():
    global _db_helper
    _db_helper = DatabaseHelper()
    # await _db_helper.del_schema()
    await _db_helper.create_schema()

    user_dao = UserDAO(_db_helper)
    chat_dao = ChatDAO(_db_helper)
    message_dao = MessageDAO(_db_helper)

    redis_client = RedisClient()
    email_client = EmailClient()

    await redis_client.connect()

    NotificationService.initialize(redis_client)

    AuthService.initialize(user_dao, email_client, redis_client)
    UserService.initialize(user_dao)
    ChatService.initialize(chat_dao, message_dao, user_dao, redis_client)

    indexer_client = IndexerClient()
    IndexerService.initialize(indexer_client, NotificationService.get_instance())
    asyncio.create_task(IndexerService.get_instance().start_periodic_queries(10))


async def shutdown():
    global _db_helper
    if _db_helper is not None:
        await _db_helper.close()
        _db_helper = None


async def run_app(app_name: str = "app"):
    load_dotenv()
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    workers = int(os.getenv("APP_WORKERS", 1))
    
    config = uvicorn.Config(
        app=f"main:{app_name}",
        host=host,
        port=port,
        workers=workers,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()
