from enums import MessageRole
from ..models import MessageEntity, MessageCreate


class MessageConverter:

    @staticmethod
    def from_pydantic_to_entity(message_create: MessageCreate) -> MessageEntity:
        return MessageEntity(
            content=message_create.content,
            role=MessageRole.USER,
            chat_id=message_create.chat_id
        )
    
    
