from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.token import Token
from app.db.session import SessionLocal
from app.crud.user import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token
from app.core.security import create_token, verify_token
from app.core.email import send_email
from app.core.config import settings
from datetime import datetime
from pydantic import BaseModel
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)
    # send verification email if email sending enabled
    try:
        token = create_token({"sub": user.email, "purpose": "email_verification"}, expires_minutes=60 * 24)
        verify_link = f"/auth/verify?token={token}"
        subject = "Verify your email"
        body = f"Please verify your email by visiting: {verify_link}"
        html = f"<p>Please verify your email by clicking <a href=\"{verify_link}\">here</a>.</p>"
        send_email(subject, [user.email], body, html)
    except Exception:
        pass
    return user


class EmailRequest(BaseModel):
    email: str


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token, purpose="email_verification")
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    email = payload.get("sub")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email_verified_at = datetime.utcnow()
    db.commit()
    return {"detail": "Email verified"}


@router.post("/resend-verification")
def resend_verification(req: EmailRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verified_at:
        return {"detail": "Already verified"}
    token = create_token({"sub": user.email, "purpose": "email_verification"}, expires_minutes=60 * 24)
    verify_link = f"/auth/verify?token={token}"
    subject = "Verify your email"
    body = f"Please verify your email by visiting: {verify_link}"
    html = f"<p>Please verify your email by clicking <a href=\"{verify_link}\">here</a>.</p>"
    send_email(subject, [user.email], body, html)
    return {"detail": "Verification email sent"}


@router.post("/password-reset/request")
def password_reset_request(req: EmailRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, req.email)
    if not user:
        # do not reveal user existence
        return {"detail": "If this email exists, a reset link has been sent"}
    token = create_token({"sub": user.email, "purpose": "password_reset"}, expires_minutes=60)
    reset_link = f"/auth/password-reset/confirm?token={token}"
    subject = "Password reset request"
    body = f"Reset your password by visiting: {reset_link}"
    html = f"<p>Reset your password by clicking <a href=\"{reset_link}\">here</a>.</p>"
    send_email(subject, [user.email], body, html)
    return {"detail": "If this email exists, a reset link has been sent"}


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/password-reset/confirm")
def password_reset_confirm(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    data = verify_token(payload.token, purpose="password_reset")
    if not data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    email = data.get("sub")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # update password
    from app.core.security import get_password_hash

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"detail": "Password updated"}


@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
        email = payload.get("email") or payload.get("username")
        password = payload.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")

    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_active_user)):
    return current_user
