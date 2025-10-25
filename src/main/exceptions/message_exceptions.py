from .base_exceptions import BaseAppException


class MessageError(BaseAppException):
    pass


class MessageNotFoundError(MessageError):
    pass

