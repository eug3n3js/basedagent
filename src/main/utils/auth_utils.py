from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from dto.models.auth_dto import AccessData
from utils.jwt_utils import decode_jwt
from exceptions.auth_exceptions import InvalidTokenError

oauth2 = OAuth2PasswordBearer(tokenUrl="/login")


async def get_access_data(token: str = Depends(oauth2)) -> AccessData:
    payload = decode_jwt(token)

    if payload.get("type") != "ACCESS":
        raise InvalidTokenError("Invalid token type")

    return AccessData(
        sub=payload["sub"],
        wallet_address=payload["wallet_address"],
        exp=payload["exp"]
    )
