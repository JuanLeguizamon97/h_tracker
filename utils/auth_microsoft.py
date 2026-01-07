
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from auth_microsoft import oauth
from datetime import datetime, timedelta
from jose import jwt

app = FastAPI()

# Clave para tus propios JWT
JWT_SECRET = "CAMBIA_ESTA_CLAVE_MUY_SECRETA"
JWT_ALGORITHM = "HS256"


def create_app_jwt(user_info: dict) -> str:
    """Crea un JWT propio para tu app usando la info del usuario Microsoft."""
    expire = datetime.utcnow() + timedelta(hours=8)
    payload = {
        "sub": user_info["sub"],         # id único de Microsoft
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@app.get("/auth/microsoft/login")
async def login_with_microsoft(request: Request):
    """
    1. Redirige al usuario a Microsoft para iniciar sesión.
    """
    redirect_uri = request.url_for("auth_microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@app.get("/auth/microsoft/callback")
async def auth_microsoft_callback(request: Request):
    """
    2. Microsoft devuelve aquí el 'code'.
    3. Intercambiamos el 'code' por tokens y sacamos el perfil del usuario.
    4. Creamos un JWT propio y se lo devolvemos al front.
    """
    try:
        token = await oauth.microsoft.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener token: {e}")

    # En muchos casos el id_token ya trae los claims del usuario
    user_info = token.get("userinfo")
    if not user_info:
        # Algunas veces hay que hacer userinfo manual
        user_info = await oauth.microsoft.parse_id_token(request, token)

    # Aquí podrías:
    # - Crear/actualizar el usuario en tu BD
    # - Asociar roles, etc.
    app_jwt = create_app_jwt(user_info)

    # Normalmente aquí rediriges a tu front con el token en query o fragment
    # Ejemplo: https://tu-frontend.com/login-success#token=...
    # Para ejemplo simple, lo devolvemos en JSON
    return {
        "access_token": app_jwt,
        "token_type": "bearer",
        "user": {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
        },
    }
