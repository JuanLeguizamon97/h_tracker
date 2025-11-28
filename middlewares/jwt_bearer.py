from utils.jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from fastapi import HTTPException, Request
from typing import Optional

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, allowed_roles: Optional[list] = None):
        super().__init__(auto_error=auto_error)
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request):
        # Obtener el token de autorización
        auth = await super().__call__(request)
        
        # Validar el token
        try:
            payload = validate_token(auth.credentials)
        except Exception as e:
            raise HTTPException(status_code=403, detail="Invalid token or expired token")

        # Verificar si hay roles permitidos y si el usuario tiene uno de esos roles
        if self.allowed_roles and payload.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have access to this resource")

        # Verificar si el email está presente en el payload y es válido
        if 'email' not in payload:
            raise HTTPException(status_code=403, detail="Invalid token structure")

        return payload  # Devuelve el payload validado para usar en otras rutas