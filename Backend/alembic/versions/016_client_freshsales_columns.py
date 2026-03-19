"""Add FreshSales CRM columns to clients table.

Revision ID: 016
Revises: 015
Create Date: 2026-03-17
"""
from alembic import op
import sqlalchemy as sa

revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clients', sa.Column('freshsales_id', sa.BigInteger(), nullable=True))
    op.add_column('clients', sa.Column('crm_synced_at', sa.DateTime(), nullable=True))
    op.add_column('clients', sa.Column('crm_created_at', sa.DateTime(), nullable=True))
    op.add_column('clients', sa.Column('crm_updated_at', sa.DateTime(), nullable=True))
    op.add_column('clients', sa.Column('crm_source', sa.String(50), nullable=True, server_default='freshsales'))
    op.create_unique_constraint('uq_clients_freshsales_id', 'clients', ['freshsales_id'])


def downgrade():
    op.drop_constraint('uq_clients_freshsales_id', 'clients', type_='unique')
    op.drop_column('clients', 'crm_source')
    op.drop_column('clients', 'crm_updated_at')
    op.drop_column('clients', 'crm_created_at')
    op.drop_column('clients', 'crm_synced_at')
    op.drop_column('clients', 'freshsales_id')
