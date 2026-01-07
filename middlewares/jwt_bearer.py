# middlewares/jwt_bearer.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        token = credentials.credentials

        # TODO: valida el token aquí (ej: con pyjwt)
        # if not verify_jwt(token):
        #     raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return token