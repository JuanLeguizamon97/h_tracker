from datetime import datetime, date, timezone
import uuid
from config.database import Base
from sqlalchemy import Column, String, Date, DateTime, Numeric, ForeignKeyConstraint
from sqlalchemy.orm import relationship


class Invoice(Base):
    __tablename__ = "invoices"

    id_invoice = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = Column(String, unique=True, nullable=True)
    primary_id_client = Column(String, nullable=False)
    second_id_client = Column(String, nullable=False)
    period_start = Column(Date, nullable=False)  
    period_end = Column(Date, nullable=False)   
    issue_date = Column(Date, nullable=False, default=date.today)
    total_hours = Column(Numeric(10, 2), nullable=False, default=0)
    total_fees = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False, default="draft")  # draft/sent/paid/cancelled
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Definir Foreign Key compuesta
    __table_args__ = (
        ForeignKeyConstraint(
            ['primary_id_client', 'second_id_client'],
            ['clients.primary_id_client', 'clients.second_id_client']
        ),
    )

    client = relationship("Client", back_populates="invoices")
    lines = relationship(
        "InvoiceLine",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
