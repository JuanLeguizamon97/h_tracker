from fastapi import FastAPI, Depends, Path, Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from config.database import db_session
from middlewares.jwt_bearer import JWTBearer
from models.employees import Employees as EmployeesModel
from services.employees import create_employee, get_employee
from schemas.employees import EmployeeProfile

employees_router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(JWTBearer())]
)

@employees_router.post("/", response_model=None, status_code=201) #Añadir un schema para la respuesta de la creación del usuario restaurante
def create_new_employee(employee: EmployeeProfile, db: Session = Depends(db_session)): #Crear el esquema de creación del perfil de restuarante
    try:
        new_profile= create_employee(db, employee)
        return new_profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#Pendiente crear los endpoints para modificar, obtener y eliminar restaurantes