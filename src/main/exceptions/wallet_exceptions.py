from .base_exceptions import BaseAppException


class WalletError(BaseAppException):
    pass


class WalletVerificationError(WalletError):
    pass


class InvalidAddressError(WalletError):
    pass