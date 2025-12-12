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

app = FastAPI()
app.title = "Impact Point Hours Tracker"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(aprojects_router)
app.include_router(clients_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(time_entries_router)
app.include_router(weeks_router)
app.include_router(invoice_router)
app.include_router(invoice_lines_router)
auth_router.include_router(auth_router)


Base.metadata.create_all(bind=engine)