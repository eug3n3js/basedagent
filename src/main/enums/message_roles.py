from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    AI = "assistant"
