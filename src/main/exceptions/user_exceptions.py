from .base_exceptions import BaseAppException


class UserError(BaseAppException):
    pass


class UserNotFoundError(UserError):
    pass


class UserAlreadyExistsError(UserError):
    pass


class UserEmailAlreadyExistsError(UserError):
    pass

