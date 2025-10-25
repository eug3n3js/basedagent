from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain import Message
from dto import MessageEntity
from utils.db_helper import DatabaseHelper


class MessageDAO:
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper

    async def get_by_id(self, message_id: int) -> MessageEntity | None:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(Message)
                .where(Message.id == message_id)
                .options(selectinload(Message.chat))
            )
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def get_chat_messages(self, chat_id: int, limit: int = None, offset: int = 0) -> list[MessageEntity]:
        async for session in self.db_helper.session_dependency():
            query = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            query = query.offset(offset)
            
            result = await session.execute(query)
            return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, message: MessageEntity) -> MessageEntity:
        message = Message(
            content=message.content,
            role=message.role,
            chat_id=message.chat_id
        )
        
        async for session in self.db_helper.session_dependency():
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return self._to_entity(message)

    @staticmethod
    def _to_entity(message: Message) -> MessageEntity:
        return MessageEntity(
            id=message.id,
            content=message.content,
            role=message.role,
            chat_id=message.chat_id,
            created_at=message.created_at
        )
