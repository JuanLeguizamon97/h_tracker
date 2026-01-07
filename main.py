from fastapi import FastAPI
from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from routers.assigned_projects import aprojects_router
from routers.clients import clients_router
from routers.employees import employees_router
from routers.projects import projects_router
from routers.time_entries import time_entries_router
from routers.weeks import weeks_router
from routers.invoice import invoice_router
from routers.invoice_lines import invoice_lines_router
from routers.auth import auth_router
from starlette.middleware.sessions import SessionMiddleware
from core.settings import settings
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.title = "Impact Point Hours Tracker"
app.version = "0.0.1"

# CORS debe ir primero
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="proyecto-tracker-secreto-2026",
    same_site="lax",
    https_only=False,
)

app.add_middleware(ErrorHandler)
app.include_router(aprojects_router)
app.include_router(clients_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(time_entries_router)
app.include_router(weeks_router)
app.include_router(invoice_router)
app.include_router(invoice_lines_router)
app.include_router(auth_router)


Base.metadata.create_all(bind=engine)