import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from app.core.config import settings, ALLOWED_ORIGINS
from app.core.redis_rate_limiter import RateLimitMiddleware
from app.db.session import SessionLocal, Base, engine


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

# Read origins from environment variable, falling back to localhost if not set
raw_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
origins.extend(["http://localhost", "http://127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "interest-cohort=()"
    return response


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


@app.get("/")
async def root():
    """API entry point with documentation links."""
    return {
        "message": "Welcome to Learn@will LMS API",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "available_endpoints": {
            "health": "/health",
            "readiness": "/readiness",
            "api": "/api"
        }
    }


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
