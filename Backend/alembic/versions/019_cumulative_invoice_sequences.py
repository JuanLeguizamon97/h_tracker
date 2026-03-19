"""Seed cumulative invoice number sequences (year=0) from existing invoice counts.

New manual invoices use IPC{N} / PGI{N} format (year=0 row).
Scheduler invoices continue using IPC-YYYY-NNN (year=current-year rows).

Revision ID: 019
Revises: 018
Create Date: 2026-03-17
"""
import uuid
from alembic import op
from sqlalchemy import text

revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Count existing invoices per company to seed the cumulative sequence
    rows = bind.execute(text(
        "SELECT owner_company, COUNT(*) AS cnt FROM invoices GROUP BY owner_company"
    )).fetchall()

    company_counts = {row[0]: int(row[1]) for row in rows if row[0]}

    # Ensure both IPC and PI have a year=0 cumulative row
    for company in ['IPC', 'PI']:
        cnt = company_counts.get(company, 0)
        bind.execute(text("""
            INSERT INTO invoice_number_sequences (id, company, year, last_sequence)
            VALUES (:id, :company, 0, :seq)
            ON CONFLICT (company, year) DO UPDATE
                SET last_sequence = EXCLUDED.last_sequence
        """), {"id": str(uuid.uuid4()), "company": company, "seq": cnt})


def downgrade():
    bind = op.get_bind()
    bind.execute(text(
        "DELETE FROM invoice_number_sequences WHERE year = 0"
    ))
