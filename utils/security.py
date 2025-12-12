
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from config.settings import settings

bearer_scheme = HTTPBearer()

def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    """
    subject: normalmente user_id o el 'sub' de Microsoft.
    extra_claims: email, name, roles, etc.
    """
    to_encode = {"sub": subject}
    if extra_claims:
        to_encode.update(extra_claims)

    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRES_HOURS)
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


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
    """
    Dependency para proteger endpoints.
    Devuelve los claims del JWT (sub, email, name, etc.).
    """
    token = creds.credentials
    payload = decode_access_token(token)
    # aquí podrías mapear a un User de BD si quieres
    return payload

