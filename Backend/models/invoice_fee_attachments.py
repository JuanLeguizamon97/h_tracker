from config.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class InvoiceFeeAttachment(Base):

    __tablename__ = "invoice_fee_attachments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fee_id = Column(String, ForeignKey("invoice_fees.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    fee = relationship("InvoiceFee", back_populates="attachments")
