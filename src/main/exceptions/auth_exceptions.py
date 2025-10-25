from .base_exceptions import BaseAppException


class AuthError(BaseAppException):
    pass


class InvalidCredentialsError(AuthError):
    pass


class TokenExpiredError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


class WalletSignatureError(AuthError):
    pass


class InvalidVerificationCodeError(AuthError):
    pass
