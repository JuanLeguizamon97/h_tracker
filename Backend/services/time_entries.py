# services/time_entries.py
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from models.time_entries import TimeEntry
from models.weeks import Week
from schemas.time_entries import TimeEntryCreate, TimeEntryUpdate


def _ensure_week_exists(db: Session, week_start_date: date) -> None:
    existing = db.query(Week).filter(Week.week_start == week_start_date).first()
    if existing:
        return

    week_end_date = week_start_date + timedelta(days=6)
    week_number = week_start_date.isocalendar()[1]
    year_number = week_start_date.isocalendar()[0]

    new_week = Week(
        week_start=week_start_date,
        week_end=week_end_date,
        week_number=week_number,
        year_number=year_number,
    )
    db.add(new_week)
    db.flush()


def create_time_entry(db: Session, entry_in: TimeEntryCreate) -> TimeEntry:
    _ensure_week_exists(db, entry_in.week_start)
    db_entry = TimeEntry(**entry_in.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_time_entries(
    db: Session,
    id_employee: Optional[str] = None,
    id_project: Optional[str] = None,
    id_client: Optional[str] = None,
    week_start: Optional[date] = None,
    week_start_gte: Optional[date] = None,
    week_start_lte: Optional[date] = None,
) -> List[TimeEntry]:
    query = db.query(TimeEntry)

    if id_employee is not None:
        query = query.filter(TimeEntry.id_employee == id_employee)

    if id_project is not None:
        query = query.filter(TimeEntry.id_project == id_project)

    if id_client is not None:
        query = query.filter(TimeEntry.id_client == id_client)

    if week_start is not None:
        query = query.filter(TimeEntry.week_start == week_start)

    if week_start_gte is not None:
        query = query.filter(TimeEntry.week_start >= week_start_gte)

    if week_start_lte is not None:
        query = query.filter(TimeEntry.week_start <= week_start_lte)

    return query.all()


def get_time_entry(db: Session, id_hours: str) -> Optional[TimeEntry]:
    return (
        db.query(TimeEntry)
        .filter(TimeEntry.id_hours == id_hours)
        .first()
    )


def update_time_entry(
    db: Session,
    id_hours: str,
    entry_in: TimeEntryUpdate,
) -> Optional[TimeEntry]:
    db_entry = get_time_entry(db, id_hours)
    if not db_entry:
        return None

    data = entry_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_entry, field, value)

    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_time_entry(db: Session, id_hours: str) -> bool:
    db_entry = get_time_entry(db, id_hours)
    if not db_entry:
        return False

    db.delete(db_entry)
    db.commit()
    return True
