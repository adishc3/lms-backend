from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_instructor, get_current_active_user
from app.schemas.assignment import AssignmentCreate, AssignmentRead
from app.schemas.submission import SubmissionRead
from app.crud.assignment import create_assignment, get_assignment, list_assignments_for_course
from app.crud.submission import create_submission, list_submissions_for_assignment, grade_submission, get_submission
from app.crud.enrollment import get_enrollment
from app.crud.course import get_course
from app.crud.notification import create_notification
from app.models.submission import Submission
import csv
import io

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/courses/{course_id}", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def create_course_assignment(course_id: int, payload: AssignmentCreate, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    assignment = create_assignment(db, course_id=course_id, title=payload.title, description=payload.description, due_date=payload.due_date, max_score=payload.max_score)
    return assignment


@router.get("/courses/{course_id}", response_model=list[AssignmentRead])
def list_course_assignments(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # require enrollment or instructor/admin
    if current_user.role.value == "student" and not get_enrollment(db, current_user.id, course_id):
        raise HTTPException(status_code=403, detail="Enrollment required")
    return list_assignments_for_course(db, course_id)


@router.post("/{assignment_id}/submit", response_model=SubmissionRead)
def submit_assignment(
    assignment_id: int,
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # require enrollment
    if current_user.role.value == "student" and not get_enrollment(db, current_user.id, assignment.course_id):
        raise HTTPException(status_code=403, detail="Enrollment required")
    file_path = None
    if file:
        import os
        from app.core.config import settings

        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        # read bytes to enforce size limits
        content_bytes = file.file.read()
        if len(content_bytes) > settings.UPLOAD_MAX_SIZE:
            raise HTTPException(status_code=413, detail="Uploaded file is too large")
        # sanitize filename
        base_name = os.path.basename(file.filename)
        safe_name = f"submission_{assignment_id}_{current_user.id}_{base_name}".replace(" ", "_")
        dest = os.path.join(uploads_dir, safe_name)
        with open(dest, "wb") as f:
            f.write(content_bytes)
        # store relative path
        file_path = os.path.join("static", "uploads", safe_name)

    submission = create_submission(db, assignment_id=assignment_id, user_id=current_user.id, content=content, file_path=file_path)
    create_notification(
        db,
        assignment.course.owner_id,
        title=f"Assignment submitted: {assignment.title}",
        message=f"{current_user.full_name or current_user.email} submitted '{assignment.title}' for '{assignment.course.title}'.",
    )
    return submission


@router.post("/{assignment_id}/submissions/{submission_id}/grade", response_model=SubmissionRead)
def grade_assignment(assignment_id: int, submission_id: int, grade: int, feedback: str | None = None, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # verify instructor is course owner or admin
    course = get_course(db, assignment.course_id)
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    submission = get_submission(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Submission not found")
    graded = grade_submission(db, submission, grader_id=current_user.id, grade=grade, feedback=feedback)
    create_notification(
        db,
        submission.user_id,
        title=f"Assignment graded: {assignment.title}",
        message=(
            f"Your submission for '{assignment.title}' was graded {grade}."
            + (f" Feedback: {feedback}" if feedback else "")
        ),
    )
    return graded


@router.get("/courses/{course_id}/gradebook")
def export_gradebook(course_id: int, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    # collect all submissions for assignments in this course
    assignments = list_assignments_for_course(db, course_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["assignment_id", "assignment_title", "submission_id", "student_id", "grade", "feedback"])
    for a in assignments:
        subs = list_submissions_for_assignment(db, a.id)
        for s in subs:
            writer.writerow([a.id, a.title, s.id, s.user_id, s.grade if s.grade is not None else "", s.feedback if s.feedback else ""])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=gradebook_course_{course_id}.csv"})


@router.get("/{assignment_id}/submissions")
def list_assignment_submissions(assignment_id: int, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    """List all submissions for an assignment (instructor/admin only)."""
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    course = get_course(db, assignment.course_id)
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    return list_submissions_for_assignment(db, assignment_id)


@router.get("/{assignment_id}/my-submission")
def my_submission(assignment_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get the current user's submission for an assignment."""
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.user_id == current_user.id
    ).first()
    if not submission:
        return None
    return submission
