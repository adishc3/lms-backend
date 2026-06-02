# LMS Architecture Summary
- Beginner-friendly monolithic Python FastAPI LMS.
- Frontend: HTML5,CSS3,Bootstrap 5,Jinja2 Templates (FastAPI equivalent of Thymeleaf)
- Backend: Python 3.12+,FastAPI,Uvicorn (ASGI server),SQLAlchemy ORM,Alembic (database migrations),Pydantic (data validation),JWT Authentication,Passlib/Bcrypt (password hashing)
- Database: MySQL.

## Core User Roles
- Student: register, login, view courses, enroll, view lessons.
- Instructor: create/manage courses and lessons.
- Admin: manage users and courses, access admin dashboard.

## Key Application Modules
- Authentication: registration, login, password validation, session management, role-based access.
- Course management: create, edit, view courses.
- Lesson management: add lessons, display lesson content.
- Enrollment: student course enrollment and access control.
- Notifications: email alerts for enrolled students when new lessons are added.
- Session timeout: JWT-based token expiration managed via secure HTTP-only cookies.

## Architecture
- Layered design: Routers → Services → Models (SQLAlchemy) → MySQL.
- Typical flow: browser request → FastAPI router → service logic → SQLAlchemy session → database.
- Permission enforcement via FastAPI Dependencies (Depends) and OAuth2/JWT scopes.

## AI feature concepts
- AI Study Assistant: student doubt answering and lesson summarization.
- AI Quiz Generator: instructors auto-generate quizzes from lesson content.
- AI Progress Insights: analyze student progress, weak topics, recommendations.
- AI Enrollment Recommender: suggest courses based on history and interests.
- External AI APIs like OpenAI/Gemini with Spring WebClient.
- External AI APIs like OpenAI/Gemini with HTTPX or official Python SDKs.

## Important design takeaways
- Beginner architecture emphasizes simplicity, clear layer separation, and security.
- Good candidate for enhancement via file uploads, quizzes, search, JWT, Docker, certificates.
- AI features are positioned as extensions rather than core dependencies.
