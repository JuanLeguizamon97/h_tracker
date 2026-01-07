
from fastapi import APIRouter, HTTPException
from fastapi import Request
from auth.microsoft_oauth import oauth
#from utils.security import create_access_token
from core.security import create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/microsoft/login")
async def microsoft_login(request: Request):
    """
    Redirige a Microsoft para que el usuario haga login.
    """
    redirect_uri = request.url_for("microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@auth_router.get("/microsoft/callback", name="microsoft_callback")
async def microsoft_callback(request: Request):
    """
    Callback de Microsoft: recibe el code, obtiene tokens,
    saca info del usuario y genera tu JWT propio.
    """
    try:
        token = await oauth.microsoft.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener token: {e}")

    user_info = token.get("userinfo")
    if not user_info:
        user_info = await oauth.microsoft.parse_id_token(request, token)

    # Aquí podrías crear/actualizar el usuario en tu BD usando el 'sub' o el 'email'.
    subject = user_info["sub"]  # id único de Microsoft
    extra_claims = {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
    }

    app_jwt = create_access_token(subject=subject, extra_claims=extra_claims)

    # Para ejemplo, lo devolvemos en JSON.
    # En un flujo real normalmente rediriges a tu frontend y le pasas el token.
    return {
        "access_token": app_jwt,
        "token_type": "bearer",
        "user": extra_claims,
    }
