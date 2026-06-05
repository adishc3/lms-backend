from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.notification import list_notifications_for_user, get_notification, mark_notification_read
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return list_notifications_for_user(db, current_user.id)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    notification = get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    return mark_notification_read(db, notification)
