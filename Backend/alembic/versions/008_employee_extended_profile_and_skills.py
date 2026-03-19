"""008 - employee extended profile + skill_catalog + employee_skills tables

Revision ID: 008
Revises: 007
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # ── 1. Extend employees table ──────────────────────────────────────────────
    conn.execute(sa.text("""
        ALTER TABLE employees
            ADD COLUMN IF NOT EXISTS first_name VARCHAR,
            ADD COLUMN IF NOT EXISTS last_name VARCHAR,
            ADD COLUMN IF NOT EXISTS date_of_birth DATE,
            ADD COLUMN IF NOT EXISTS gender VARCHAR,
            ADD COLUMN IF NOT EXISTS personal_email VARCHAR,
            ADD COLUMN IF NOT EXISTS personal_phone VARCHAR,
            ADD COLUMN IF NOT EXISTS id_number VARCHAR,
            ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR,
            ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR,
            ADD COLUMN IF NOT EXISTS country VARCHAR,
            ADD COLUMN IF NOT EXISTS state VARCHAR,
            ADD COLUMN IF NOT EXISTS city VARCHAR,
            ADD COLUMN IF NOT EXISTS timezone VARCHAR,
            ADD COLUMN IF NOT EXISTS street_address VARCHAR,
            ADD COLUMN IF NOT EXISTS zip_code VARCHAR,
            ADD COLUMN IF NOT EXISTS work_mode VARCHAR,
            ADD COLUMN IF NOT EXISTS corporate_phone VARCHAR,
            ADD COLUMN IF NOT EXISTS employee_code VARCHAR,
            ADD COLUMN IF NOT EXISTS employment_type VARCHAR,
            ADD COLUMN IF NOT EXISTS start_date DATE,
            ADD COLUMN IF NOT EXISTS end_date DATE,
            ADD COLUMN IF NOT EXISTS employment_status VARCHAR,
            ADD COLUMN IF NOT EXISTS billing_currency VARCHAR,
            ADD COLUMN IF NOT EXISTS notes TEXT
    """))

    # ── 2. Create skill_catalog table ─────────────────────────────────────────
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS skill_catalog (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))

    # ── 3. Create employee_skills table ───────────────────────────────────────
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS employee_skills (
            id VARCHAR PRIMARY KEY,
            employee_id VARCHAR NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            skill_catalog_id VARCHAR REFERENCES skill_catalog(id),
            skill_name VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            proficiency_level INTEGER NOT NULL DEFAULT 1,
            years_experience NUMERIC(4,1),
            certified BOOLEAN NOT NULL DEFAULT FALSE,
            certificate_name VARCHAR,
            cert_expiry_date DATE,
            notes VARCHAR,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS employee_skills"))
    conn.execute(sa.text("DROP TABLE IF EXISTS skill_catalog"))
    conn.execute(sa.text("""
        ALTER TABLE employees
            DROP COLUMN IF EXISTS first_name,
            DROP COLUMN IF EXISTS last_name,
            DROP COLUMN IF EXISTS date_of_birth,
            DROP COLUMN IF EXISTS gender,
            DROP COLUMN IF EXISTS personal_email,
            DROP COLUMN IF EXISTS personal_phone,
            DROP COLUMN IF EXISTS id_number,
            DROP COLUMN IF EXISTS emergency_contact_name,
            DROP COLUMN IF EXISTS emergency_contact_phone,
            DROP COLUMN IF EXISTS country,
            DROP COLUMN IF EXISTS state,
            DROP COLUMN IF EXISTS city,
            DROP COLUMN IF EXISTS timezone,
            DROP COLUMN IF EXISTS street_address,
            DROP COLUMN IF EXISTS zip_code,
            DROP COLUMN IF EXISTS work_mode,
            DROP COLUMN IF EXISTS corporate_phone,
            DROP COLUMN IF EXISTS employee_code,
            DROP COLUMN IF EXISTS employment_type,
            DROP COLUMN IF EXISTS start_date,
            DROP COLUMN IF EXISTS end_date,
            DROP COLUMN IF EXISTS employment_status,
            DROP COLUMN IF EXISTS billing_currency,
            DROP COLUMN IF EXISTS notes
    """))
