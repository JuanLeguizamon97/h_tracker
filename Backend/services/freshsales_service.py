"""
FreshSales CRM API integration service.

Docs: https://developers.freshworks.com/crm/api/
Authentication: Token token={API_KEY} header.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

FRESHSALES_DOMAIN = os.getenv("FRESHSALES_DOMAIN", "")
FRESHSALES_API_KEY = os.getenv("FRESHSALES_API_KEY", "")

# Retry config for rate-limited requests
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def _is_configured() -> bool:
    return bool(FRESHSALES_DOMAIN and FRESHSALES_API_KEY)


def _base_url() -> str:
    return f"https://{FRESHSALES_DOMAIN}.myfreshworks.com/crm/sales/api"


def _headers() -> dict:
    return {
        "Authorization": f"Token token={FRESHSALES_API_KEY}",
        "Content-Type": "application/json",
    }


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception:
        return None


def _normalize_account_preview(account: dict) -> dict:
    """Minimal fields for the import list UI."""
    address = account.get("address") or {}
    industry = None
    if account.get("industry_type"):
        industry = account["industry_type"].get("name")
    return {
        "id": account.get("id"),
        "name": account.get("name") or "",
        "email": account.get("email"),
        "phone": account.get("phone"),
        "website": account.get("website"),
        "city": address.get("city"),
        "country": address.get("country"),
        "industry": industry,
    }


def _map_account_to_client(account: dict, contact: dict | None = None) -> dict:
    """Map FreshSales account fields to Horas+ client schema."""
    address = account.get("address") or {}
    industry = None
    if account.get("industry_type"):
        industry = account["industry_type"].get("name")

    mapped: dict = {
        "name": account.get("name") or "",
        "email": account.get("email"),
        "phone": account.get("phone"),
        "website": account.get("website"),
        "street_address_1": address.get("street"),
        "city": address.get("city"),
        "state": address.get("state"),
        "country": address.get("country"),
        "zip": address.get("zipcode"),
        "industry": industry,
        "freshsales_id": account.get("id"),
        "crm_created_at": _parse_dt(account.get("created_at")),
        "crm_updated_at": _parse_dt(account.get("updated_at")),
        "crm_synced_at": datetime.now(timezone.utc),
        "crm_source": "freshsales",
    }

    if account.get("owner"):
        mapped["rep"] = account["owner"].get("name")

    if contact:
        first = contact.get("first_name") or ""
        last = contact.get("last_name") or ""
        mapped["manager_name"] = f"{first} {last}".strip() or None
        mapped["manager_email"] = contact.get("email")
        mapped["manager_phone"] = contact.get("work_number")
        mapped["job_title"] = contact.get("job_title")

    return mapped


async def _get_with_retry(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """GET with up to MAX_RETRIES retries on 429."""
    import asyncio
    for attempt in range(MAX_RETRIES):
        r = await client.get(url, **kwargs)
        if r.status_code != 429:
            return r
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
    return r


async def test_connection() -> dict:
    """Test FreshSales API connectivity."""
    if not _is_configured():
        return {"success": False, "error": "FRESHSALES_DOMAIN or FRESHSALES_API_KEY not set"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await _get_with_retry(client, f"{_base_url()}/settings/profiles", headers=_headers())

        if r.status_code == 200:
            data = r.json()
            user = data.get("user", {})
            return {
                "success": True,
                "user": user.get("display_name") or user.get("email", ""),
                "domain": FRESHSALES_DOMAIN,
            }
        elif r.status_code == 401:
            return {"success": False, "error": "Invalid FreshSales API key"}
        elif r.status_code == 404:
            return {"success": False, "error": "FreshSales domain not found"}
        else:
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except httpx.TimeoutException:
        return {"success": False, "error": "FreshSales API timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def fetch_accounts(page: int = 1, search: str | None = None) -> dict:
    """Fetch accounts from FreshSales, normalized for the import UI."""
    if not _is_configured():
        return {"accounts": [], "total": 0, "error": "Not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            if search:
                url = f"{_base_url()}/accounts/search"
                params = {"q": search, "per_page": 25}
            else:
                url = f"{_base_url()}/accounts"
                params = {"page": page, "per_page": 25}

            r = await _get_with_retry(client, url, headers=_headers(), params=params)

        if r.status_code == 401:
            return {"accounts": [], "total": 0, "error": "Invalid FreshSales API key"}
        if r.status_code == 504 or isinstance(r, Exception):
            return {"accounts": [], "total": 0, "error": "FreshSales API timeout"}
        if r.status_code != 200:
            return {"accounts": [], "total": 0, "error": f"HTTP {r.status_code}"}

        data = r.json()
        accounts_raw = data.get("accounts", [])
        meta = data.get("meta", {})

        return {
            "accounts": [_normalize_account_preview(a) for a in accounts_raw],
            "total": meta.get("total_count", len(accounts_raw)),
        }
    except httpx.TimeoutException:
        return {"accounts": [], "total": 0, "error": "FreshSales API timeout"}
    except Exception as e:
        logger.error(f"FreshSales fetch_accounts error: {e}")
        return {"accounts": [], "total": 0, "error": str(e)}


async def fetch_account_detail(freshsales_id: int) -> dict | None:
    """Fetch single account full detail."""
    if not _is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await _get_with_retry(client, f"{_base_url()}/accounts/{freshsales_id}", headers=_headers())
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get("account", data)
    except Exception as e:
        logger.error(f"FreshSales fetch_account_detail({freshsales_id}) error: {e}")
        return None


async def fetch_primary_contact(account_id: int) -> dict | None:
    """Fetch the first contact linked to an account."""
    if not _is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await _get_with_retry(
                client,
                f"{_base_url()}/contacts",
                headers=_headers(),
                params={"filter": f"account_id:{account_id}", "per_page": 1},
            )
        if r.status_code != 200:
            return None
        data = r.json()
        contacts = data.get("contacts", [])
        return contacts[0] if contacts else None
    except Exception as e:
        logger.error(f"FreshSales fetch_primary_contact({account_id}) error: {e}")
        return None


async def import_accounts(db, account_ids: list[int]) -> dict:
    """Import / upsert FreshSales accounts into the clients table."""
    from models.clients import Client

    imported = 0
    updated = 0
    errors = []

    for fid in account_ids:
        try:
            account = await fetch_account_detail(fid)
            if not account:
                errors.append({"id": fid, "error": "Account not found in FreshSales"})
                continue

            contact = await fetch_primary_contact(fid)
            mapped = _map_account_to_client(account, contact)

            existing = db.query(Client).filter(Client.freshsales_id == fid).first()
            if existing:
                for k, v in mapped.items():
                    setattr(existing, k, v)
                db.commit()
                db.refresh(existing)
                updated += 1
            else:
                new_client = Client(**mapped)
                db.add(new_client)
                db.commit()
                db.refresh(new_client)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing FreshSales account {fid}: {e}")
            db.rollback()
            errors.append({"id": fid, "error": str(e)})

    return {"imported": imported, "updated": updated, "skipped": 0, "errors": errors}


async def sync_account(db, freshsales_id: int) -> dict:
    """Re-sync a single client from FreshSales."""
    from models.clients import Client

    account = await fetch_account_detail(freshsales_id)
    if not account:
        return {"success": False, "error": "Account not found in FreshSales"}

    contact = await fetch_primary_contact(freshsales_id)
    mapped = _map_account_to_client(account, contact)

    try:
        existing = db.query(Client).filter(Client.freshsales_id == freshsales_id).first()
        if existing:
            for k, v in mapped.items():
                setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            return {"success": True, "updated": True, "client_id": existing.id}
        else:
            new_client = Client(**mapped)
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            return {"success": True, "updated": False, "client_id": new_client.id}
    except Exception as e:
        db.rollback()
        logger.error(f"FreshSales sync_account({freshsales_id}) error: {e}")
        return {"success": False, "error": str(e)}
