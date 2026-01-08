# core/security.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from core.settings import settings

bearer_scheme = HTTPBearer()


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    data = {"sub": subject}
    if extra_claims:
        data.update(extra_claims)

    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRES_HOURS)
    data["exp"] = expire

    encoded = jwt.encode(
        data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = creds.credentials
    payload = decode_access_token(token)
    return payload

