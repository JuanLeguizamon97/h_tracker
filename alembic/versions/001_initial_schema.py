"""Initial schema - all tables

Revision ID: 001
Revises:
Create Date: 2026-02-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # app_users (Azure JIT provisioned)
    op.create_table(
        "app_users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("azure_oid", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_app_users_azure_oid", "app_users", ["azure_oid"])

    # employees
    op.create_table(
        "employees",
        sa.Column("id_employee", sa.String(), primary_key=True),
        sa.Column("employee_name", sa.String(), nullable=False),
        sa.Column("employee_email", sa.String(), nullable=False, unique=True),
        sa.Column("home_state", sa.String(), nullable=True),
        sa.Column("home_country", sa.String(), nullable=True),
    )

    # clients
    op.create_table(
        "clients",
        sa.Column("primary_id_client", sa.String(), primary_key=True),
        sa.Column("second_id_client", sa.String(), primary_key=True),
        sa.Column("client_name", sa.String(), nullable=False),
        sa.Column("contact_name", sa.String(), nullable=True),
        sa.Column("contact_title", sa.String(), nullable=True),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("contact_phone", sa.String(), nullable=True),
        sa.Column("billing_address_line1", sa.String(), nullable=True),
        sa.Column("billing_address_line2", sa.String(), nullable=True),
        sa.Column("billing_city", sa.String(), nullable=True),
        sa.Column("billing_state", sa.String(), nullable=True),
        sa.Column("billing_postal_code", sa.Integer(), nullable=True),
        sa.Column("billing_country", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_unique_constraint("uq_clients_second_id", "clients", ["second_id_client"])

    # projects
    op.create_table(
        "projects",
        sa.Column("id_project", sa.String(), primary_key=True),
        sa.Column("id_client", sa.String(), sa.ForeignKey("clients.second_id_client"), nullable=False),
        sa.Column("project_name", sa.String(), nullable=False),
        sa.Column("billable_default", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # weeks
    op.create_table(
        "weeks",
        sa.Column("week_start", sa.Date(), primary_key=True),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("year_number", sa.Integer(), nullable=False),
        sa.Column("is_split_month", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("month_a_key", sa.Integer(), nullable=True),
        sa.Column("month_b_key", sa.Integer(), nullable=True),
        sa.Column("qty_days_a", sa.Integer(), nullable=True),
        sa.Column("qty_days_b", sa.Integer(), nullable=True),
    )

    # assigned_projects
    op.create_table(
        "assigned_projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("employee_id", sa.String(), sa.ForeignKey("employees.id_employee"), nullable=False),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id_project"), nullable=False),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.second_id_client"), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # time_entries
    op.create_table(
        "time_entries",
        sa.Column("id_hours", sa.String(), primary_key=True),
        sa.Column("id_employee", sa.String(), sa.ForeignKey("employees.id_employee"), nullable=False),
        sa.Column("id_project", sa.String(), sa.ForeignKey("projects.id_project"), nullable=False),
        sa.Column("id_client", sa.String(), sa.ForeignKey("clients.second_id_client"), nullable=False),
        sa.Column("week_start", sa.Date(), sa.ForeignKey("weeks.week_start"), nullable=False),
        sa.Column("total_hours", sa.Numeric(6, 2), nullable=False),
        sa.Column("billable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("location_type", sa.String(), nullable=False),
        sa.Column("location_value", sa.String(), nullable=True),
        sa.Column("is_split_month", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("month_a_hours", sa.Numeric(6, 2), nullable=True),
        sa.Column("month_b_hours", sa.Numeric(6, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # invoices
    op.create_table(
        "invoices",
        sa.Column("id_invoice", sa.String(), primary_key=True),
        sa.Column("invoice_number", sa.String(), unique=True, nullable=True),
        sa.Column("primary_id_client", sa.String(), nullable=False),
        sa.Column("second_id_client", sa.String(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("total_hours", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_fees", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="'USD'"),
        sa.Column("status", sa.String(), nullable=False, server_default="'draft'"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["primary_id_client", "second_id_client"],
            ["clients.primary_id_client", "clients.second_id_client"],
        ),
    )

    # invoice_lines
    op.create_table(
        "invoice_lines",
        sa.Column("id_invoice_line", sa.String(), primary_key=True),
        sa.Column("id_invoice", sa.String(), sa.ForeignKey("invoices.id_invoice"), nullable=False),
        sa.Column("id_employee", sa.String(), sa.ForeignKey("employees.id_employee"), nullable=False),
        sa.Column("id_project", sa.String(), sa.ForeignKey("projects.id_project"), nullable=False),
        sa.Column("role_title", sa.String(), nullable=True),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("hours", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("invoice_lines")
    op.drop_table("invoices")
    op.drop_table("time_entries")
    op.drop_table("assigned_projects")
    op.drop_table("weeks")
    op.drop_table("projects")
    op.drop_table("clients")
    op.drop_table("employees")
    op.drop_index("ix_app_users_azure_oid", table_name="app_users")
    op.drop_table("app_users")
