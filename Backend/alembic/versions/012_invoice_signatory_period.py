"""Add signatory and period fields to invoices

Revision ID: 012
Revises: 011
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS signatory_name VARCHAR NULL"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS signatory_title VARCHAR NULL"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS period_start DATE NULL"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS period_end DATE NULL"
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS signatory_name"))
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS signatory_title"))
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS period_start"))
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS period_end"))
