import os
import logging
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.auth_microsoft import azure_scheme
from config.database import engine, Base

# Import routers
from routers.auth import auth_router
from routers.clients import clients_router
from routers.employees import employees_router
from routers.projects import projects_router
from routers.project_roles import project_roles_router
from routers.user_roles import user_roles_router
from routers.employee_projects import employee_projects_router
from routers.time_entries import time_entries_router
from routers.invoice import invoice_router
from routers.invoice_lines import invoice_lines_router
from routers.invoice_manual_lines import invoice_manual_lines_router
from routers.invoice_fees import invoice_fees_router
from routers.invoice_fee_attachments import invoice_fee_attachments_router
from routers.invoice_time_entries import invoice_time_entries_router
from routers.invoice_expenses import invoice_expenses_router
from routers.expensify import expensify_router

# Import all models so Base.metadata sees them
import models  # noqa - imports all models via __init__.py

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
app.version = "0.0.2"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


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
app.include_router(auth_router)
app.include_router(clients_router, dependencies=auth_deps)
app.include_router(employees_router, dependencies=auth_deps)
app.include_router(projects_router, dependencies=auth_deps)
app.include_router(project_roles_router, dependencies=auth_deps)
app.include_router(user_roles_router, dependencies=auth_deps)
app.include_router(employee_projects_router, dependencies=auth_deps)
app.include_router(time_entries_router, dependencies=auth_deps)
app.include_router(invoice_router, dependencies=auth_deps)
app.include_router(invoice_lines_router, dependencies=auth_deps)
app.include_router(invoice_manual_lines_router, dependencies=auth_deps)
app.include_router(invoice_fees_router, dependencies=auth_deps)
app.include_router(invoice_fee_attachments_router, dependencies=auth_deps)
app.include_router(invoice_time_entries_router, dependencies=auth_deps)
app.include_router(invoice_expenses_router, dependencies=auth_deps)
app.include_router(expensify_router, dependencies=auth_deps)


# ---------- Health check ----------
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# ---------- Create tables (fallback if no Alembic migration run) ----------
Base.metadata.create_all(bind=engine)
