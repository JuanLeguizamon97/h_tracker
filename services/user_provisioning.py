from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from models.app_user import AppUser


def upsert_app_user(
    db: Session,
    azure_oid: str,
    email: Optional[str] = None,
    display_name: Optional[str] = None,
) -> AppUser:
    """
    Just-in-time provisioning: create or update a local user row
    based on Azure AD token claims.
    """
    user = db.query(AppUser).filter(AppUser.azure_oid == azure_oid).first()
    now = datetime.now(timezone.utc)

    if user is None:
        user = AppUser(
            azure_oid=azure_oid,
            email=email,
            display_name=display_name,
            last_login_at=now,
        )
        db.add(user)
    else:
        if email is not None:
            user.email = email
        if display_name is not None:
            user.display_name = display_name
        user.last_login_at = now
        user.updated_at = now

    db.commit()
    db.refresh(user)
    return user
