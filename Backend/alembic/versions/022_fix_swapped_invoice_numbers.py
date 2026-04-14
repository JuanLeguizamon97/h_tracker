"""Fix swapped invoice numbers from migrations 020/021.

Migration 020 renamed PI drafts but accidentally left one with IPC prefix,
and migration 021 renamed IPC drafts but one ended up with PIN prefix.
Result: PIN20261 has owner_company=IPC and IPC20263 has owner_company=PI.

This migration corrects the swap by renaming each invoice to match
its actual owner_company.

Revision ID: 022
Revises: 021
Create Date: 2026-03-26
"""

from alembic import op
from sqlalchemy import text

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # The two swapped invoices:
    # - PIN20261 belongs to IPC → should be IPC20263 (3rd IPC draft)
    # - IPC20263 belongs to PI  → should be PIN20261 (1st PI draft)

    # Use a temp name to avoid unique constraint collision during swap
    bind.execute(text(
        "UPDATE invoices SET invoice_number = '__TEMP__' WHERE invoice_number = 'PIN20261' AND owner_company = 'IPC'"
    ))
    bind.execute(text(
        "UPDATE invoices SET invoice_number = 'PIN20261' WHERE invoice_number = 'IPC20263' AND owner_company = 'PI'"
    ))
    bind.execute(text(
        "UPDATE invoices SET invoice_number = 'IPC20263' WHERE invoice_number = '__TEMP__' AND owner_company = 'IPC'"
    ))

    print("[022] Fixed swapped invoice numbers: PIN20261 (IPC) → IPC20263, IPC20263 (PI) → PIN20261")

    # Sequences are already correct at 3 for both companies — no change needed.


def downgrade():
    bind = op.get_bind()
    bind.execute(text(
        "UPDATE invoices SET invoice_number = '__TEMP__' WHERE invoice_number = 'IPC20263' AND owner_company = 'IPC'"
    ))
    bind.execute(text(
        "UPDATE invoices SET invoice_number = 'IPC20263' WHERE invoice_number = 'PIN20261' AND owner_company = 'PI'"
    ))
    bind.execute(text(
        "UPDATE invoices SET invoice_number = 'PIN20261' WHERE invoice_number = '__TEMP__' AND owner_company = 'IPC'"
    ))
