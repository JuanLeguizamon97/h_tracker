"""Align schema with frontend models

Revision ID: 002
Revises: 001
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Drop all old tables in FK-dependency order using raw SQL for IF EXISTS support
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS invoice_lines CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS invoices CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS time_entries CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS assigned_projects CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS weeks CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS projects CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS clients CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS employees CASCADE"))
    # Keep app_users as-is (no schema changes needed)

    # New tables will be created by Base.metadata.create_all() in main.py
    # This migration just ensures old tables are cleaned up


def downgrade():
    pass  # No downgrade for dev environment
