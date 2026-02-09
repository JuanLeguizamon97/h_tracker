from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Security
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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await azure_scheme.openid_config.load_config()
    yield


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "b44bcf9e-cc38-4542-82b9-e9447a45a7ec",
        "scopes": ["api://6cda0fcc-09b3-4173-b6cc-07df8bf2b82b/user_impersonation"],
    },
    title="Impact Point Hours Tracker",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(aprojects_router, dependencies=[Security(azure_scheme)])
app.include_router(clients_router, dependencies=[Security(azure_scheme)])
app.include_router(employees_router, dependencies=[Security(azure_scheme)])
app.include_router(projects_router, dependencies=[Security(azure_scheme)])
app.include_router(time_entries_router, dependencies=[Security(azure_scheme)])
app.include_router(weeks_router, dependencies=[Security(azure_scheme)])
app.include_router(invoice_router, dependencies=[Security(azure_scheme)])
app.include_router(invoice_lines_router, dependencies=[Security(azure_scheme)])

# ---------- Crear tablas ----------
Base.metadata.create_all(bind=engine)
