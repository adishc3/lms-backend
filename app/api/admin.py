from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_admin
from app.schemas.user import UserRead, UserUpdate
from app.schemas.ai import AdminAIInsightRequest, AdminAIInsightResponse
from app.crud.user import get_user, get_users, update_user
from app.crud.admin_log import create_admin_log, get_admin_logs, get_system_context_for_ai
from app.models.user import Role
from app.core.ai import query_ai
from fastapi.responses import StreamingResponse
import csv
import io
import json

router = APIRouter(prefix="/admin", tags=["admin"])


def get_api_route_summary(app) -> str:
    routes = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in {"/openapi.json", "/docs", "/redoc", "/favicon.ico"}:
            continue
        methods = sorted([m for m in route.methods if m not in {"HEAD", "OPTIONS"}])
        if not methods:
            continue
        title = route.summary or route.description or route.name or route.path
        routes.append(f"{','.join(methods)} {route.path} — {title}")
    return "\n".join(sorted(routes))


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
def list_logs(skip: int = 0, limit: int | None = None, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    logs = get_admin_logs(db, skip=skip, limit=limit)
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user.email if log.user else "Unknown",
            "user_name": log.user.full_name if log.user else "Unknown",
            "user_role": log.user.role.value if log.user else "Unknown",
            "action": log.action,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
        if log.user and log.user.role != Role.admin
    ]


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


@router.post("/ai-insights", response_model=AdminAIInsightResponse)
async def get_ai_insights(request: Request, request_body: AdminAIInsightRequest, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """
    Get AI-powered insights about system activity, user progress, instructor courses, etc.
    """
    try:
        # Gather system context for AI analysis
        context = get_system_context_for_ai(db)
        api_routes = get_api_route_summary(request.app)
        
        # Build a simple summary
        summary = f"""System Statistics:
- Students: {context['user_statistics']['total_students']}
- Instructors: {context['user_statistics']['total_instructors']}
- Courses: {context['course_statistics']['total_courses']}
- Total Enrollments: {context['enrollment_statistics']['total_enrollments']}
- Lesson Completions: {context['lesson_completion_statistics']['total_completions']}

Available API Endpoints:
{api_routes}

Top Courses:
{json.dumps(context['course_statistics']['courses'][:10], indent=2)}

Lesson Completion Summaries:
{json.dumps(context['lesson_completion_statistics']['lesson_statistics'][:20], indent=2)}

Student Course Progress Samples:
{json.dumps(context['student_course_progress'][:20], indent=2)}

Activity Log (most recent 50 entries):
{json.dumps(context['activity_log'][:50], indent=2)}

Please answer the admin's question using only the provided application context and endpoint information. Keep the response concise and avoid unnecessary details."""
        
        # Query AI with context
        insight = await query_ai(request_body.query, summary)
        
        # Log the request
        create_admin_log(db, current_user.id, "ai_insight_query", f"query={request_body.query[:100]}")
        
        return AdminAIInsightResponse(insight=insight)
        
        # Query AI with context
        insight = await query_ai(request.query, summary)
        
        # Log the request
        create_admin_log(db, current_user.id, "ai_insight_query", f"query={request.query[:100]}")
        
        return AdminAIInsightResponse(insight=insight)
    except ValueError as e:
        create_admin_log(db, current_user.id, "ai_insight_error", f"error={str(e)[:100]}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        create_admin_log(db, current_user.id, "ai_insight_error", f"error={str(e)[:100]}")
        raise HTTPException(status_code=500, detail=str(e))
