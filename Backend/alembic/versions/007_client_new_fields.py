"""007 - add new fields to clients table

Revision ID: 007
Revises: 006
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""
        ALTER TABLE clients
            ADD COLUMN IF NOT EXISTS industry VARCHAR,
            ADD COLUMN IF NOT EXISTS website VARCHAR,
            ADD COLUMN IF NOT EXISTS tax_id VARCHAR,
            ADD COLUMN IF NOT EXISTS referral_source VARCHAR,
            ADD COLUMN IF NOT EXISTS referred_by VARCHAR,
            ADD COLUMN IF NOT EXISTS acquisition_date DATE,
            ADD COLUMN IF NOT EXISTS contract_start_date DATE,
            ADD COLUMN IF NOT EXISTS contract_end_date DATE,
            ADD COLUMN IF NOT EXISTS billing_rate NUMERIC(10,2),
            ADD COLUMN IF NOT EXISTS billing_currency VARCHAR,
            ADD COLUMN IF NOT EXISTS billing_email VARCHAR
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""
        ALTER TABLE clients
            DROP COLUMN IF EXISTS industry,
            DROP COLUMN IF EXISTS website,
            DROP COLUMN IF EXISTS tax_id,
            DROP COLUMN IF EXISTS referral_source,
            DROP COLUMN IF EXISTS referred_by,
            DROP COLUMN IF EXISTS acquisition_date,
            DROP COLUMN IF EXISTS contract_start_date,
            DROP COLUMN IF EXISTS contract_end_date,
            DROP COLUMN IF EXISTS billing_rate,
            DROP COLUMN IF EXISTS billing_currency,
            DROP COLUMN IF EXISTS billing_email
    """))
