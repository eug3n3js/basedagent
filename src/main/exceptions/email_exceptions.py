from .base_exceptions import BaseAppException


class EmailError(BaseAppException):
    pass


class EmailSendError(EmailError):
    pass


class EmailConfigurationError(EmailError):
    pass
