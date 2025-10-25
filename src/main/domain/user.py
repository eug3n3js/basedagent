from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from chat import Chat


class User(Base):
    __tablename__ = "users"
    
    wallet_address: Mapped[str] = mapped_column(String(42), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    remaining_chat_credits: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user")
