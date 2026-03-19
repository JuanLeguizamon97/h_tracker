"""Add owner_company + billing fields to projects; create invoice_number_sequences; backfill invoice numbers.

Revision ID: 017
Revises: 016
Create Date: 2026-03-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    # ── 1. Add company + billing columns to projects ──────────────────────────
    op.add_column('projects', sa.Column('owner_company', sa.String(10), nullable=True, server_default='IPC'))
    op.add_column('projects', sa.Column('billing_period', sa.String(20), nullable=True, server_default='monthly'))
    op.add_column('projects', sa.Column('billing_day_of_period', sa.Integer(), nullable=True, server_default='3'))
    op.add_column('projects', sa.Column('custom_period_days', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('billing_anchor_date', sa.Date(), nullable=True))

    # Backfill nulls
    op.execute(text("UPDATE projects SET owner_company = 'IPC' WHERE owner_company IS NULL"))
    op.execute(text("UPDATE projects SET billing_period = 'monthly' WHERE billing_period IS NULL"))
    op.execute(text("UPDATE projects SET billing_day_of_period = 3 WHERE billing_day_of_period IS NULL"))

    # ── 2. Create invoice_number_sequences table ──────────────────────────────
    op.create_table(
        'invoice_number_sequences',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('company', sa.String(10), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('last_sequence', sa.Integer(), nullable=False, server_default='0'),
        sa.UniqueConstraint('company', 'year', name='uq_invoice_seq_company_year'),
    )

    # ── 3. Backfill existing invoices with proper IPC-YYYY-NNN numbers ────────
    conn = op.get_bind()

    # Get all invoices ordered by created_at to preserve original order
    invoices = conn.execute(text(
        "SELECT i.id, i.invoice_number, i.created_at, p.owner_company "
        "FROM invoices i "
        "JOIN projects p ON p.id = i.project_id "
        "ORDER BY i.created_at ASC"
    )).fetchall()

    # Group by (company, year), assign sequential numbers
    from collections import defaultdict
    import datetime
    import uuid

    seq_counters: dict = defaultdict(int)
    seed_values: dict = {}  # (company, year) -> max_seq used

    for row in invoices:
        inv_id, inv_number, created_at, company = row
        company = company or 'IPC'

        # Determine year from created_at
        if isinstance(created_at, str):
            year = int(created_at[:4])
        elif created_at:
            year = created_at.year
        else:
            year = datetime.datetime.now().year

        key = (company, year)
        seq_counters[key] += 1
        seq = seq_counters[key]
        new_number = f"{company}-{year}-{seq:03d}"
        seed_values[key] = seq

        # Only update if the existing number looks like a UUID or old INV- format
        needs_update = (
            inv_number is None or
            not inv_number.startswith(company + '-') or
            inv_number.startswith('INV-')
        )
        if needs_update:
            conn.execute(
                text("UPDATE invoices SET invoice_number = :num WHERE id = :id"),
                {"num": new_number, "id": inv_id}
            )

    # ── 4. Seed invoice_number_sequences with current counters ───────────────
    for (company, year), last_seq in seed_values.items():
        conn.execute(text(
            "INSERT INTO invoice_number_sequences (id, company, year, last_sequence) "
            "VALUES (:id, :company, :year, :seq) "
            "ON CONFLICT (company, year) DO UPDATE SET last_sequence = :seq"
        ), {"id": str(uuid.uuid4()), "company": company, "year": year, "seq": last_seq})

    # Ensure IPC/PI 2026 rows always exist
    for company in ('IPC', 'PI'):
        existing = conn.execute(
            text("SELECT 1 FROM invoice_number_sequences WHERE company=:c AND year=2026"),
            {"c": company}
        ).fetchone()
        if not existing:
            conn.execute(text(
                "INSERT INTO invoice_number_sequences (id, company, year, last_sequence) "
                "VALUES (:id, :company, 2026, 0)"
            ), {"id": str(uuid.uuid4()), "company": company})


def downgrade():
    op.drop_table('invoice_number_sequences')
    op.drop_column('projects', 'billing_anchor_date')
    op.drop_column('projects', 'custom_period_days')
    op.drop_column('projects', 'billing_day_of_period')
    op.drop_column('projects', 'billing_period')
    op.drop_column('projects', 'owner_company')
