from fastapi import FastAPI
from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from routers.assigned_projects import aprojects_router


app = FastAPI()
app.title = "Impact Point Hours Tracker"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(aprojects_router)


Base.metadata.create_all(bind=engine)