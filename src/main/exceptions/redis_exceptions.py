from .base_exceptions import BaseAppException


class RedisError(BaseAppException):
    pass


class RedisConnectionError(RedisError):
    pass


class RedisOperationError(RedisError):
    pass
