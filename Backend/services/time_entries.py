from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from models.time_entries import TimeEntry
from schemas.time_entries import TimeEntryCreate, TimeEntryUpdate


def create_time_entry(db: Session, entry_in: TimeEntryCreate) -> TimeEntry:
    data = entry_in.model_dump(exclude_unset=True)
    db_entry = TimeEntry(**data)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_time_entries(
    db: Session,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    date_gte: Optional[date] = None,
    date_lte: Optional[date] = None,
    billable: Optional[bool] = None,
    status: Optional[str] = None,
) -> List[TimeEntry]:
    query = db.query(TimeEntry)
    if user_id is not None:
        query = query.filter(TimeEntry.user_id == user_id)
    if project_id is not None:
        query = query.filter(TimeEntry.project_id == project_id)
    if date_gte is not None:
        query = query.filter(TimeEntry.date >= date_gte)
    if date_lte is not None:
        query = query.filter(TimeEntry.date <= date_lte)
    if billable is not None:
        query = query.filter(TimeEntry.billable == billable)
    if status is not None:
        query = query.filter(TimeEntry.status == status)
    return query.order_by(TimeEntry.date.desc()).all()


def get_time_entry(db: Session, entry_id: str) -> Optional[TimeEntry]:
    return db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()


def update_time_entry(db: Session, entry_id: str, entry_in: TimeEntryUpdate) -> Optional[TimeEntry]:
    db_entry = get_time_entry(db, entry_id)
    if not db_entry:
        return None
    data = entry_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_time_entry(db: Session, entry_id: str) -> bool:
    db_entry = get_time_entry(db, entry_id)
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True
