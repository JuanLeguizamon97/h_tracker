from typing import Iterable
from fastapi import Depends
from fastapi_azure_auth.exceptions import Unauthorized
from fastapi_azure_auth.user import User
from core.auth import azure_scheme

def require_roles(allowed: Iterable[str]):
    allowed_set = set(allowed)

    async def _dep(user: User = Depends(azure_scheme)) -> User:
        # user.roles viene del token; doc muestra validación tipo 'AdminUser' in user.roles
        if not allowed_set.intersection(set(user.roles or [])):
            raise Unauthorized(f"Missing required role. Need one of: {sorted(allowed_set)}")
        return user

    return _dep
