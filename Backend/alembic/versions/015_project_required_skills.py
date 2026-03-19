"""Add project_required_skills table

Revision ID: 015
Revises: 014
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_required_skills",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("min_level", sa.Integer(), nullable=True, server_default="2"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skill_catalog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "skill_id", name="uq_project_required_skill"),
    )
    op.create_index(
        "ix_project_required_skills_project_id",
        "project_required_skills",
        ["project_id"],
    )


def downgrade():
    op.drop_index("ix_project_required_skills_project_id", "project_required_skills")
    op.drop_table("project_required_skills")
