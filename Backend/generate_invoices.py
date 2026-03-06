"""
Generate 10 realistic invoices based on existing time entries and project data.
Each invoice covers a distinct project + month combination with real hours logged.
"""
import uuid
from datetime import date, timedelta
from decimal import Decimal

from config.database import SessionLocal
import models

from models.employees import Employee
from models.projects import Project
from models.project_roles import ProjectRole
from models.employee_projects import EmployeeProject
from models.time_entries import TimeEntry
from models.invoice import Invoice
from models.invoice_lines import InvoiceLine
from models.clients import Client


def uid():
    return str(uuid.uuid4())


def generate():
    db = SessionLocal()
    try:
        # Get next invoice number
        existing_count = db.query(Invoice).count()
        next_num = existing_count + 1

        employees = {e.id: e for e in db.query(Employee).all()}
        projects  = {p.id: p for p in db.query(Project).all()}
        clients   = {c.id: c for c in db.query(Client).all()}
        roles     = {r.id: r for r in db.query(ProjectRole).all()}

        # Define 10 invoice scenarios: (project_name_fragment, month_start, status)
        scenarios = [
            ("Portal Web Corporativo",    date(2025, 11, 1), "paid"),
            ("App Movil Ventas",          date(2025, 11, 1), "sent"),
            ("Sistema ERP",               date(2025, 11, 1), "paid"),
            ("Dashboard BI",              date(2025, 11, 1), "draft"),
            ("Portal Web Corporativo",    date(2025, 12, 1), "paid"),
            ("App Movil Ventas",          date(2025, 12, 1), "sent"),
            ("API REST Microservicios",   date(2025, 12, 1), "paid"),
            ("Plataforma Seguridad",      date(2025, 11, 1), "sent"),
            ("Sistema ERP",               date(2026, 1,  1), "sent"),
            ("Plataforma Seguridad",      date(2025, 12, 1), "draft"),
        ]

        invoices_created = 0

        for project_fragment, month_start, status in scenarios:
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            issue_date = month_end
            due_date = month_end + timedelta(days=30)

            # Find matching project
            project = next((p for p in projects.values() if project_fragment in p.name), None)
            if not project:
                print(f"  Project '{project_fragment}' not found, skipping.")
                continue

            # Check if invoice for this project+month already exists
            already = db.query(Invoice).filter(
                Invoice.project_id == project.id,
                Invoice.issue_date >= month_start,
                Invoice.issue_date <= month_end,
            ).first()
            if already:
                print(f"  Invoice for {project.name} / {month_start.strftime('%b %Y')} already exists, skipping.")
                continue

            # Get time entries for this project in this month
            entries = db.query(TimeEntry).filter(
                TimeEntry.project_id == project.id,
                TimeEntry.date >= month_start,
                TimeEntry.date <= month_end,
                TimeEntry.billable == True,
            ).all()

            if not entries:
                print(f"  No entries for {project.name} / {month_start.strftime('%b %Y')}, skipping.")
                continue

            # Group hours by employee
            emp_hours: dict[str, Decimal] = {}
            for e in entries:
                emp_hours[e.user_id] = emp_hours.get(e.user_id, Decimal("0")) + Decimal(str(e.hours))

            # Build invoice lines using project role rates
            lines = []
            subtotal = Decimal("0")

            for emp_id, hours in emp_hours.items():
                emp = employees.get(emp_id)
                if not emp:
                    continue
                # Find assignment to get role rate
                assignment = db.query(EmployeeProject).filter(
                    EmployeeProject.user_id == emp_id,
                    EmployeeProject.project_id == project.id,
                ).first()
                role = roles.get(assignment.role_id) if assignment and assignment.role_id else None
                rate = Decimal(str(role.hourly_rate_usd)) if role else Decimal("75.00")
                role_name = role.name if role else "Consultant"
                amount = (hours * rate).quantize(Decimal("0.01"))
                subtotal += amount
                lines.append(InvoiceLine(
                    id=uid(),
                    user_id=emp_id,
                    employee_name=emp.name,
                    role_name=role_name,
                    hours=hours,
                    rate_snapshot=rate,
                    amount=amount,
                ))

            if not lines:
                continue

            inv_number = f"INV-2025-{next_num:03d}" if month_start.year == 2025 else f"INV-2026-{next_num:03d}"
            invoice = Invoice(
                id=uid(),
                project_id=project.id,
                status=status,
                invoice_number=inv_number,
                issue_date=issue_date,
                due_date=due_date,
                subtotal=subtotal,
                discount=Decimal("0"),
                total=subtotal,
            )
            db.add(invoice)
            db.flush()

            for line in lines:
                line.invoice_id = invoice.id
                db.add(line)

            client = clients.get(project.client_id)
            print(f"  [{status.upper():6}] {inv_number}  {project.name} / {month_start.strftime('%b %Y')}  "
                  f"client={client.name if client else '?'}  total=${subtotal:,.2f}  lines={len(lines)}")
            next_num += 1
            invoices_created += 1

        db.commit()
        print(f"\nDone — {invoices_created} invoices created.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate()
