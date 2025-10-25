from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel


@dataclass
class UserEntity:
    id: int = None
    wallet_address: str = None
    email: str = None
    remaining_chat_credits: float = 0
    created_at: datetime = None

