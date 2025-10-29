import asyncio

from . import UserService
from constants import PROMPT_MAP
from dto import ChatEntity, MessageEntity
from enums import MessageRole
from persistence import ChatDAO, MessageDAO, UserDAO
from clients import RedisClient
from clients import MCPClient
from clients import LLMClient
from exceptions import (
    ChatNotFoundError, ChatAccessDeniedError,
    InsufficientCreditsError, PendingUserError,
    UserNotFoundError
)


class ChatService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChatService, cls).__new__(cls)
        return cls._instance

    def __init__(self, chat_dao: ChatDAO, message_dao: MessageDAO, user_dao: UserDAO, redis_client: RedisClient):
        if not hasattr(self, '_initialized'):
            self.chat_dao = chat_dao
            self.message_dao = message_dao
            self.user_dao = user_dao
            self.redis_client = redis_client
            self._initialized = True
            self.pending_chats = set()
            self.lock = asyncio.Lock()

    @classmethod
    def initialize(cls, chat_dao: ChatDAO, message_dao: MessageDAO, user_dao: UserDAO, redis_client: RedisClient):
        if cls._instance:
            raise RuntimeError("ChatService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(chat_dao=chat_dao, message_dao=message_dao, user_dao=user_dao, redis_client=redis_client)
        cls._instance = instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("ChatService not initialized. Call initialize() first.")
        return cls._instance

    async def create(self, user_id: int) -> ChatEntity:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User not found")
        if user.remaining_chat_credits <= 0:
            raise InsufficientCreditsError(f"User has no chat credits")
        return await self.chat_dao.create(ChatEntity(user_id=user_id, title="New Chat"))

    async def get_by_id(self, chat_id: int) -> ChatEntity:
        chat = await self.chat_dao.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(f"Chat {chat_id} not found or access denied")
        return chat

    async def get_user_chats(self, user_id: int, limit: int = 50, offset: int = 0) -> list[ChatEntity]:
        return await self.chat_dao.get_user_chats(user_id, limit, offset)

    async def update(self, chat: ChatEntity) -> None:
        await self.chat_dao.update(chat)

    async def delete(self, chat_id: int) -> None:
        await self.chat_dao.delete(chat_id)

    async def get_chat_messages(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[MessageEntity]:
        return await self.message_dao.get_chat_messages(chat_id, limit, offset)

    async def process_user_message(self,
                                   user_id: int,
                                   message_create: MessageEntity,
                                   task_name: str = None) -> [MessageEntity, float]:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User not found")
        if user.remaining_chat_credits <= 0:
            raise InsufficientCreditsError(f"User has no chat credits")
        await self.verify_chat_ownership(message_create.chat_id, user_id)
        async with self.lock:
            if message_create.chat_id in self.pending_chats:
                raise PendingUserError(f"Chat {message_create.chat_id} is already being processed")
            self.pending_chats.add(message_create.chat_id)
        try:
            user_message = await self.message_dao.create(message_create)
            
            cached_messages = await self.redis_client.get_chat_messages(message_create.chat_id)
            print(f"cached_messages: {cached_messages}")
            if not cached_messages:
                db_messages = await self.message_dao.get_chat_messages(message_create.chat_id, limit=20, offset=0)
                db_messages.reverse()
                if db_messages:
                    for db_message in db_messages:
                        await self.redis_client.add_chat_message(message_create.chat_id, db_message)
            
            mcp_client = MCPClient()
            await mcp_client.setup_default_providers()
            llm_client = LLMClient(mcp_client, message_create.chat_id, self.redis_client)
            
            chat = await self.chat_dao.get_by_id(message_create.chat_id)
            if chat.title == "New Chat":
                title = await llm_client.generate_chat_title(user_message.content)
                await self.chat_dao.update(ChatEntity(id=message_create.chat_id, title=title))
            prompt = PROMPT_MAP.get(task_name)
            
            try:
                response = await asyncio.wait_for(
                    llm_client.get_ai_response(message_create.content, prompt),
                    timeout=60
                )
            except asyncio.TimeoutError:
                response = "Failed to generate response"
            ai_message = await self.message_dao.create(MessageEntity(
                content=response,
                role=MessageRole.AI,
                chat_id=message_create.chat_id
            ))
            
            await self.redis_client.add_chat_message(message_create.chat_id, user_message)
            await self.redis_client.add_chat_message(message_create.chat_id, ai_message)
            await self.redis_client.extend_chat_messages_ttl(message_create.chat_id, 300)
            used_credit = mcp_client.get_total_cost()
            used_credit += 0.1
            new_balance = await UserService.get_instance().update_balance_by_id(user_id, -used_credit)

            return ai_message, new_balance
        finally:
            async with self.lock:
                if message_create.chat_id in self.pending_chats:
                    self.pending_chats.remove(message_create.chat_id)

    async def verify_chat_ownership(self, chat_id: int, user_id: int) -> None:
        chat = await self.chat_dao.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(f"Chat {chat_id} not found")
        if chat.user_id != user_id:
            raise ChatAccessDeniedError(f"Chat {chat_id} does not belong to user {user_id}")

    @staticmethod
    def get_task_types() -> list[str]:
        return list(PROMPT_MAP.keys())
    
    async def is_chat_pending(self, chat_id: int) -> bool:
        async with self.lock:
            return chat_id in self.pending_chats
