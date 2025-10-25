from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatEntity:
    id: int = None
    user_id: int = None
    title: str = None
    created_at: datetime = None

