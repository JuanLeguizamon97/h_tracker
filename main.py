from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from core.settings import settings  # tu Settings actual

# 👇 NUEVO: esquema Azure (fastapi-azure-auth)
from auth.azure import azure_scheme

from routers.assigned_projects import aprojects_router
from routers.clients import clients_router
from routers.employees import employees_router
from routers.projects import projects_router
from routers.time_entries import time_entries_router
from routers.weeks import weeks_router
from routers.invoice import invoice_router
from routers.invoice_lines import invoice_lines_router
from routers.auth import auth_router  # (puedes eliminarlo después si ya no lo usas)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Carga la configuración OpenID (issuer, jwks, endpoints) de Entra ID al arrancar.
    Si falla, es mejor fallar temprano para detectar mala config de tenant/client/scopes.
    """
    await azure_scheme.openid_config.load_config()
    yield


# ---------- Swagger + OAuth (Azure Entra ID) ----------
extra_kwargs: dict = {}

# Solo configuramos OAuth en Swagger si hay OPENAPI_CLIENT_ID
if getattr(settings, "OPENAPI_CLIENT_ID", None):
    extra_kwargs["swagger_ui_oauth2_redirect_url"] = "/oauth2-redirect"
    extra_kwargs["swagger_ui_init_oauth"] = {
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.OPENAPI_CLIENT_ID,
        # 👇 IMPORTANTE: indica el scope del API para que Swagger lo solicite
        # Debe ser algo como: "api://<APP_CLIENT_ID>/user_impersonation"
        "scopes": getattr(settings, "AZURE_API_SCOPE", ""),
    }

# ---------- Crear la app ----------
app = FastAPI(
    title="Impact Point Hours Tracker",
    version="0.0.1",
    lifespan=lifespan,
    **extra_kwargs,
)

# Middleware de errores
app.add_middleware(ErrorHandler)

# CORS leyendo de settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(aprojects_router)
app.include_router(clients_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(time_entries_router)
app.include_router(weeks_router)
app.include_router(invoice_router)
app.include_router(invoice_lines_router)
app.include_router(auth_router)

# ---------- Crear tablas ----------
Base.metadata.create_all(bind=engine)
