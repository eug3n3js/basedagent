from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from domain import Chat
from dto import ChatEntity
from exceptions import ChatNotFoundError
from utils.db_helper import DatabaseHelper


class ChatDAO:
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper

    async def get_by_id(self, chat_id: int) -> ChatEntity | None:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.messages))
            )
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def get_user_chats(self, user_id: int, limit: int = 50, offset: int = 0) -> list[ChatEntity]:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(Chat)
                .where(Chat.user_id == user_id)
                .order_by(Chat.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return [self._to_entity(chat) for chat in result.scalars().all()]

    async def count_user_chats(self, user_id: int) -> int:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(func.count(Chat.id)).where(Chat.user_id == user_id)
            )
            return result.scalar()

    async def create(self, chat: ChatEntity) -> ChatEntity:
        chat = Chat(
            title=chat.title,
            user_id=chat.user_id
        )
        
        async for session in self.db_helper.session_dependency():
            session.add(chat)
            await session.commit()
            await session.refresh(chat)
            return self._to_entity(chat)

    async def update(self, chat: ChatEntity) -> None:
        async for session in self.db_helper.session_dependency():
            existing_chat = await session.get(Chat, chat.id)
            if not existing_chat:
                raise ChatNotFoundError(f"Chat {chat.id} not found")
            if chat.title:
                existing_chat.title = chat.title
            await session.commit()

    async def delete(self, chat_id: int) -> None:
        async for session in self.db_helper.session_dependency():
            await session.execute(
                delete(Chat)
                .where(Chat.id == chat_id)
            )
            
            await session.commit()

    @staticmethod
    def _to_entity(chat: Chat) -> ChatEntity:
        return ChatEntity(
            id=chat.id,
            title=chat.title,
            user_id=chat.user_id,
            created_at=chat.created_at
        )
