from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from dto.models.auth_dto import AccessData
from services.user_service import UserService
from utils.auth_utils import get_access_data

user_router = APIRouter(prefix="/user")


@user_router.get("/me")
async def get_profile(current_user: AccessData = Depends(get_access_data),
                      user_service: UserService = Depends(UserService.get_instance)) -> JSONResponse:
    user = await user_service.get_user_by_id(current_user.sub)
    return JSONResponse(content=jsonable_encoder(user, exclude_none=True))

