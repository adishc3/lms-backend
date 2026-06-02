import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.admin import router as admin_router
from app.api.quizzes import router as quizzes_router
from app.api.ai import router as ai_router
from app.api.assignments import router as assignments_router
from app.api.certificates import router as certificates_router
from app.api.insights import router as insights_router
from app.api.badges import router as badges_router
from app.core.redis_rate_limiter import RateLimitMiddleware
from app.core.config import settings
from app.db.session import SessionLocal, Base, engine

# Construct path to frontend/dist relative to project root
# __file__ = backend/app/main.py, so we go up 2 levels to reach project root
frontend_dist = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
frontend_assets_dir = os.path.join(frontend_dist, "assets")
frontend_index_path = os.path.join(frontend_dist, "index.html")


@asynccontextmanager
async def lifespan(app: FastAPI):
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Learn@will", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=settings.GZIP_MIN_SIZE)
if settings.FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)
allowed_hosts = [host.strip() for host in settings.TRUSTED_HOSTS.split(",") if host.strip()]
if allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

if os.path.isdir(frontend_assets_dir):
    app.mount("/assets", StaticFiles(directory=frontend_assets_dir), name="frontend_assets")


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "interest-cohort=()"
    return response


app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount all API routers under /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(quizzes_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(assignments_router, prefix="/api")
app.include_router(certificates_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(badges_router, prefix="/api")

# add Redis-backed rate limiter middleware (falls back to in-memory)
app.add_middleware(RateLimitMiddleware)



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if os.path.isfile(frontend_index_path):
        with open(frontend_index_path, "r", encoding="utf-8") as template_file:
            return HTMLResponse(template_file.read())

    template_path = os.path.join("templates", "app.html")
    with open(template_path, "r", encoding="utf-8") as template_file:
        return HTMLResponse(template_file.read())


@app.get("/favicon.svg")
async def favicon():
    if os.path.isfile(os.path.join(frontend_dist, "favicon.svg")):
        return FileResponse(os.path.join(frontend_dist, "favicon.svg"))
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/icons.svg")
async def icons():
    if os.path.isfile(os.path.join(frontend_dist, "icons.svg")):
        return FileResponse(os.path.join(frontend_dist, "icons.svg"))
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def react_app_catchall(request: Request, full_path: str):
    # List of API endpoints that should not be served as React routes
    api_prefixes = (
        "auth/",
        "admin/",
        "quizzes/",
        "ai/",
        "assignments/",
        "certificates/",
        "insights/",
        "health",
        "readiness",
        "static/",
        "assets/",
        "favicon.svg",
        "icons.svg",
    )
    
    # Check if this is a static file (has file extension)
    if "." in full_path.split("/")[-1]:
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check if this is an API-only endpoint
    if full_path.startswith(api_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check the Accept header to determine if this is an API request
    accept_header = request.headers.get("accept", "")
    # If the request explicitly wants JSON (not from browser), return 404
    if "application/json" in accept_header and "text/html" not in accept_header:
        # This is an API request, let the API routes handle it
        raise HTTPException(status_code=404, detail="Not Found")

    # Serve React SPA for all client-side routes
    if os.path.isfile(frontend_index_path):
        with open(frontend_index_path, "r", encoding="utf-8") as template_file:
            return HTMLResponse(template_file.read())

    template_path = os.path.join("templates", "app.html")
    with open(template_path, "r", encoding="utf-8") as template_file:
        return HTMLResponse(template_file.read())


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "lms-api"}


@app.get("/readiness")
async def readiness_check():
    """Readiness check endpoint - verifies database connectivity."""
    try:
        from app.db.session import SessionLocal
        with SessionLocal() as session:
            session.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse({"status": "not ready", "error": str(e)}, status_code=503)
