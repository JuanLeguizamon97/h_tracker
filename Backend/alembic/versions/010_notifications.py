"""010 - notifications table

Revision ID: 010
Revises: 009
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS notifications (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            message TEXT,
            link VARCHAR,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id)"
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS notifications"))
