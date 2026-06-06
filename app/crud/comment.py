from sqlalchemy.orm import Session
from app.models.comment import Comment


def create_comment(db: Session, user_id: int, course_id: int | None, lesson_id: int | None, content: str):
    comment = Comment(user_id=user_id, course_id=course_id, lesson_id=lesson_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments_for_course(db: Session, course_id: int):
    return (
        db.query(Comment)
        .filter(Comment.course_id == course_id)
        .order_by(Comment.created_at.desc())
        .all()
    )


def list_comments_for_lesson(db: Session, lesson_id: int):
    return (
        db.query(Comment)
        .filter(Comment.lesson_id == lesson_id)
        .order_by(Comment.created_at.desc())
        .all()
    )


def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def update_comment(db: Session, comment: Comment, content: str):
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment):
    db.delete(comment)
    db.commit()
