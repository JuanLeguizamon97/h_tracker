from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.database import get_db
from services import freshsales_service
from schemas.clients import (
    FreshSalesTestResponse,
    FreshSalesAccountsResponse,
    FreshSalesImportRequest,
    FreshSalesImportResponse,
    FreshSalesSyncResponse,
)

freshsales_router = APIRouter(prefix="/integrations/freshsales", tags=["freshsales"])


@freshsales_router.get("/test", response_model=FreshSalesTestResponse)
async def test_connection():
    """Test FreshSales API connectivity."""
    return await freshsales_service.test_connection()


@freshsales_router.get("/accounts", response_model=FreshSalesAccountsResponse)
async def list_accounts(
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
):
    """Fetch and normalize accounts from FreshSales."""
    return await freshsales_service.fetch_accounts(page=page, search=search)


@freshsales_router.post("/import", response_model=FreshSalesImportResponse)
async def import_accounts(body: FreshSalesImportRequest, db: Session = Depends(get_db)):
    """Import selected FreshSales accounts into the clients table."""
    return await freshsales_service.import_accounts(db, body.account_ids)


@freshsales_router.post("/sync/{freshsales_id}", response_model=FreshSalesSyncResponse)
async def sync_account(freshsales_id: int, db: Session = Depends(get_db)):
    """Re-sync a single client from FreshSales."""
    result = await freshsales_service.sync_account(db, freshsales_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result
