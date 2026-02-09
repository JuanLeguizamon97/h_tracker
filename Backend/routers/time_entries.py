# routers/time_entries.py
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db

from services.time_entries import (
    create_time_entry,
    get_time_entries,
    get_time_entry as get_time_entry_service,
    update_time_entry as update_time_entry_service,
    delete_time_entry as delete_time_entry_service,
)
from schemas.time_entries import TimeEntryCreate, TimeEntryUpdate, TimeEntryOut


time_entries_router = APIRouter(
    prefix="/time-entries",
    tags=["time_entries"],
)


@time_entries_router.post(
    "/",
    response_model=TimeEntryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_time_entry(
    entry_in: TimeEntryCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_time_entry(db, entry_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@time_entries_router.get(
    "/",
    response_model=List[TimeEntryOut],
    status_code=status.HTTP_200_OK,
)
def list_time_entries(
    id_employee: Optional[str] = None,
    id_project: Optional[str] = None,
    id_client: Optional[str] = None,
    week_start: Optional[date] = None,
    week_start_gte: Optional[date] = None,
    week_start_lte: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return get_time_entries(
        db,
        id_employee=id_employee,
        id_project=id_project,
        id_client=id_client,
        week_start=week_start,
        week_start_gte=week_start_gte,
        week_start_lte=week_start_lte,
    )


@time_entries_router.get(
    "/{id_hours}",
    response_model=TimeEntryOut,
    status_code=status.HTTP_200_OK,
)
def get_time_entry_detail(
    id_hours: str,
    db: Session = Depends(get_db),
):
    entry = get_time_entry_service(db, id_hours)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )
    return entry


@time_entries_router.put(
    "/{id_hours}",
    response_model=TimeEntryOut,
    status_code=status.HTTP_200_OK,
)
def update_time_entry_detail(
    id_hours: str,
    entry_in: TimeEntryUpdate,
    db: Session = Depends(get_db),
):
    entry = update_time_entry_service(db, id_hours, entry_in)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )
    return entry


@time_entries_router.delete(
    "/{id_hours}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_time_entry_detail(
    id_hours: str,
    db: Session = Depends(get_db),
):
    deleted = delete_time_entry_service(db, id_hours)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )
    return
