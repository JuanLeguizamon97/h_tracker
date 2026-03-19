"""009 - drop hourly_rate from employees (rate lives in project_roles)

Revision ID: 009
Revises: 008
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE employees DROP COLUMN IF EXISTS hourly_rate"))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS hourly_rate NUMERIC(10,2)"))
