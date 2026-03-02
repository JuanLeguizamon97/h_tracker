import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.invoice_fee_attachments import (
    create_invoice_fee_attachment, get_invoice_fee_attachments,
    get_invoice_fee_attachment, delete_invoice_fee_attachment,
)
from schemas.invoice_fee_attachments import InvoiceFeeAttachmentCreate, InvoiceFeeAttachmentOut

invoice_fee_attachments_router = APIRouter(prefix="/invoice-fee-attachments", tags=["invoice-fee-attachments"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "uploads"))


@invoice_fee_attachments_router.post("/upload", response_model=InvoiceFeeAttachmentOut, status_code=status.HTTP_201_CREATED)
async def upload_fee_attachment(
    fee_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{unique_name}"
    attachment_in = InvoiceFeeAttachmentCreate(
        fee_id=fee_id,
        file_name=unique_name,
        file_url=file_url,
        file_size=len(contents),
    )
    return create_invoice_fee_attachment(db, attachment_in)


@invoice_fee_attachments_router.get("/", response_model=List[InvoiceFeeAttachmentOut])
def list_attachments(fee_id: Optional[str] = None, db: Session = Depends(get_db)):
    return get_invoice_fee_attachments(db, fee_id=fee_id)


@invoice_fee_attachments_router.get("/{attachment_id}", response_model=InvoiceFeeAttachmentOut)
def get_attachment_detail(attachment_id: str, db: Session = Depends(get_db)):
    att = get_invoice_fee_attachment(db, attachment_id)
    if not att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return att


@invoice_fee_attachments_router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment_detail(attachment_id: str, db: Session = Depends(get_db)):
    if not delete_invoice_fee_attachment(db, attachment_id, upload_dir=UPLOAD_DIR):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
