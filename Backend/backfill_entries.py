"""
Backfill time entries for all employees from Nov 1, 2025 to today.
Skips weekends and dates that already have an entry for that employee+project.
"""
import uuid
import random
from datetime import date, timedelta
from decimal import Decimal

from config.database import engine, Base, SessionLocal
import models  # ensure all models are registered

from models.employees import Employee
from models.employee_projects import EmployeeProject
from models.time_entries import TimeEntry


def uid():
    return str(uuid.uuid4())


def weekdays_between(start: date, end: date):
    d = start
    while d <= end:
        if d.weekday() < 5:  # Mon–Fri
            yield d
        d += timedelta(days=1)


def seed_entries():
    db = SessionLocal()
    try:
        start = date(2025, 11, 1)
        end = date.today()

        assignments = db.query(EmployeeProject).all()

        # Build set of existing (user_id, project_id, date) to avoid duplicates
        existing = set(
            (te.user_id, te.project_id, te.date)
            for te in db.query(TimeEntry).all()
        )

        # Fixed hours per employee to look realistic
        hours_map = {
            "Juan Leguizamon":   [6.5, 7.0, 8.0, 6.0, 7.5],
            "Laura Garcia":      [4.0, 5.0, 6.0, 4.5, 5.5],
            "Carlos Rodriguez":  [8.0, 7.5, 8.0, 7.0, 8.0],
            "Maria Fernandez":   [7.0, 7.5, 8.0, 7.0, 7.5],
            "Diego Lopez":       [6.0, 6.5, 7.0, 6.0, 6.5],
        }

        new_entries = []
        random.seed(42)

        for assignment in assignments:
            emp = db.query(Employee).filter(Employee.id == assignment.user_id).first()
            if not emp:
                continue

            hours_options = hours_map.get(emp.name, [6.0, 7.0, 8.0])

            for day in weekdays_between(start, end):
                key = (assignment.user_id, assignment.project_id, day)
                if key in existing:
                    continue
                existing.add(key)

                hours = random.choice(hours_options)
                new_entries.append(TimeEntry(
                    id=uid(),
                    user_id=assignment.user_id,
                    project_id=assignment.project_id,
                    role_id=assignment.role_id,
                    date=day,
                    hours=Decimal(str(hours)),
                    billable=True,
                    notes=None,
                ))

        if not new_entries:
            print("No new entries to insert — everything already exists.")
            return

        # Insert in batches
        batch_size = 500
        for i in range(0, len(new_entries), batch_size):
            db.add_all(new_entries[i:i + batch_size])
            db.flush()

        db.commit()
        print(f"Inserted {len(new_entries)} time entries from {start} to {end}.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_entries()
