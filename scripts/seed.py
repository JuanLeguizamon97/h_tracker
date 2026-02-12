"""
Seed script — inserts sample domain data for testing.
Idempotent: safe to re-run (uses INSERT ... ON CONFLICT DO NOTHING pattern via check-first).

Usage:
    python -m scripts.seed          (from project root)
    python scripts/seed.py          (alternatively)

Does NOT seed passwords. User rows are created via JIT provisioning on first Azure login.
In AUTH_MODE=mock, a dev identity row is seeded for convenience.
"""
import os
import sys
from datetime import date
from decimal import Decimal

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.database import db_session, engine, Base
from models.employees import Employees
from models.clients import Client
from models.projects import Project
from models.weeks import Week
from models.time_entries import TimeEntry
from models.assigned_projects import AssignedProject
from models.invoice import Invoice  # noqa: F401
from models.invoice_lines import InvoiceLine  # noqa: F401
from models.app_user import AppUser

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def seed():
    db = db_session()
    try:
        _seed_data(db)
        db.commit()
        print("[seed] Done.")
    except Exception as e:
        db.rollback()
        print(f"[seed] Error: {e}")
        raise
    finally:
        db.close()


def _exists(db, model, **kwargs):
    return db.query(model).filter_by(**kwargs).first() is not None


def _seed_data(db):
    # ---------- Mock dev user (only in mock mode) ----------
    auth_mode = os.getenv("AUTH_MODE", "azure")
    if auth_mode == "mock":
        if not _exists(db, AppUser, azure_oid="00000000-0000-0000-0000-000000000001"):
            db.add(AppUser(
                id="u-dev-0001",
                azure_oid="00000000-0000-0000-0000-000000000001",
                email="dev@impactpoint.local",
                display_name="Dev User",
            ))
            print("[seed] Mock dev user created.")

    # ---------- Employees ----------
    employees = [
        {"id_employee": "emp-001", "employee_name": "Alice Johnson", "employee_email": "alice@impactpoint.com", "home_state": "TX", "home_country": "US"},
        {"id_employee": "emp-002", "employee_name": "Bob Martinez", "employee_email": "bob@impactpoint.com", "home_state": "CA", "home_country": "US"},
        {"id_employee": "emp-003", "employee_name": "Carol Chen", "employee_email": "carol@impactpoint.com", "home_state": "NY", "home_country": "US"},
    ]
    for e in employees:
        if not _exists(db, Employees, id_employee=e["id_employee"]):
            db.add(Employees(**e))
            print(f"[seed] Employee: {e['employee_name']}")

    # ---------- Clients ----------
    clients = [
        {
            "primary_id_client": "cli-ent-001",
            "second_id_client": "cli-grp-001",
            "client_name": "Acme Corporation",
            "contact_name": "John Doe",
            "contact_email": "john@acme.com",
            "billing_city": "Austin",
            "billing_state": "TX",
            "billing_country": "US",
        },
        {
            "primary_id_client": "cli-ent-002",
            "second_id_client": "cli-grp-002",
            "client_name": "Globex Industries",
            "contact_name": "Jane Smith",
            "contact_email": "jane@globex.com",
            "billing_city": "San Francisco",
            "billing_state": "CA",
            "billing_country": "US",
        },
    ]
    for c in clients:
        if not _exists(db, Client, primary_id_client=c["primary_id_client"], second_id_client=c["second_id_client"]):
            db.add(Client(**c))
            print(f"[seed] Client: {c['client_name']}")

    # ---------- Projects ----------
    projects = [
        {"id_project": "proj-001", "id_client": "cli-grp-001", "project_name": "Acme Website Redesign", "hourly_rate": Decimal("150.00")},
        {"id_project": "proj-002", "id_client": "cli-grp-001", "project_name": "Acme Mobile App", "hourly_rate": Decimal("175.00")},
        {"id_project": "proj-003", "id_client": "cli-grp-002", "project_name": "Globex Data Migration", "hourly_rate": Decimal("200.00")},
    ]
    for p in projects:
        if not _exists(db, Project, id_project=p["id_project"]):
            db.add(Project(**p))
            print(f"[seed] Project: {p['project_name']}")

    # ---------- Weeks ----------
    weeks = [
        {"week_start": date(2026, 1, 5), "week_end": date(2026, 1, 11), "week_number": 2, "year_number": 2026, "is_split_month": False},
        {"week_start": date(2026, 1, 12), "week_end": date(2026, 1, 18), "week_number": 3, "year_number": 2026, "is_split_month": False},
        {"week_start": date(2026, 1, 26), "week_end": date(2026, 2, 1), "week_number": 5, "year_number": 2026, "is_split_month": True, "month_a_key": 1, "month_b_key": 2, "qty_days_a": 5, "qty_days_b": 2},
        {"week_start": date(2026, 2, 2), "week_end": date(2026, 2, 8), "week_number": 6, "year_number": 2026, "is_split_month": False},
    ]
    for w in weeks:
        if not _exists(db, Week, week_start=w["week_start"]):
            db.add(Week(**w))
            print(f"[seed] Week: {w['week_start']}")

    # ---------- Assigned projects ----------
    assignments = [
        {"id": "ap-001", "employee_id": "emp-001", "project_id": "proj-001", "client_id": "cli-grp-001"},
        {"id": "ap-002", "employee_id": "emp-001", "project_id": "proj-002", "client_id": "cli-grp-001"},
        {"id": "ap-003", "employee_id": "emp-002", "project_id": "proj-003", "client_id": "cli-grp-002"},
        {"id": "ap-004", "employee_id": "emp-003", "project_id": "proj-001", "client_id": "cli-grp-001"},
    ]
    for a in assignments:
        if not _exists(db, AssignedProject, id=a["id"]):
            db.add(AssignedProject(**a))
            print(f"[seed] Assignment: {a['employee_id']} -> {a['project_id']}")

    # ---------- Time entries ----------
    entries = [
        {"id_hours": "te-001", "id_employee": "emp-001", "id_project": "proj-001", "id_client": "cli-grp-001", "week_start": date(2026, 1, 5), "total_hours": Decimal("40.00"), "billable": True, "location_type": "remote"},
        {"id_hours": "te-002", "id_employee": "emp-002", "id_project": "proj-003", "id_client": "cli-grp-002", "week_start": date(2026, 1, 5), "total_hours": Decimal("32.00"), "billable": True, "location_type": "onsite", "location_value": "SF Office"},
        {"id_hours": "te-003", "id_employee": "emp-003", "id_project": "proj-001", "id_client": "cli-grp-001", "week_start": date(2026, 1, 12), "total_hours": Decimal("24.50"), "billable": True, "location_type": "remote"},
    ]
    for t in entries:
        if not _exists(db, TimeEntry, id_hours=t["id_hours"]):
            db.add(TimeEntry(**t))
            print(f"[seed] TimeEntry: {t['id_hours']}")

    db.flush()
    print("[seed] All seed data inserted.")


if __name__ == "__main__":
    seed()
