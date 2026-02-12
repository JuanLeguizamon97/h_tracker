import os
import logging
from fastapi import APIRouter, Depends, Security, HTTPException, Request
from sqlalchemy.orm import Session

from config.database import db_session
from services.user_provisioning import upsert_app_user
from schemas.app_user import AppUserOut

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_MODE = os.getenv("AUTH_MODE", "azure")

# Dev-only mock identity
_MOCK_USER = {
    "oid": "00000000-0000-0000-0000-000000000001",
    "email": "dev@impactpoint.local",
    "name": "Dev User",
}


def _extract_claims_from_token(token) -> dict:
    """Extract user claims from a validated fastapi-azure-auth token."""
    # fastapi-azure-auth returns a TokenPayload with .claims dict
    claims = getattr(token, "claims", {})
    oid = claims.get("oid") or claims.get("sub") or ""
    email = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )
    display_name = claims.get("name", "")
    return {"oid": oid, "email": email, "display_name": display_name}


if AUTH_MODE == "mock" and os.getenv("ENV", "dev") != "prod":
    logger.warning("*** /auth/me running in MOCK mode — NOT for production ***")

    @auth_router.get("/me", response_model=AppUserOut)
    def get_current_user_mock(
        request: Request,
        db: Session = Depends(db_session),
    ):
        dev_oid = request.headers.get("X-Dev-User-Oid", _MOCK_USER["oid"])
        dev_email = request.headers.get("X-Dev-User-Email", _MOCK_USER["email"])
        dev_name = request.headers.get("X-Dev-User-Name", _MOCK_USER["name"])
        user = upsert_app_user(db, azure_oid=dev_oid, email=dev_email, display_name=dev_name)
        return user

else:
    from utils.auth_microsoft import azure_scheme

    @auth_router.get("/me", response_model=AppUserOut)
    def get_current_user(
        db: Session = Depends(db_session),
        token=Security(azure_scheme),
    ):
        claims = _extract_claims_from_token(token)
        oid = claims["oid"]
        if not oid:
            raise HTTPException(status_code=401, detail="Token missing oid/sub claim")
        user = upsert_app_user(
            db,
            azure_oid=oid,
            email=claims.get("email") or None,
            display_name=claims.get("display_name") or None,
        )
        return user
