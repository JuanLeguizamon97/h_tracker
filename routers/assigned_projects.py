# routers/projects.py (o como lo tengas)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import db_session
from middlewares.jwt_bearer import JWTBearer
from services.assigned_projects import (
    get_assigned_projects,
    create_assigned_project,
    get_assigned_projects_by_employee,
)
from schemas.assigned_projects import (
    AssignedProjectCreate,
    AssignedProjectOut,
    ProjectDesignOut,
)

aprojects_router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(JWTBearer())],  # protege todos los endpoints
)


# 🔹 GET: listado de asignaciones (versión simple: todos)
@aprojects_router.get(
    "/",
    response_model=list[ProjectDesignOut],
    status_code=status.HTTP_200_OK,
)
def list_projects(db: Session = Depends(db_session)):
    try:
        projects = get_assigned_projects(db)
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# 🔹 GET opcional: solo del empleado (si luego tienes un current_employee)
# from dependencies.auth import get_current_employee
#
# @projects_router.get(
#     "/me",
#     response_model=list[ProjectDesignOut],
#     status_code=status.HTTP_200_OK,
# )
# def list_my_projects(
#     db: Session = Depends(db_session),
#     current_employee = Depends(get_current_employee),
# ):
#     try:
#         projects = get_assigned_projects_by_employee(
#             db, current_employee.id_employee
#         )
#         return projects
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e),
#         )


# 🔹 POST: crear una nueva asignación empleado–proyecto–cliente
@aprojects_router.post(
    "/",
    response_model=AssignedProjectOut,
    status_code=status.HTTP_201_CREATED,
)
def assign_project(
    payload: AssignedProjectCreate,
    db: Session = Depends(db_session),
):
    try:
        new_assignment = create_assigned_project(db, payload)
        return new_assignment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
