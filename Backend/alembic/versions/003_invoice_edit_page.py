"""Invoice edit page: cap_amount, line discounts, invoice_expenses table

Revision ID: 003
Revises: 002
Create Date: 2026-03-06
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Add cap_amount to invoices
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS cap_amount NUMERIC(12, 2) NULL"
    ))

    # Add discount fields to invoice_lines
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ADD COLUMN IF NOT EXISTS discount_type VARCHAR NULL"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ADD COLUMN IF NOT EXISTS discount_value NUMERIC(10, 2) NOT NULL DEFAULT 0"
    ))

    # Create invoice_expenses table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS invoice_expenses (
            id               VARCHAR PRIMARY KEY,
            invoice_id       VARCHAR NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            date             DATE NOT NULL,
            professional     VARCHAR NULL,
            vendor           VARCHAR NULL,
            description      VARCHAR NULL,
            category         VARCHAR NOT NULL,
            amount_usd       NUMERIC(12, 2) NOT NULL DEFAULT 0,
            payment_source   VARCHAR NULL,
            receipt_attached BOOLEAN NOT NULL DEFAULT false,
            notes            VARCHAR NULL,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS invoice_expenses"))
    conn.execute(sa.text("ALTER TABLE invoice_lines DROP COLUMN IF EXISTS discount_value"))
    conn.execute(sa.text("ALTER TABLE invoice_lines DROP COLUMN IF EXISTS discount_type"))
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS cap_amount"))
