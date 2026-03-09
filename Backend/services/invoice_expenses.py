from sqlalchemy.orm import Session
from models.invoice_expenses import InvoiceExpense
from schemas.invoice_expenses import InvoiceExpenseCreate, InvoiceExpenseUpdate
import uuid


def create_expense(db: Session, expense_in: InvoiceExpenseCreate) -> InvoiceExpense:
    expense = InvoiceExpense(
        id=str(uuid.uuid4()),
        **expense_in.model_dump()
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expenses(db: Session, invoice_id: str) -> list[InvoiceExpense]:
    return (
        db.query(InvoiceExpense)
        .filter(InvoiceExpense.invoice_id == invoice_id)
        .order_by(InvoiceExpense.date)
        .all()
    )


def get_expense(db: Session, expense_id: str) -> InvoiceExpense | None:
    return db.query(InvoiceExpense).filter(InvoiceExpense.id == expense_id).first()


def update_expense(db: Session, expense_id: str, expense_in: InvoiceExpenseUpdate) -> InvoiceExpense | None:
    expense = get_expense(db, expense_id)
    if not expense:
        return None
    for field, value in expense_in.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: str) -> bool:
    expense = get_expense(db, expense_id)
    if not expense:
        return False
    db.delete(expense)
    db.commit()
    return True
