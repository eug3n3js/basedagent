from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dto import (
    WalletAuthRequest, SendEmailCodeRequest,
    VerifyEmailCodeRequest, TokenResponse,
    AccessData)
from services import AuthService
from utils.auth_utils import get_access_data

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/authenticate")
async def authenticate(auth_request: WalletAuthRequest,
                       auth_service: AuthService = Depends(AuthService.get_instance)) -> TokenResponse:
    token_info = await auth_service.authenticate(auth_request)
    return token_info


@auth_router.post("/send-email-code")
async def send_email_code(email_request: SendEmailCodeRequest,
                          auth_service: AuthService = Depends(AuthService.get_instance)) -> JSONResponse:
    await auth_service.send_email_verification_code(email_request)
    return JSONResponse(content={"message": "Verification code sent to email"})


@auth_router.post("/verify-email-code")
async def verify_email_code(verification_request: VerifyEmailCodeRequest,
                            current_user: AccessData = Depends(get_access_data),
                            auth_service: AuthService = Depends(AuthService.get_instance)) -> JSONResponse:
    await auth_service.verify_email_code(current_user.sub, verification_request)
    return JSONResponse(content={"message": "Email verified and added successfully"})


@auth_router.get("/message")
async def get_auth_message(auth_service: AuthService = Depends(AuthService.get_instance)) -> JSONResponse:
    message = await auth_service.generate_auth_message()
    return JSONResponse(content={"message": message})


