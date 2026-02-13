"""
Seed script: creates tables and loads dummy data into PostgreSQL.

Usage:
    cd Backend
    python seed.py
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from config.database import engine, Base, SessionLocal

# Import ALL models so SQLAlchemy registers them on Base.metadata
from models.employees import Employees
from models.clients import Client
from models.projects import Project
from models.weeks import Week
from models.time_entries import TimeEntry
from models.assigned_projects import AssignedProject
from models.invoice import Invoice
from models.invoice_lines import InvoiceLine


def uid() -> str:
    return str(uuid.uuid4())


def _exists(db, model, **kwargs):
    return db.query(model).filter_by(**kwargs).first() is not None


def seed():
    # Ensure tables exist (idempotent, does not drop existing data)
    Base.metadata.create_all(bind=engine)
    print("Tables verified.")

    db = SessionLocal()

    try:
        # Skip if data already exists (idempotent)
        if db.query(Employees).first() is not None:
            print("[seed] Data already exists, skipping.")
            return

        # ============================================================
        # EMPLOYEES
        # ============================================================
        emp_admin = Employees(
            id_employee=uid(),
            employee_name="Juan Leguizamón",
            employee_email="juan@impactpoint.com",
            home_state="Florida",
            home_country="US",
            role="admin",
            hourly_rate=Decimal("75.00"),
        )
        emp_laura = Employees(
            id_employee=uid(),
            employee_name="Laura García",
            employee_email="laura@impactpoint.com",
            home_state="Texas",
            home_country="US",
            role="employee",
            hourly_rate=Decimal("55.00"),
        )
        emp_carlos = Employees(
            id_employee=uid(),
            employee_name="Carlos Rodríguez",
            employee_email="carlos@impactpoint.com",
            home_state="California",
            home_country="US",
            role="employee",
            hourly_rate=Decimal("60.00"),
        )
        emp_maria = Employees(
            id_employee=uid(),
            employee_name="María Fernández",
            employee_email="maria@impactpoint.com",
            home_state="New York",
            home_country="US",
            role="employee",
            hourly_rate=Decimal("50.00"),
        )
        emp_diego = Employees(
            id_employee=uid(),
            employee_name="Diego López",
            employee_email="diego@impactpoint.com",
            home_state="Illinois",
            home_country="US",
            role="admin",
            hourly_rate=Decimal("70.00"),
        )

        employees = [emp_admin, emp_laura, emp_carlos, emp_maria, emp_diego]
        db.add_all(employees)
        db.flush()
        print(f"  {len(employees)} employees inserted.")

        # ============================================================
        # CLIENTS
        # ============================================================
        cl_acme = Client(
            primary_id_client=uid(),
            second_id_client=uid(),
            client_name="Acme Corporation",
            contact_name="John Smith",
            contact_title="CTO",
            contact_email="jsmith@acme.com",
            contact_phone="+1 305 555 0100",
            billing_address_line1="123 Main St",
            billing_city="Miami",
            billing_state="FL",
            billing_postal_code=33101,
            billing_country="US",
            active=True,
        )
        cl_globex = Client(
            primary_id_client=uid(),
            second_id_client=uid(),
            client_name="Globex Industries",
            contact_name="Sarah Connor",
            contact_title="VP Engineering",
            contact_email="sconnor@globex.com",
            contact_phone="+1 212 555 0200",
            billing_address_line1="456 Park Ave",
            billing_city="New York",
            billing_state="NY",
            billing_postal_code=10022,
            billing_country="US",
            active=True,
        )
        cl_initech = Client(
            primary_id_client=uid(),
            second_id_client=uid(),
            client_name="Initech Solutions",
            contact_name="Bill Lumbergh",
            contact_title="Director",
            contact_email="bill@initech.com",
            contact_phone="+1 415 555 0300",
            billing_address_line1="789 Market St",
            billing_city="San Francisco",
            billing_state="CA",
            billing_postal_code=94105,
            billing_country="US",
            active=True,
        )
        cl_wayne = Client(
            primary_id_client=uid(),
            second_id_client=uid(),
            client_name="Wayne Enterprises",
            contact_name="Lucius Fox",
            contact_title="CEO",
            contact_email="lfox@wayne.com",
            contact_phone="+1 312 555 0400",
            billing_address_line1="1007 Wayne Tower",
            billing_city="Chicago",
            billing_state="IL",
            billing_postal_code=60601,
            billing_country="US",
            active=True,
        )
        cl_inactive = Client(
            primary_id_client=uid(),
            second_id_client=uid(),
            client_name="Old Client LLC",
            contact_name="Nobody",
            contact_email="old@client.com",
            active=False,
        )

        clients = [cl_acme, cl_globex, cl_initech, cl_wayne, cl_inactive]
        db.add_all(clients)
        db.flush()
        print(f"  {len(clients)} clients inserted.")

        # ============================================================
        # PROJECTS
        # ============================================================
        prj_acme_web = Project(
            id_project=uid(),
            id_client=cl_acme.second_id_client,
            project_name="Portal Web Corporativo",
            billable_default=True,
            hourly_rate=Decimal("85.00"),
            active=True,
        )
        prj_acme_mobile = Project(
            id_project=uid(),
            id_client=cl_acme.second_id_client,
            project_name="App Móvil Ventas",
            billable_default=True,
            hourly_rate=Decimal("90.00"),
            active=True,
        )
        prj_globex_erp = Project(
            id_project=uid(),
            id_client=cl_globex.second_id_client,
            project_name="Sistema ERP",
            billable_default=True,
            hourly_rate=Decimal("100.00"),
            active=True,
        )
        prj_globex_bi = Project(
            id_project=uid(),
            id_client=cl_globex.second_id_client,
            project_name="Dashboard BI",
            billable_default=True,
            hourly_rate=Decimal("80.00"),
            active=True,
        )
        prj_initech_api = Project(
            id_project=uid(),
            id_client=cl_initech.second_id_client,
            project_name="API REST Microservicios",
            billable_default=True,
            hourly_rate=Decimal("95.00"),
            active=True,
        )
        prj_wayne_sec = Project(
            id_project=uid(),
            id_client=cl_wayne.second_id_client,
            project_name="Plataforma Seguridad",
            billable_default=True,
            hourly_rate=Decimal("110.00"),
            active=True,
        )
        prj_inactive = Project(
            id_project=uid(),
            id_client=cl_inactive.second_id_client,
            project_name="Proyecto Antiguo",
            billable_default=False,
            active=False,
        )

        projects = [
            prj_acme_web, prj_acme_mobile, prj_globex_erp,
            prj_globex_bi, prj_initech_api, prj_wayne_sec, prj_inactive,
        ]
        db.add_all(projects)
        db.flush()
        print(f"  {len(projects)} projects inserted.")

        # ============================================================
        # ASSIGNED PROJECTS
        # ============================================================
        assignments = [
            # Juan (admin) → all active projects
            AssignedProject(id=uid(), employee_id=emp_admin.id_employee, project_id=prj_acme_web.id_project, client_id=cl_acme.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_admin.id_employee, project_id=prj_globex_erp.id_project, client_id=cl_globex.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_admin.id_employee, project_id=prj_wayne_sec.id_project, client_id=cl_wayne.second_id_client),
            # Laura → Acme + Globex
            AssignedProject(id=uid(), employee_id=emp_laura.id_employee, project_id=prj_acme_web.id_project, client_id=cl_acme.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_laura.id_employee, project_id=prj_acme_mobile.id_project, client_id=cl_acme.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_laura.id_employee, project_id=prj_globex_bi.id_project, client_id=cl_globex.second_id_client),
            # Carlos → Globex + Initech
            AssignedProject(id=uid(), employee_id=emp_carlos.id_employee, project_id=prj_globex_erp.id_project, client_id=cl_globex.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_carlos.id_employee, project_id=prj_initech_api.id_project, client_id=cl_initech.second_id_client),
            # María → Initech + Wayne
            AssignedProject(id=uid(), employee_id=emp_maria.id_employee, project_id=prj_initech_api.id_project, client_id=cl_initech.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_maria.id_employee, project_id=prj_wayne_sec.id_project, client_id=cl_wayne.second_id_client),
            # Diego → Wayne + Acme
            AssignedProject(id=uid(), employee_id=emp_diego.id_employee, project_id=prj_wayne_sec.id_project, client_id=cl_wayne.second_id_client),
            AssignedProject(id=uid(), employee_id=emp_diego.id_employee, project_id=prj_acme_mobile.id_project, client_id=cl_acme.second_id_client),
        ]
        db.add_all(assignments)
        db.flush()
        print(f"  {len(assignments)} project assignments inserted.")

        # ============================================================
        # WEEKS  (Jan & Feb 2026)
        # ============================================================
        weeks_data = [
            # January 2026
            Week(week_start=date(2025, 12, 29), week_end=date(2026, 1, 4), week_number=1, year_number=2026, is_split_month=True, month_a_key=12, month_b_key=1, qty_days_a=3, qty_days_b=4),
            Week(week_start=date(2026, 1, 5), week_end=date(2026, 1, 11), week_number=2, year_number=2026),
            Week(week_start=date(2026, 1, 12), week_end=date(2026, 1, 18), week_number=3, year_number=2026),
            Week(week_start=date(2026, 1, 19), week_end=date(2026, 1, 25), week_number=4, year_number=2026),
            Week(week_start=date(2026, 1, 26), week_end=date(2026, 2, 1), week_number=5, year_number=2026, is_split_month=True, month_a_key=1, month_b_key=2, qty_days_a=6, qty_days_b=1),
            # February 2026
            Week(week_start=date(2026, 2, 2), week_end=date(2026, 2, 8), week_number=6, year_number=2026),
            Week(week_start=date(2026, 2, 9), week_end=date(2026, 2, 15), week_number=7, year_number=2026),
            Week(week_start=date(2026, 2, 16), week_end=date(2026, 2, 22), week_number=8, year_number=2026),
            Week(week_start=date(2026, 2, 23), week_end=date(2026, 3, 1), week_number=9, year_number=2026, is_split_month=True, month_a_key=2, month_b_key=3, qty_days_a=5, qty_days_b=2),
        ]
        db.add_all(weeks_data)
        db.flush()
        print(f"  {len(weeks_data)} weeks inserted.")

        # ============================================================
        # TIME ENTRIES  (spread across Jan & Feb 2026)
        # ============================================================
        def te(emp, prj, cli, ws, hours, loc="remote"):
            return TimeEntry(
                id_hours=uid(),
                id_employee=emp.id_employee,
                id_project=prj.id_project,
                id_client=cli.second_id_client,
                week_start=ws,
                total_hours=Decimal(str(hours)),
                billable=True,
                location_type=loc,
                created_at=datetime.now(timezone.utc),
            )

        time_entries = [
            # ---- Week 2 (Jan 5) ----
            te(emp_admin, prj_acme_web, cl_acme, date(2026, 1, 5), 32),
            te(emp_admin, prj_globex_erp, cl_globex, date(2026, 1, 5), 8),
            te(emp_laura, prj_acme_web, cl_acme, date(2026, 1, 5), 20),
            te(emp_laura, prj_acme_mobile, cl_acme, date(2026, 1, 5), 16),
            te(emp_carlos, prj_globex_erp, cl_globex, date(2026, 1, 5), 40, "onsite"),
            te(emp_maria, prj_initech_api, cl_initech, date(2026, 1, 5), 35),
            te(emp_diego, prj_wayne_sec, cl_wayne, date(2026, 1, 5), 30),
            te(emp_diego, prj_acme_mobile, cl_acme, date(2026, 1, 5), 10),

            # ---- Week 3 (Jan 12) ----
            te(emp_admin, prj_acme_web, cl_acme, date(2026, 1, 12), 25),
            te(emp_admin, prj_wayne_sec, cl_wayne, date(2026, 1, 12), 15),
            te(emp_laura, prj_globex_bi, cl_globex, date(2026, 1, 12), 40),
            te(emp_carlos, prj_initech_api, cl_initech, date(2026, 1, 12), 32),
            te(emp_carlos, prj_globex_erp, cl_globex, date(2026, 1, 12), 8),
            te(emp_maria, prj_wayne_sec, cl_wayne, date(2026, 1, 12), 40, "onsite"),
            te(emp_diego, prj_wayne_sec, cl_wayne, date(2026, 1, 12), 40),

            # ---- Week 4 (Jan 19) ----
            te(emp_admin, prj_globex_erp, cl_globex, date(2026, 1, 19), 40),
            te(emp_laura, prj_acme_web, cl_acme, date(2026, 1, 19), 24),
            te(emp_laura, prj_acme_mobile, cl_acme, date(2026, 1, 19), 16),
            te(emp_carlos, prj_initech_api, cl_initech, date(2026, 1, 19), 40),
            te(emp_maria, prj_initech_api, cl_initech, date(2026, 1, 19), 20),
            te(emp_maria, prj_wayne_sec, cl_wayne, date(2026, 1, 19), 20),
            te(emp_diego, prj_acme_mobile, cl_acme, date(2026, 1, 19), 40),

            # ---- Week 6 (Feb 2) ----
            te(emp_admin, prj_acme_web, cl_acme, date(2026, 2, 2), 30),
            te(emp_admin, prj_wayne_sec, cl_wayne, date(2026, 2, 2), 10),
            te(emp_laura, prj_globex_bi, cl_globex, date(2026, 2, 2), 36),
            te(emp_laura, prj_acme_web, cl_acme, date(2026, 2, 2), 4),
            te(emp_carlos, prj_globex_erp, cl_globex, date(2026, 2, 2), 24),
            te(emp_carlos, prj_initech_api, cl_initech, date(2026, 2, 2), 16),
            te(emp_maria, prj_wayne_sec, cl_wayne, date(2026, 2, 2), 40, "onsite"),
            te(emp_diego, prj_wayne_sec, cl_wayne, date(2026, 2, 2), 32),
            te(emp_diego, prj_acme_mobile, cl_acme, date(2026, 2, 2), 8),

            # ---- Week 7 (Feb 9 – current week) ----
            te(emp_admin, prj_acme_web, cl_acme, date(2026, 2, 9), 20),
            te(emp_admin, prj_globex_erp, cl_globex, date(2026, 2, 9), 16),
            te(emp_laura, prj_acme_mobile, cl_acme, date(2026, 2, 9), 30),
            te(emp_laura, prj_globex_bi, cl_globex, date(2026, 2, 9), 10),
            te(emp_carlos, prj_initech_api, cl_initech, date(2026, 2, 9), 40),
            te(emp_maria, prj_initech_api, cl_initech, date(2026, 2, 9), 24),
            te(emp_maria, prj_wayne_sec, cl_wayne, date(2026, 2, 9), 16),
            te(emp_diego, prj_wayne_sec, cl_wayne, date(2026, 2, 9), 40),
        ]

        db.add_all(time_entries)
        db.flush()
        print(f"  {len(time_entries)} time entries inserted.")

        # ============================================================
        # INVOICES  (one per client for January)
        # ============================================================
        inv_acme = Invoice(
            id_invoice=uid(),
            invoice_number="INV-2026-001",
            primary_id_client=cl_acme.primary_id_client,
            second_id_client=cl_acme.second_id_client,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            issue_date=date(2026, 2, 1),
            total_hours=Decimal("182"),
            total_fees=Decimal("15470.00"),
            status="sent",
        )
        inv_globex = Invoice(
            id_invoice=uid(),
            invoice_number="INV-2026-002",
            primary_id_client=cl_globex.primary_id_client,
            second_id_client=cl_globex.second_id_client,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            issue_date=date(2026, 2, 1),
            total_hours=Decimal("136"),
            total_fees=Decimal("12240.00"),
            status="draft",
        )

        invoices = [inv_acme, inv_globex]
        db.add_all(invoices)
        db.flush()
        print(f"  {len(invoices)} invoices inserted.")

        # ============================================================
        # INVOICE LINES
        # ============================================================
        invoice_lines = [
            InvoiceLine(
                id_invoice_line=uid(),
                id_invoice=inv_acme.id_invoice,
                id_employee=emp_admin.id_employee,
                id_project=prj_acme_web.id_project,
                role_title="Senior Developer",
                hourly_rate=Decimal("75.00"),
                hours=Decimal("57"),
                subtotal=Decimal("4275.00"),
                discount=Decimal("0"),
                total=Decimal("4275.00"),
            ),
            InvoiceLine(
                id_invoice_line=uid(),
                id_invoice=inv_acme.id_invoice,
                id_employee=emp_laura.id_employee,
                id_project=prj_acme_web.id_project,
                role_title="Frontend Developer",
                hourly_rate=Decimal("55.00"),
                hours=Decimal("44"),
                subtotal=Decimal("2420.00"),
                discount=Decimal("0"),
                total=Decimal("2420.00"),
            ),
            InvoiceLine(
                id_invoice_line=uid(),
                id_invoice=inv_globex.id_invoice,
                id_employee=emp_carlos.id_employee,
                id_project=prj_globex_erp.id_project,
                role_title="Backend Developer",
                hourly_rate=Decimal("60.00"),
                hours=Decimal("48"),
                subtotal=Decimal("2880.00"),
                discount=Decimal("0"),
                total=Decimal("2880.00"),
            ),
        ]
        db.add_all(invoice_lines)
        db.flush()
        print(f"  {len(invoice_lines)} invoice lines inserted.")

        # ============================================================
        db.commit()
        print("\nSeed completed successfully!")
        print(f"\nSummary:")
        print(f"  Employees:     {len(employees)}")
        print(f"  Clients:       {len(clients)}")
        print(f"  Projects:      {len(projects)}")
        print(f"  Assignments:   {len(assignments)}")
        print(f"  Weeks:         {len(weeks_data)}")
        print(f"  Time Entries:  {len(time_entries)}")
        print(f"  Invoices:      {len(invoices)}")
        print(f"  Invoice Lines: {len(invoice_lines)}")

    except Exception as e:
        db.rollback()
        print(f"\nError during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
