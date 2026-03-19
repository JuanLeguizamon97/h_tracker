from config.database import Base
from sqlalchemy import Column, String, Integer, UniqueConstraint
import uuid


class InvoiceNumberSequence(Base):
    __tablename__ = "invoice_number_sequences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company = Column(String(10), nullable=False)
    year = Column(Integer, nullable=False)
    last_sequence = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('company', 'year', name='uq_invoice_seq_company_year'),
    )
