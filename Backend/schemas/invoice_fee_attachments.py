# schemas/invoice_fee_attachments.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InvoiceFeeAttachmentBase(BaseModel):
    fee_id: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None


class InvoiceFeeAttachmentCreate(InvoiceFeeAttachmentBase):
    pass


class InvoiceFeeAttachmentOut(InvoiceFeeAttachmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
