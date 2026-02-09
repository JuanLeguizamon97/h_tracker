# routers/projects.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db

from services.projects import (
    create_project,
    get_projects,
    get_project as get_project_service,
    update_project as update_project_service,
    delete_project as delete_project_service,
)
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut


projects_router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@projects_router.post(
    "/",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_project(db, project_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@projects_router.get(
    "/",
    response_model=List[ProjectOut],
    status_code=status.HTTP_200_OK,
)
def list_projects(
    active: Optional[bool] = None,
    id_client: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_projects(db, active=active, id_client=id_client)


@projects_router.get(
    "/{id_project}",
    response_model=ProjectOut,
    status_code=status.HTTP_200_OK,
)
def get_project_detail(
    id_project: str,
    db: Session = Depends(get_db),
):
    project = get_project_service(db, id_project)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@projects_router.put(
    "/{id_project}",
    response_model=ProjectOut,
    status_code=status.HTTP_200_OK,
)
def update_project_detail(
    id_project: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = update_project_service(db, id_project, project_in)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@projects_router.delete(
    "/{id_project}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_detail(
    id_project: str,
    db: Session = Depends(get_db),
):
    deleted = delete_project_service(db, id_project)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return
