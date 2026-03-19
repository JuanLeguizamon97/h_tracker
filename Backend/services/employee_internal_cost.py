from sqlalchemy.orm import Session
from models.employee_internal_cost import EmployeeInternalCost
from schemas.employee_internal_cost import EmployeeInternalCostCreate
import uuid
from datetime import datetime, timezone


def get_current_internal_cost(db: Session, employee_id: str) -> EmployeeInternalCost | None:
    """Return the most recent cost record for an employee."""
    return (
        db.query(EmployeeInternalCost)
        .filter(EmployeeInternalCost.employee_id == employee_id)
        .order_by(
            EmployeeInternalCost.effective_from.desc().nullslast(),
            EmployeeInternalCost.created_at.desc(),
        )
        .first()
    )


def get_internal_cost_history(db: Session, employee_id: str) -> list[EmployeeInternalCost]:
    """Return all cost records ordered newest first."""
    return (
        db.query(EmployeeInternalCost)
        .filter(EmployeeInternalCost.employee_id == employee_id)
        .order_by(
            EmployeeInternalCost.effective_from.desc().nullslast(),
            EmployeeInternalCost.created_at.desc(),
        )
        .all()
    )


def upsert_internal_cost(
    db: Session,
    employee_id: str,
    data: EmployeeInternalCostCreate,
    actor_id: str | None = None,
) -> EmployeeInternalCost:
    """
    Insert a new cost record (preserving history).
    If a record with the same effective_from already exists for this employee, update it in-place.
    """
    existing = None
    if data.effective_from:
        existing = (
            db.query(EmployeeInternalCost)
            .filter(
                EmployeeInternalCost.employee_id == employee_id,
                EmployeeInternalCost.effective_from == data.effective_from,
            )
            .first()
        )

    if existing:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        existing.updated_by = actor_id
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    record = EmployeeInternalCost(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        **data.model_dump(),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
