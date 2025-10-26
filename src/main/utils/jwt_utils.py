import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from exceptions import InvalidTokenError, TokenExpiredError


def encode_jwt(payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    try:
        private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH")
        algorithm = os.getenv("JWT_ALGORITHM", "RS256")
        
        if not private_key_path:
            raise InvalidTokenError("JWT private key path not configured")
        
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        
        if expires_delta:
            expire_dt = datetime.utcnow() + expires_delta
        else:
            expire_dt = datetime.utcnow() + timedelta(seconds=int(os.getenv("JWT_EXPIRE_ACCESS", 3600)))
        
        payload.update({"exp": int(expire_dt.timestamp())})
        payload["sub"] = str(payload["sub"])
        
        token = jwt.encode(payload, private_key, algorithm=algorithm)
        return token
        
    except Exception as e:
        raise InvalidTokenError(f"Failed to encode JWT: {str(e)}")


def decode_jwt(token: str) -> Dict[str, Any]:
    try:
        public_key_path = os.getenv("JWT_PUBLIC_KEY_PATH")
        algorithm = os.getenv("JWT_ALGORITHM", "RS256")
        
        if not public_key_path:
            raise InvalidTokenError("JWT public key path not configured")
        
        with open(public_key_path, 'r') as f:
            public_key = f.read()
        
        payload = jwt.decode(token, public_key, algorithms=[algorithm])
        payload["sub"] = int(payload["sub"])
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise InvalidTokenError(f"Failed to decode JWT: {str(e)}")


def create_access_token(user_id: int, wallet_address: str) -> str:
    payload = {
        "sub": user_id,
        "wallet_address": wallet_address,
        "type": "ACCESS"
    }
    
    expires_delta = timedelta(seconds=int(os.getenv("JWT_EXPIRE_ACCESS", 3600)))
    return encode_jwt(payload, expires_delta)
