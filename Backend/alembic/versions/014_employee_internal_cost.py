"""Add employee_internal_costs table

Revision ID: 014
Revises: 013
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "employee_internal_costs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("cost_type", sa.String(20), nullable=True, server_default="hourly"),
        sa.Column("internal_hourly", sa.Numeric(10, 2), nullable=True),
        sa.Column("monthly_salary", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(10), nullable=True, server_default="USD"),
        sa.Column("reference_billing_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_employee_internal_costs_employee_id",
        "employee_internal_costs",
        ["employee_id"],
    )


def downgrade():
    op.drop_index("ix_employee_internal_costs_employee_id", "employee_internal_costs")
    op.drop_table("employee_internal_costs")
