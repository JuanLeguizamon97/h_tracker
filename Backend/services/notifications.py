from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from models.notifications import Notification


def create_notification(
    db: Session,
    user_id: str,
    type: str,
    title: str,
    message: Optional[str] = None,
    link: Optional[str] = None,
) -> Notification:
    n = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
    )
    db.add(n)
    return n


def notify_invoice_generated(db: Session, invoice_id: str, invoice_number: str, project_name: str, manager_id: Optional[str], total: float) -> None:
    """Create an in-app notification for the project manager when an invoice is generated."""
    if not manager_id:
        return
    create_notification(
        db,
        user_id=manager_id,
        type="invoice_generated",
        title=f"Invoice ready for review — {project_name}",
        message=f"A draft invoice ({invoice_number}) has been generated for {project_name}. "
                f"Total: ${total:,.2f}. Please review before sending to the client.",
        link=f"/invoices/{invoice_id}/edit",
    )


def get_notifications(db: Session, user_id: str, unread_only: bool = False) -> List[Notification]:
    q = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    return q.order_by(Notification.created_at.desc()).limit(50).all()


def mark_read(db: Session, notification_id: str, user_id: str) -> Optional[Notification]:
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    ).first()
    if n:
        n.is_read = True
        db.commit()
        db.refresh(n)
    return n


def mark_all_read(db: Session, user_id: str) -> int:
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return count
