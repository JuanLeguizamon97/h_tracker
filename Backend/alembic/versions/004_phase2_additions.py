"""Phase 2: add project/client/employee fields

Revision ID: 004
Revises: 003
Create Date: 2026-03-06
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # ── Projects ──
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_code VARCHAR UNIQUE"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS area_category VARCHAR NULL"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS business_unit VARCHAR NULL"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS referral_id VARCHAR NULL REFERENCES employees(id)"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS referral_type VARCHAR NULL"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS referral_value NUMERIC(10, 2) NULL"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'active'"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS start_date DATE NULL"))
    conn.execute(sa.text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS end_date DATE NULL"))

    # ── Clients ──
    for col in [
        "ADD COLUMN IF NOT EXISTS client_code VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS salutation VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS first_name VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS middle_initial VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS last_name VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS job_title VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS main_phone VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS work_phone VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS mobile VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS main_email VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS street_address_1 VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS street_address_2 VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS city VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS state VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS zip VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS country VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS rep VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS payment_terms VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS team_member VARCHAR NULL",
        "ADD COLUMN IF NOT EXISTS notes TEXT NULL",
    ]:
        conn.execute(sa.text(f"ALTER TABLE clients {col}"))

    # ── Employees ──
    conn.execute(sa.text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS title VARCHAR NULL"))
    conn.execute(sa.text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS department VARCHAR NULL"))
    conn.execute(sa.text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS business_unit VARCHAR NULL"))


def downgrade():
    pass  # not implemented — migrations are additive
