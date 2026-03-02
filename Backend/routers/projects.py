from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.projects import create_project, get_projects, get_project, update_project, delete_project
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut

projects_router = APIRouter(prefix="/projects", tags=["projects"])


@projects_router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_new_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, project_in)


@projects_router.get("/", response_model=List[ProjectOut])
def list_projects(
    active: Optional[bool] = None,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_projects(db, active=active, client_id=client_id)


@projects_router.get("/{project_id}", response_model=ProjectOut)
def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@projects_router.put("/{project_id}", response_model=ProjectOut)
def update_project_detail(project_id: str, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    project = update_project(db, project_id, project_in)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_detail(project_id: str, db: Session = Depends(get_db)):
    if not delete_project(db, project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
