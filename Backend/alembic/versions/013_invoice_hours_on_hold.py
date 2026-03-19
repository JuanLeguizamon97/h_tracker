"""Add invoice_hours_on_hold table

Revision ID: 013
Revises: 012
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoice_hours_on_hold (
            id              VARCHAR PRIMARY KEY,
            invoice_id      VARCHAR NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            line_id         VARCHAR NOT NULL REFERENCES invoice_lines(id) ON DELETE CASCADE,
            employee_name   VARCHAR NOT NULL,
            original_hours  NUMERIC(8, 2) NOT NULL,
            billed_hours    NUMERIC(8, 2) NOT NULL,
            on_hold_hours   NUMERIC(8, 2) NOT NULL,
            rate            NUMERIC(10, 2) NOT NULL,
            on_hold_amount  NUMERIC(12, 2) NOT NULL,
            reason          TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE (invoice_id, line_id)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS invoice_hours_on_hold")
