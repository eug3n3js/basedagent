from .base_exceptions import BaseAppException


class IndexerConnectionError(BaseAppException):
    pass


class IndexerQueryError(BaseAppException):
    pass
