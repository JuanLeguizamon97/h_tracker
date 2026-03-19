"""
Invoice number generation service.

Format: {PREFIX}{YEAR}{SEQ}
  IPC  → IPC202614   (prefix IPC, year 2026, cumulative seq 14)
  PI   → PIN20261    (prefix PIN, year 2026, cumulative seq 1)

Sequence is cumulative per company — never resets.
Year in the number is the invoice creation year.
Counter stored in invoice_number_sequences using year=0 sentinel row.

Counter is incremented ONLY on actual invoice creation, never on previews.
"""
import uuid
import logging
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

_PREFIXES: dict[str, str] = {
    "IPC": "IPC",
    "PI":  "PIN",
}


def _format(company: str, year: int, seq: int) -> str:
    prefix = _PREFIXES.get(company, company)
    return f"{prefix}{year}{seq}"


def preview_next_number(db: Session, company: str) -> dict:
    """
    Non-destructive preview of the next invoice number.
    Reads last_sequence from year=0 row and adds 1.
    Does NOT increment the counter — safe to call repeatedly.
    """
    row = db.execute(
        text("SELECT last_sequence FROM invoice_number_sequences WHERE company = :co AND year = 0"),
        {"co": company},
    ).scalar()
    seq = (int(row) if row is not None else 0) + 1
    year = date.today().year
    return {
        "company": company,
        "invoice_number": _format(company, year, seq),
    }


def atomic_generate_number(db: Session, company: str, issue_year: int | None = None) -> str:
    """
    Atomically increment the year=0 counter and return the locked invoice number.
    Called ONCE at invoice creation — never called again for the same invoice.
    Does NOT commit — caller owns the transaction.
    Thread-safe via INSERT ... ON CONFLICT DO UPDATE ... RETURNING.
    """
    year = issue_year or date.today().year
    result = db.execute(
        text("""
            INSERT INTO invoice_number_sequences (id, company, year, last_sequence)
            VALUES (:id, :company, 0, 1)
            ON CONFLICT (company, year) DO UPDATE
                SET last_sequence = invoice_number_sequences.last_sequence + 1
            RETURNING last_sequence
        """),
        {"id": str(uuid.uuid4()), "company": company},
    ).scalar()
    return _format(company, year, int(result))
