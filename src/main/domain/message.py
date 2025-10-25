from datetime import datetime
from typing import TYPE_CHECKING


from sqlalchemy import DateTime,  ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from enums import MessageRole

if TYPE_CHECKING:
    from chat import Chat


class Message(Base):
    __tablename__ = "messages"
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
