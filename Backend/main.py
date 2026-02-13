import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Security, Depends
from fastapi.middleware.cors import CORSMiddleware

from utils.auth_microsoft import azure_scheme
from config.database import engine, Base

from routers.assigned_projects import aprojects_router
from routers.clients import clients_router
from routers.employees import employees_router
from routers.projects import projects_router
from routers.time_entries import time_entries_router
from routers.weeks import weeks_router
from routers.invoice import invoice_router
from routers.invoice_lines import invoice_lines_router
from routers.auth import auth_router

# Import all models so Base.metadata sees them
from models.employees import Employees  # noqa
from models.clients import Client  # noqa
from models.projects import Project  # noqa
from models.time_entries import TimeEntry  # noqa
from models.assigned_projects import AssignedProject  # noqa
from models.invoice import Invoice  # noqa
from models.invoice_lines import InvoiceLine  # noqa
from models.weeks import Week  # noqa
from models.app_user import AppUser  # noqa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

AUTH_MODE = os.getenv("AUTH_MODE", "azure")

app = FastAPI(
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": os.getenv("AZURE_SWAGGER_CLIENT_ID", "b44bcf9e-cc38-4542-82b9-e9447a45a7ec"),
        "scopes": [
            os.getenv(
                "AZURE_API_SCOPE",
                "api://6cda0fcc-09b3-4173-b6cc-07df8bf2b82b/user_impersonation",
            )
        ],
    },
)
app.title = "Impact Point Hours Tracker"
app.version = "0.0.1"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Auth dependency selection ----------
def get_auth_dependency():
    if AUTH_MODE == "mock":
        env = os.getenv("ENV", "dev")
        if env == "prod":
            raise RuntimeError("AUTH_MODE=mock is forbidden when ENV=prod")
        logger.warning("*** AUTH_MODE=mock is active — NOT for production ***")
        return []
    return [Security(azure_scheme)]


auth_deps = get_auth_dependency()

# ---------- Routers ----------
# Auth router has its own auth handling
app.include_router(auth_router)

app.include_router(aprojects_router, dependencies=auth_deps)
app.include_router(clients_router, dependencies=auth_deps)
app.include_router(employees_router, dependencies=auth_deps)
app.include_router(projects_router, dependencies=auth_deps)
app.include_router(time_entries_router, dependencies=auth_deps)
app.include_router(weeks_router, dependencies=auth_deps)
app.include_router(invoice_router, dependencies=auth_deps)
app.include_router(invoice_lines_router, dependencies=auth_deps)


# ---------- Health check ----------
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# ---------- Create tables (fallback if no Alembic migration run) ----------
Base.metadata.create_all(bind=engine)
