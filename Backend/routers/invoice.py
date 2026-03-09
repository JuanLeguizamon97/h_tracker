from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from config.database import get_db
from services.invoice import create_invoice, get_invoices, get_invoice, update_invoice, delete_invoice
from services.invoice_expenses import create_expense, get_expenses, get_expense, update_expense, delete_expense
from services.export_pdf import generate_invoice_pdf
from services.export_excel import generate_invoice_xlsx
from schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceOut,
    InvoiceEditDataOut, InvoiceEditClient, InvoiceEditProject, InvoiceEditLine, InvoiceEditExpense,
    InvoicePatch,
)
from schemas.invoice_expenses import InvoiceExpenseCreate
from schemas.invoice_lines import InvoiceLineUpdate
from models.invoice_lines import InvoiceLine
from models.invoice_expenses import InvoiceExpense
from models.projects import Project
from models.clients import Client
from models.employees import Employee
from models.user_roles import UserRole
import uuid

invoice_router = APIRouter(prefix="/invoices", tags=["invoices"])


@invoice_router.post("/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_new_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    return create_invoice(db, invoice_in)


@invoice_router.get("/", response_model=List[InvoiceOut])
def list_invoices(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_invoices(db, project_id=project_id, status=status)


def _build_edit_data(invoice_id: str, db: Session) -> dict:
    """Shared helper — returns a plain dict suitable for PDF/Excel generators and the API response."""
    invoice = get_invoice(db, invoice_id)
    project = db.query(Project).filter(Project.id == invoice.project_id).first()
    client = db.query(Client).filter(Client.id == project.client_id).first() if project else None

    lines_out = []
    for line in invoice.lines:
        user_role = db.query(UserRole).filter(UserRole.user_id == line.user_id).first()
        lines_out.append({
            "id": line.id,
            "user_id": line.user_id,
            "employee_name": line.employee_name,
            "title": line.role_name,
            "role": user_role.role if user_role else None,
            "hours": float(line.hours),
            "hourly_rate": float(line.rate_snapshot),
            "discount_type": line.discount_type,
            "discount_value": float(line.discount_value) if line.discount_value is not None else 0.0,
            "amount": float(line.amount),
        })

    expenses_out = [
        {
            "id": exp.id,
            "date": exp.date,
            "professional": exp.professional,
            "vendor": exp.vendor,
            "description": exp.description,
            "category": exp.category,
            "amount_usd": float(exp.amount_usd),
            "payment_source": exp.payment_source,
            "receipt_attached": exp.receipt_attached,
            "notes": exp.notes,
        }
        for exp in get_expenses(db, invoice_id)
    ]

    return {
        "invoice": {
            "id": invoice.id,
            "project_id": invoice.project_id,
            "status": invoice.status,
            "subtotal": float(invoice.subtotal),
            "discount": float(invoice.discount),
            "total": float(invoice.total),
            "cap_amount": float(invoice.cap_amount) if invoice.cap_amount is not None else None,
            "notes": invoice.notes,
            "invoice_number": invoice.invoice_number,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at,
        },
        "client": {"id": client.id, "name": client.name, "email": client.email, "phone": client.phone} if client else None,
        "project": {"id": project.id, "name": project.name, "client_id": project.client_id} if project else None,
        "lines": lines_out,
        "expenses": expenses_out,
    }


@invoice_router.get("/{invoice_id}/edit-data", response_model=InvoiceEditDataOut)
def get_invoice_edit_data(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    data = _build_edit_data(invoice_id, db)

    def _line(d):
        return InvoiceEditLine(**d)

    def _exp(d):
        return InvoiceEditExpense(**d)

    client_d = data["client"]
    project_d = data["project"]

    return InvoiceEditDataOut(
        invoice=invoice,
        client=InvoiceEditClient(**client_d) if client_d else None,
        project=InvoiceEditProject(**project_d) if project_d else None,
        lines=[_line(l) for l in data["lines"]],
        expenses=[_exp(e) for e in data["expenses"]],
    )


@invoice_router.patch("/{invoice_id}", response_model=InvoiceOut)
def patch_invoice(invoice_id: str, patch_in: InvoicePatch, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # Update simple invoice fields
    simple_fields = ["status", "cap_amount", "invoice_number", "issue_date", "due_date", "notes"]
    for field in simple_fields:
        value = getattr(patch_in, field)
        if value is not None:
            setattr(invoice, field, value)

    # Update lines
    if patch_in.lines:
        for line_patch in patch_in.lines:
            line = db.query(InvoiceLine).filter(
                InvoiceLine.id == line_patch.id,
                InvoiceLine.invoice_id == invoice_id,
            ).first()
            if line:
                if line_patch.hours is not None:
                    line.hours = line_patch.hours
                if line_patch.rate_snapshot is not None:
                    line.rate_snapshot = line_patch.rate_snapshot
                if line_patch.discount_type is not None:
                    line.discount_type = line_patch.discount_type
                if line_patch.discount_value is not None:
                    line.discount_value = line_patch.discount_value
                # Recompute amount
                line.amount = float(line.hours) * float(line.rate_snapshot)

    # Recompute invoice subtotal/total from lines
    db.flush()
    db.refresh(invoice)
    subtotal = sum(float(ln.amount) for ln in invoice.lines)
    total_discount = sum(
        (float(ln.amount) * float(ln.discount_value) / 100)
        if ln.discount_type == "percent"
        else float(ln.discount_value)
        for ln in invoice.lines
    )
    invoice.subtotal = subtotal
    invoice.discount = total_discount
    invoice.total = subtotal - total_discount

    # Handle expenses (upsert)
    if patch_in.expenses is not None:
        for exp_patch in patch_in.expenses:
            if exp_patch.id is None:
                # Create new expense
                new_exp = InvoiceExpense(
                    id=str(uuid.uuid4()),
                    invoice_id=invoice_id,
                    date=exp_patch.date,
                    professional=exp_patch.professional,
                    vendor=exp_patch.vendor,
                    description=exp_patch.description,
                    category=exp_patch.category or "Other",
                    amount_usd=exp_patch.amount_usd or 0,
                    payment_source=exp_patch.payment_source,
                    receipt_attached=exp_patch.receipt_attached or False,
                    notes=exp_patch.notes,
                )
                db.add(new_exp)
            else:
                exp = db.query(InvoiceExpense).filter(
                    InvoiceExpense.id == exp_patch.id,
                    InvoiceExpense.invoice_id == invoice_id,
                ).first()
                if exp:
                    for field in ["date", "professional", "vendor", "description", "category",
                                  "amount_usd", "payment_source", "receipt_attached", "notes"]:
                        value = getattr(exp_patch, field)
                        if value is not None:
                            setattr(exp, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice


@invoice_router.get("/{invoice_id}/export/pdf")
def export_invoice_pdf(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    edit_data = _build_edit_data(invoice_id, db)
    pdf_bytes = generate_invoice_pdf(edit_data)
    inv_label = invoice.invoice_number or invoice_id[:8]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="INV-{inv_label}.pdf"'},
    )


@invoice_router.get("/{invoice_id}/export/xlsx")
def export_invoice_xlsx(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    edit_data = _build_edit_data(invoice_id, db)
    xlsx_bytes = generate_invoice_xlsx(edit_data)
    inv_label = invoice.invoice_number or invoice_id[:8]
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="INV-{inv_label}.xlsx"'},
    )


@invoice_router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@invoice_router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice_detail(invoice_id: str, invoice_in: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice = update_invoice(db, invoice_id, invoice_in)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@invoice_router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    if not delete_invoice(db, invoice_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
