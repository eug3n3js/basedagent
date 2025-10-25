from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel

from enums import MessageRole


@dataclass
class MessageEntity:
    id: int = None
    content: str = None
    role: MessageRole = None
    chat_id: int = None
    created_at: datetime = None


@dataclass
class MessageResponse:
    message: MessageEntity
    remaining_credits: float


class MessageCreate(BaseModel):
    content: str
    chat_id: int
