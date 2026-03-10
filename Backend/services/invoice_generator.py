import logging
import uuid
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.invoice import Invoice
from models.invoice_lines import InvoiceLine
from models.invoice_time_entries import InvoiceTimeEntry
from models.projects import Project
from models.time_entries import TimeEntry
from models.employee_projects import EmployeeProject
from models.project_roles import ProjectRole
from models.employees import Employee

logger = logging.getLogger(__name__)


def generate_invoices_for_period(db: Session, period_start: date, period_end: date) -> dict:
    """
    For each active, non-internal project that has unlinked billable time entries
    in the given period, generate one Draft invoice.
    Skip projects that already have an invoice for this period.
    Returns: {"generated": int, "skipped": int, "errors": list}
    """
    generated = 0
    skipped = 0
    errors = []

    active_projects = db.query(Project).filter(
        Project.is_active == True,
        Project.is_internal == False,
    ).all()

    for project in active_projects:
        try:
            # Skip if invoice already exists for this period
            existing = db.query(Invoice).filter(
                Invoice.project_id == project.id,
                Invoice.issue_date >= period_start,
                Invoice.issue_date <= period_end,
            ).first()
            if existing:
                skipped += 1
                logger.info(f"Skipping project {project.id}: invoice already exists for period")
                continue

            # Get linked time entry IDs
            linked_ids_result = db.execute(
                text("SELECT time_entry_id FROM invoice_time_entries")
            ).fetchall()
            linked_ids = {row[0] for row in linked_ids_result}

            # Get unlinked billable time entries for this period
            entries = db.query(TimeEntry).filter(
                TimeEntry.project_id == project.id,
                TimeEntry.billable == True,
                TimeEntry.status == 'normal',
                TimeEntry.date >= period_start,
                TimeEntry.date <= period_end,
            ).all()
            entries = [e for e in entries if e.id not in linked_ids]

            if not entries:
                skipped += 1
                logger.info(f"Skipping project {project.id}: no unlinked billable entries")
                continue

            # Generate invoice number INV-{YYYY}-{seq:03d}
            year = period_end.year
            count_result = db.execute(
                text(f"SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE 'INV-{year}-%'")
            ).scalar()
            seq = (count_result or 0) + 1
            invoice_number = f"INV-{year}-{seq:03d}"

            # Create invoice
            invoice = Invoice(
                id=str(uuid.uuid4()),
                project_id=project.id,
                status="draft",
                subtotal=0,
                discount=0,
                total=0,
                invoice_number=invoice_number,
                issue_date=date.today(),
                notes=f"[Auto-generated] Period: {period_start} to {period_end}",
            )
            db.add(invoice)
            db.flush()

            # Get project roles and employee assignments
            assignments = db.query(EmployeeProject).filter(
                EmployeeProject.project_id == project.id
            ).all()
            assign_map = {a.user_id: a.role_id for a in assignments}

            roles = db.query(ProjectRole).filter(
                ProjectRole.project_id == project.id
            ).all()
            role_map = {r.id: r for r in roles}

            # Group entries by user_id
            employee_hours: dict = {}
            for entry in entries:
                uid = entry.user_id
                if uid not in employee_hours:
                    employee = db.query(Employee).filter(Employee.id == uid).first()
                    employee_hours[uid] = {
                        "user_id": uid,
                        "name": employee.name if employee else "Unknown",
                        "hours": 0,
                        "entry_ids": [],
                    }
                employee_hours[uid]["hours"] += float(entry.hours)
                employee_hours[uid]["entry_ids"].append(entry.id)

            # Create invoice lines
            subtotal = 0.0
            for uid, data in employee_hours.items():
                role_id = assign_map.get(uid)
                role = role_map.get(role_id) if role_id else None
                rate = float(role.hourly_rate_usd) if role else 0.0
                role_name = role.name if role else None
                amount = data["hours"] * rate

                line = InvoiceLine(
                    id=str(uuid.uuid4()),
                    invoice_id=invoice.id,
                    user_id=uid,
                    employee_name=data["name"],
                    role_name=role_name,
                    hours=data["hours"],
                    rate_snapshot=rate,
                    amount=amount,
                    discount_type="amount",
                    discount_value=0,
                )
                db.add(line)
                subtotal += amount

            # Link time entries
            for uid, data in employee_hours.items():
                for entry_id in data["entry_ids"]:
                    link = InvoiceTimeEntry(
                        id=str(uuid.uuid4()),
                        invoice_id=invoice.id,
                        time_entry_id=entry_id,
                    )
                    db.add(link)

            # Update invoice totals
            invoice.subtotal = subtotal
            invoice.total = subtotal

            db.commit()
            generated += 1
            logger.info(f"Auto-generated invoice {invoice_number} for project {project.id} ({period_start} -> {period_end})")

        except Exception as e:
            db.rollback()
            errors.append(str(e))
            logger.error(f"Error generating invoice for project {project.id}: {e}")

    return {"generated": generated, "skipped": skipped, "errors": errors}
