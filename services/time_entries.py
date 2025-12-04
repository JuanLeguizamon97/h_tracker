# services/time_entries.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from models.time_entries import TimeEntry
from schemas.time_entries import TimeEntryCreate, TimeEntryUpdate


def create_time_entry(db: Session, entry_in: TimeEntryCreate) -> TimeEntry:
    """
    Crea un nuevo registro de horas.
    """
    db_entry = TimeEntry(**entry_in.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_time_entries(
    db: Session,
    id_employee: Optional[int] = None,
    id_project: Optional[int] = None,
    id_client: Optional[int] = None,
    week_start: Optional[date] = None,
) -> List[TimeEntry]:
    """
    Lista registros de horas con filtros opcionales.
    """
    query = db.query(TimeEntry)

    if id_employee is not None:
        query = query.filter(TimeEntry.id_employee == id_employee)

    if id_project is not None:
        query = query.filter(TimeEntry.id_project == id_project)

    if id_client is not None:
        query = query.filter(TimeEntry.id_client == id_client)

    if week_start is not None:
        query = query.filter(TimeEntry.week_start == week_start)

    return query.all()


def get_time_entry(db: Session, id_hours: int) -> Optional[TimeEntry]:
    """
    Obtiene un registro de horas por su ID.
    """
    return (
        db.query(TimeEntry)
        .filter(TimeEntry.id_hours == id_hours)
        .first()
    )


def update_time_entry(
    db: Session,
    id_hours: int,
    entry_in: TimeEntryUpdate,
) -> Optional[TimeEntry]:
    """
    Actualiza parcialmente un registro de horas.
    """
    db_entry = get_time_entry(db, id_hours)
    if not db_entry:
        return None

    data = entry_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_entry, field, value)

    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_time_entry(db: Session, id_hours: int) -> bool:
    """
    Elimina un registro de horas.
    """
    db_entry = get_time_entry(db, id_hours)
    if not db_entry:
        return False

    db.delete(db_entry)
    db.commit()
    return True
