"""Add discount fields to invoice_lines

Revision ID: 002
Revises: 001
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('invoice_lines', sa.Column('discount', sa.Numeric(12, 2), nullable=False, server_default='0'))
    op.add_column('invoice_lines', sa.Column('discount_type', sa.String(), nullable=False, server_default='fixed'))


def downgrade() -> None:
    op.drop_column('invoice_lines', 'discount_type')
    op.drop_column('invoice_lines', 'discount')
