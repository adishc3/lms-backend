from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.comment import (
    create_comment,
    delete_comment,
    get_comment,
    list_comments_for_course,
    list_comments_for_lesson,
    update_comment,
)
from app.crud.course import get_course
from app.crud.lesson import get_lesson
from app.schemas.comment import CommentCreate, CommentRead

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/course/{course_id}", response_model=list[CommentRead])
def list_course_comments(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return list_comments_for_course(db, course_id)


@router.get("/lesson/{lesson_id}", response_model=list[CommentRead])
def list_lesson_comments(lesson_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return list_comments_for_lesson(db, lesson_id)


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_new_comment(comment_in: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    course = get_course(db, comment_in.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if comment_in.lesson_id is not None:
        lesson = get_lesson(db, comment_in.lesson_id)
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
        if lesson.course_id != comment_in.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lesson does not belong to the specified course",
            )
    return create_comment(db, current_user.id, comment_in.course_id, comment_in.lesson_id, comment_in.content)


@router.put("/{comment_id}", response_model=CommentRead)
def edit_comment(comment_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id and current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    return update_comment(db, comment, comment_in.content)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(comment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id and current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    delete_comment(db, comment)
    return None
