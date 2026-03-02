from config.database import Base
from sqlalchemy import Column, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    discount = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(String, nullable=True)
    invoice_number = Column(String, unique=True, nullable=True)
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    manual_lines = relationship("InvoiceManualLine", back_populates="invoice", cascade="all, delete-orphan")
    fees = relationship("InvoiceFee", back_populates="invoice", cascade="all, delete-orphan")
    time_entry_links = relationship("InvoiceTimeEntry", back_populates="invoice", cascade="all, delete-orphan")
