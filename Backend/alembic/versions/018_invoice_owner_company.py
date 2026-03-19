"""Add owner_company to invoices table; backfill from projects.

Revision ID: 018
Revises: 017
Create Date: 2026-03-17
"""
from alembic import op
import sqlalchemy as sa

revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('invoices', sa.Column(
        'owner_company', sa.String(10), nullable=True, server_default='IPC'
    ))

    # Backfill from the project's owner_company
    op.execute("""
        UPDATE invoices
        SET owner_company = p.owner_company
        FROM projects p
        WHERE invoices.project_id = p.id
    """)

    # Fill any remaining NULLs (invoices without a project — shouldn't happen, but safe)
    op.execute("UPDATE invoices SET owner_company = 'IPC' WHERE owner_company IS NULL")


def downgrade():
    op.drop_column('invoices', 'owner_company')
