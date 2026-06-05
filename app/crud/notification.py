from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str, is_read: bool = False):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        is_read=is_read,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications_for_user(db: Session, user_id: int, limit: int = 20):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def get_notification(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()


def mark_notification_read(db: Session, notification: Notification):
    if not notification.is_read:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification
