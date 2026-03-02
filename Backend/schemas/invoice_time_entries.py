# schemas/invoice_time_entries.py
from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class InvoiceTimeEntryBase(BaseModel):
    invoice_id: str
    time_entry_id: str


class InvoiceTimeEntryCreate(InvoiceTimeEntryBase):
    pass


class InvoiceTimeEntryOut(InvoiceTimeEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class BulkLinkRequest(BaseModel):
    entries: List[InvoiceTimeEntryCreate]
