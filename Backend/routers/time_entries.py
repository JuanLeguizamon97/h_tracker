from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.time_entries import (
    create_time_entry, get_time_entries, get_time_entry, update_time_entry, delete_time_entry,
)
from schemas.time_entries import TimeEntryCreate, TimeEntryUpdate, TimeEntryOut

time_entries_router = APIRouter(prefix="/time-entries", tags=["time-entries"])


@time_entries_router.post("/", response_model=TimeEntryOut, status_code=status.HTTP_201_CREATED)
def create_new_time_entry(entry_in: TimeEntryCreate, db: Session = Depends(get_db)):
    return create_time_entry(db, entry_in)


@time_entries_router.get("/", response_model=List[TimeEntryOut])
def list_time_entries(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    date_gte: Optional[date] = None,
    date_lte: Optional[date] = None,
    billable: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_time_entries(
        db,
        user_id=user_id,
        project_id=project_id,
        date_gte=date_gte,
        date_lte=date_lte,
        billable=billable,
        status=status,
    )


@time_entries_router.get("/{entry_id}", response_model=TimeEntryOut)
def get_time_entry_detail(entry_id: str, db: Session = Depends(get_db)):
    entry = get_time_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    return entry


@time_entries_router.put("/{entry_id}", response_model=TimeEntryOut)
def update_time_entry_detail(entry_id: str, entry_in: TimeEntryUpdate, db: Session = Depends(get_db)):
    entry = update_time_entry(db, entry_id, entry_in)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    return entry


@time_entries_router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry_detail(entry_id: str, db: Session = Depends(get_db)):
    if not delete_time_entry(db, entry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
