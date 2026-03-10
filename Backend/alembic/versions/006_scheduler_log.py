"""006 - create scheduler_log table

Revision ID: 006
Revises: 005
Create Date: 2026-03-09
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS scheduler_log (
            id VARCHAR PRIMARY KEY,
            run_at TIMESTAMP NOT NULL DEFAULT NOW(),
            period_start VARCHAR NOT NULL,
            period_end VARCHAR NOT NULL,
            invoices_generated INTEGER NOT NULL DEFAULT 0,
            invoices_skipped INTEGER NOT NULL DEFAULT 0,
            status VARCHAR NOT NULL DEFAULT 'success',
            error_message VARCHAR
        )
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS scheduler_log"))
