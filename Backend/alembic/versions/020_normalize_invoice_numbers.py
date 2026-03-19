"""Renumber Draft invoices to new format: IPC{YEAR}{SEQ} / PIN{YEAR}{SEQ}.

Old format: IPC-2026-002  (dashes)
New format: IPC20261      (no dashes, prefix + year + cumulative seq)

Rules:
- Only Draft invoices are renumbered.
- Sent/Paid invoices keep their existing numbers unchanged.
- Sequences restart from 1 for each company in new format.
- year=0 sequence rows are reset to reflect renumbered counts.

Revision ID: 020
Revises: 019
Create Date: 2026-03-17
"""
import uuid
from alembic import op
from sqlalchemy import text

revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None

_PREFIXES = {"IPC": "IPC", "PI": "PIN"}


def upgrade():
    bind = op.get_bind()

    for company, prefix in _PREFIXES.items():
        rows = bind.execute(text("""
            SELECT id, invoice_number, created_at
            FROM invoices
            WHERE owner_company = :co
              AND status = 'draft'
              AND (invoice_number IS NULL OR invoice_number NOT LIKE :pat)
            ORDER BY created_at ASC
        """), {"co": company, "pat": f"{prefix}%"}).fetchall()

        if not rows:
            print(f"[020] {company}: no draft invoices to renumber")
            continue

        seq = 0
        for row in rows:
            seq += 1
            created_year = row[2].year if row[2] else 2026
            new_number = f"{prefix}{created_year}{seq}"
            bind.execute(text(
                "UPDATE invoices SET invoice_number = :num WHERE id = :id"
            ), {"num": new_number, "id": row[0]})
            print(f"[020] {company}: {row[1]} → {new_number}")

        # Reset year=0 sequence to the count of renumbered invoices
        bind.execute(text("""
            INSERT INTO invoice_number_sequences (id, company, year, last_sequence)
            VALUES (:id, :company, 0, :seq)
            ON CONFLICT (company, year) DO UPDATE
                SET last_sequence = EXCLUDED.last_sequence
        """), {"id": str(uuid.uuid4()), "company": company, "seq": seq})
        print(f"[020] {company}: year=0 sequence set to {seq}")


def downgrade():
    pass  # Renaming is not safely reversible without storing old values
