from .base_exceptions import BaseAppException


class ChatError(BaseAppException):
    pass


class ChatNotFoundError(ChatError):
    pass


class ChatAccessDeniedError(ChatError):
    pass


class ChatLimitExceededError(ChatError):
    pass


class InsufficientCreditsError(ChatError):
    pass


class PendingUserError(ChatError):
    pass