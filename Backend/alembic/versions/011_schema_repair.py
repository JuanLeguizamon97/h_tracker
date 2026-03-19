"""Schema repair: add missing cap_amount, discount_value; fix invoice_lines user_id and discount_type

Revision ID: 011
Revises: 010
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # 1. invoices.cap_amount — was supposed to be added in 003 but didn't persist
    conn.execute(sa.text(
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS cap_amount NUMERIC(12, 2) NULL"
    ))

    # 2. invoice_lines.discount_value — was supposed to be added in 003 but didn't persist
    #    The old 'discount' column (from 001) stays as-is; we add the new one alongside it
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ADD COLUMN IF NOT EXISTS discount_value NUMERIC(10, 2) NOT NULL DEFAULT 0"
    ))

    # 3. Migrate existing data: copy old 'discount' values into 'discount_value' where they differ
    conn.execute(sa.text(
        "UPDATE invoice_lines SET discount_value = discount WHERE discount_value = 0 AND discount != 0"
    ))

    # 4. invoice_lines.discount_type — make nullable to match the SQLAlchemy model
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ALTER COLUMN discount_type DROP NOT NULL"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ALTER COLUMN discount_type DROP DEFAULT"
    ))

    # 5. invoice_lines.user_id — drop NOT NULL and FK so manual lines (no employee) can be saved
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines DROP CONSTRAINT IF EXISTS invoice_lines_user_id_fkey"
    ))
    conn.execute(sa.text(
        "ALTER TABLE invoice_lines ALTER COLUMN user_id DROP NOT NULL"
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE invoice_lines ALTER COLUMN user_id SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE invoice_lines ALTER COLUMN discount_type SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE invoice_lines ALTER COLUMN discount_type SET DEFAULT 'fixed'"))
    conn.execute(sa.text("ALTER TABLE invoice_lines DROP COLUMN IF EXISTS discount_value"))
    conn.execute(sa.text("ALTER TABLE invoices DROP COLUMN IF EXISTS cap_amount"))
