from pydantic import BaseModel


class WalletAuthRequest(BaseModel):
    wallet_address: str
    signature: str


class SendEmailCodeRequest(BaseModel):
    email: str


class VerifyEmailCodeRequest(BaseModel):
    email: str
    code: str   


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    exp: int


class AccessData(BaseModel):
    sub: int
    wallet_address: str
    exp: int
