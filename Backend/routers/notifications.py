from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from services.notifications import get_notifications, mark_read, mark_all_read
from schemas.notifications import NotificationOut

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


@notifications_router.get("/", response_model=List[NotificationOut])
def list_notifications(
    user_id: str,
    unread_only: bool = False,
    db: Session = Depends(get_db),
):
    return get_notifications(db, user_id=user_id, unread_only=unread_only)


@notifications_router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: str, user_id: str, db: Session = Depends(get_db)):
    n = mark_read(db, notification_id, user_id)
    if not n:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return n


@notifications_router.post("/mark-all-read")
def mark_all_notifications_read(user_id: str, db: Session = Depends(get_db)):
    count = mark_all_read(db, user_id)
    return {"marked": count}
