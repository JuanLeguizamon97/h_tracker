from fastapi import FastAPI
from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from routers.employees import employees_router


app = FastAPI()
app.title = "Impact Point Hours Tracker"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(employees_router)


Base.metadata.create_all(bind=engine)