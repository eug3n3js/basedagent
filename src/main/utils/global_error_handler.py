from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from exceptions import *


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "http_error"}
        )
    
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "http_error"}
        )
    
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors(), "type": "validation_error"}
        )
    
    if isinstance(exc, (UserNotFoundError, ChatNotFoundError, MessageNotFoundError)):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "type": "not_found_error"}
        )
    
    if isinstance(exc, (UserAlreadyExistsError, UserEmailAlreadyExistsError)):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc), "type": "conflict_error"}
        )
    
    if isinstance(exc, (
            InvalidCredentialsError, InvalidTokenError, TokenExpiredError,
            WalletSignatureError, InvalidVerificationCodeError)):
        response = JSONResponse(
            status_code=401,
            content={"detail": str(exc), "type": "auth_error"}
        )
        # Явно добавляем CORS заголовки для 401 ошибок
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    if isinstance(exc, ChatAccessDeniedError):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc), "type": "forbidden_error"}
        )
    
    if isinstance(exc, InsufficientCreditsError):
        response = JSONResponse(
            status_code=402,
            content={"detail": str(exc), "type": "insufficient_credits_error"}
        )
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    
    if isinstance(exc, (ChatLimitExceededError, PendingUserError)):
        return JSONResponse(
            status_code=429,
            content={"detail": str(exc), "type": "rate_limit_error"}
        )
    
    if isinstance(exc, (
            RedisConnectionError, RedisOperationError,
            IndexerConnectionError, IndexerQueryError)):
        return JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable", "type": "service_error"}
        )
    
    if isinstance(exc, (EmailSendError, EmailConfigurationError)):
        return JSONResponse(
            status_code=500,
            content={"detail": "Email service error", "type": "email_error"}
        )
    
    if isinstance(exc, LLMClientError):
        return JSONResponse(
            status_code=500,
            content={"detail": "AI service error", "type": "llm_error"}
        )
    
    if isinstance(exc, WalletVerificationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "type": "wallet_error"}
        )
    
    if isinstance(exc, BaseAppException):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": "application_error"}
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )
