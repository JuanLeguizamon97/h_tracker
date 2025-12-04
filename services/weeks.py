# services/weeks.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from models.weeks import Week
from schemas.weeks import WeekCreate, WeekUpdate


def create_week(db: Session, week_in: WeekCreate) -> Week:
    """
    Crea un nuevo registro de semana.
    """
    db_week = Week(**week_in.dict())
    db.add(db_week)
    db.commit()
    db.refresh(db_week)
    return db_week


def get_weeks(
    db: Session,
    year_number: Optional[int] = None,
    week_number: Optional[int] = None,
    is_split_month: Optional[bool] = None,
) -> List[Week]:
    """
    Lista semanas con filtros opcionales.
    """
    query = db.query(Week)

    if year_number is not None:
        query = query.filter(Week.year_number == year_number)

    if week_number is not None:
        query = query.filter(Week.week_number == week_number)

    if is_split_month is not None:
        query = query.filter(Week.is_split_month == is_split_month)

    return query.all()


def get_week(db: Session, week_start: date) -> Optional[Week]:
    """
    Obtiene una semana por su fecha de inicio (PK).
    """
    return (
        db.query(Week)
        .filter(Week.week_start == week_start)
        .first()
    )


def update_week(
    db: Session,
    week_start: date,
    week_in: WeekUpdate,
) -> Optional[Week]:
    """
    Actualiza parcialmente una semana.
    """
    db_week = get_week(db, week_start)
    if not db_week:
        return None

    data = week_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_week, field, value)

    db.commit()
    db.refresh(db_week)
    return db_week


def delete_week(db: Session, week_start: date) -> bool:
    """
    Elimina una semana por su PK.
    """
    db_week = get_week(db, week_start)
    if not db_week:
        return False

    db.delete(db_week)
    db.commit()
    return True
