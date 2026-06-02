from sqlalchemy.orm import Session
from app.models.admin_log import AdminLog


def create_admin_log(db: Session, user_id: int, action: str, details: str | None = None, ip_address: str | None = None) -> AdminLog:
    log = AdminLog(user_id=user_id, action=action, details=details, ip_address=ip_address)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_admin_logs(db: Session, skip: int = 0, limit: int = 50) -> list[AdminLog]:
    return db.query(AdminLog).order_by(AdminLog.created_at.desc()).offset(skip).limit(limit).all()