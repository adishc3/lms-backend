from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_admin
from app.schemas.user import UserRead, UserUpdate
from app.crud.user import get_user, get_users, update_user
from app.crud.admin_log import create_admin_log, get_admin_logs
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


def log_admin_action(user_id: int, action: str, details: str | None = None, ip_address: str | None = None):
    def _log(db: Session = Depends(get_db)):
        create_admin_log(db, user_id, action, details, ip_address)
    return _log


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    create_admin_log(db, current_user.id, "list_users")
    return get_users(db)


@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    create_admin_log(db, current_user.id, "read_user", f"user_id={user_id}")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def edit_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    create_admin_log(db, current_user.id, "update_user", f"user_id={user_id}")
    return update_user(db, user, user_in)


@router.get("/logs", response_model=list[dict])
def list_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    logs = get_admin_logs(db, skip=skip, limit=limit)
    return [{"id": log.id, "user_id": log.user_id, "action": log.action, "details": log.details, "ip_address": log.ip_address, "created_at": log.created_at} for log in logs]


@router.post("/users/import-csv")
def import_users(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    errors = []
    
    for row in reader:
        try:
            from app.crud.user import create_user
            from app.schemas.user import UserCreate
            user_in = UserCreate(email=row["email"], password=row["password"], full_name=row.get("full_name"), role=row.get("role", "student"))
            create_user(db, user_in)
            imported += 1
        except Exception as e:
            errors.append(str(e))
    
    create_admin_log(db, current_user.id, "import_users", f"imported={imported}")
    return {"imported": imported, "errors": errors}


@router.get("/users/export-csv")
def export_users(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    from app.models.user import User
    users = db.query(User).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "full_name", "role"])
    for u in users:
        writer.writerow([u.id, u.email, u.full_name, u.role.value])
    output.seek(0)
    create_admin_log(db, current_user.id, "export_users", f"count={len(users)}")
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users.csv"})
