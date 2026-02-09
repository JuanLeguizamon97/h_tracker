# routers/invoice_lines.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db

from services.invoice_lines import (
    create_invoice_line,
    get_invoice_lines,
    get_invoice_line as get_invoice_line_service,
    update_invoice_line as update_invoice_line_service,
    delete_invoice_line as delete_invoice_line_service,
)
from schemas.invoice_lines import InvoiceLineCreate, InvoiceLineUpdate, InvoiceLineOut


invoice_lines_router = APIRouter(
    prefix="/invoice-lines",
    tags=["invoice_lines"],
)


@invoice_lines_router.post(
    "/",
    response_model=InvoiceLineOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_invoice_line(
    line_in: InvoiceLineCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_invoice_line(db, line_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@invoice_lines_router.get(
    "/",
    response_model=List[InvoiceLineOut],
    status_code=status.HTTP_200_OK,
)
def list_invoice_lines(
    id_invoice: Optional[str] = None,
    id_employee: Optional[str] = None,
    id_project: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_invoice_lines(
        db,
        id_invoice=id_invoice,
        id_employee=id_employee,
        id_project=id_project,
    )


@invoice_lines_router.get(
    "/{id_invoice_line}",
    response_model=InvoiceLineOut,
    status_code=status.HTTP_200_OK,
)
def get_invoice_line_detail(
    id_invoice_line: str,
    db: Session = Depends(get_db),
):
    line = get_invoice_line_service(db, id_invoice_line)
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice line not found",
        )
    return line


@invoice_lines_router.put(
    "/{id_invoice_line}",
    response_model=InvoiceLineOut,
    status_code=status.HTTP_200_OK,
)
def update_invoice_line_detail(
    id_invoice_line: str,
    line_in: InvoiceLineUpdate,
    db: Session = Depends(get_db),
):
    line = update_invoice_line_service(db, id_invoice_line, line_in)
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice line not found",
        )
    return line


@invoice_lines_router.delete(
    "/{id_invoice_line}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_invoice_line_detail(
    id_invoice_line: str,
    db: Session = Depends(get_db),
):
    deleted = delete_invoice_line_service(db, id_invoice_line)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice line not found",
        )
    return
