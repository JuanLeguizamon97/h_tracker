"""005 - projects: add manager_id; create project_categories table

Revision ID: 005
Revises: 004
Create Date: 2026-03-07
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Add manager_id to projects (FK to employees.id — admin employees)
    conn.execute(sa.text("""
        ALTER TABLE projects
        ADD COLUMN IF NOT EXISTS manager_id VARCHAR REFERENCES employees(id)
    """))

    # Create project_categories lookup table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS project_categories (
            id VARCHAR PRIMARY KEY,
            type VARCHAR NOT NULL,
            value VARCHAR NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
    """))

    # Seed defaults only if empty
    count = conn.execute(sa.text("SELECT COUNT(*) FROM project_categories")).scalar()
    if count == 0:
        import uuid
        defaults = [
            ("area_category", "Data Engineering"),
            ("area_category", "Frontend"),
            ("area_category", "Backend"),
            ("area_category", "Strategy"),
            ("area_category", "QA"),
            ("area_category", "DevOps"),
            ("business_unit", "Technology"),
            ("business_unit", "Consulting"),
            ("business_unit", "Operations"),
            ("business_unit", "Management"),
        ]
        for cat_type, cat_value in defaults:
            conn.execute(sa.text(
                "INSERT INTO project_categories (id, type, value, active) VALUES (:id, :type, :value, TRUE)"
            ), {"id": str(uuid.uuid4()), "type": cat_type, "value": cat_value})


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS project_categories"))
    conn.execute(sa.text("ALTER TABLE projects DROP COLUMN IF EXISTS manager_id"))
