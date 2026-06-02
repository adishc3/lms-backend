from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.badge import (
    award_badge,
    get_badge,
    get_badge_by_code,
    get_badges,
    get_course_badges,
    get_user_badges,
)
from app.api.deps import get_db
from app.schemas.badge import BadgeCreate, BadgeRead

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("", response_model=list[BadgeRead])
def list_badges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_badges(db, skip=skip, limit=limit)


@router.get("/{badge_id}", response_model=BadgeRead)
def read_badge(badge_id: int, db: Session = Depends(get_db)):
    badge = get_badge(db, badge_id)
    if badge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found")
    return badge


@router.get("/user/{user_id}", response_model=list[BadgeRead])
def read_user_badges(user_id: int, db: Session = Depends(get_db)):
    return get_user_badges(db, user_id)


@router.get("/course/{course_id}", response_model=list[BadgeRead])
def read_course_badges(course_id: int, db: Session = Depends(get_db)):
    return get_course_badges(db, course_id)


@router.post("", response_model=BadgeRead, status_code=status.HTTP_201_CREATED)
def create_badge_endpoint(badge_in: BadgeCreate, db: Session = Depends(get_db)):
    if badge_in.badge_code and get_badge_by_code(db, badge_in.badge_code) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Badge already exists")
    badge = award_badge(
        db,
        user_id=badge_in.user_id,
        badge_code=badge_in.badge_code or "",
        badge_name=badge_in.badge_name,
        badge_description=badge_in.badge_description,
        course_id=badge_in.course_id,
    )
    if badge is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Badge already awarded")
    return badge
