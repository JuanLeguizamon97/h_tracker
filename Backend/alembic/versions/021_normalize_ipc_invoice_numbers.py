"""Renumber remaining IPC Draft invoices from IPC-YYYY-NNN to IPC{YEAR}{SEQ}.

Migration 020 missed IPC drafts because their numbers start with 'IPC'
(matching the broad LIKE 'IPC%' pattern). This migration uses a stricter
check: numbers containing a dash are old format.

Revision ID: 021
Revises: 020
Create Date: 2026-03-17
"""
import uuid
from alembic import op
from sqlalchemy import text

revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Find IPC Draft invoices still in old format (contains a dash)
    rows = bind.execute(text("""
        SELECT id, invoice_number, created_at
        FROM invoices
        WHERE owner_company = 'IPC'
          AND status = 'draft'
          AND invoice_number LIKE '%-%'
        ORDER BY created_at ASC
    """)).fetchall()

    if not rows:
        print("[021] IPC: no dash-format draft invoices to renumber")
        return

    seq = 0
    for row in rows:
        seq += 1
        created_year = row[2].year if row[2] else 2026
        new_number = f"IPC{created_year}{seq}"
        bind.execute(text(
            "UPDATE invoices SET invoice_number = :num WHERE id = :id"
        ), {"num": new_number, "id": row[0]})
        print(f"[021] IPC: {row[1]} → {new_number}")

    # Reset IPC year=0 sequence to the count of renamed invoices
    bind.execute(text("""
        INSERT INTO invoice_number_sequences (id, company, year, last_sequence)
        VALUES (:id, 'IPC', 0, :seq)
        ON CONFLICT (company, year) DO UPDATE
            SET last_sequence = EXCLUDED.last_sequence
    """), {"id": str(uuid.uuid4()), "seq": seq})
    print(f"[021] IPC: year=0 sequence set to {seq}")


def downgrade():
    pass
