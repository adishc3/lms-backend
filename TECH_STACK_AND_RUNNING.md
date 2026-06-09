# Technology Stack and Running Instructions

## Overview
This document provides a detailed explanation of the technology stack used in the Beginner LMS (Learning Management System) project and various ways to run the project through the terminal.

## Technology Stack

### Backend Technologies
- **Framework**: FastAPI (modern, fast web framework for building APIs with Python 3.12+)
- **ASGI Server**: Uvicorn (lightning-fast ASGI server)
- **ORM**: SQLAlchemy (SQL toolkit and Object-Relational Mapping library)
- **Database Migrations**: Alembic (lightweight database migration tool)
- **Data Validation**: Pydantic (data validation and settings management)
- **Authentication**: 
  - JWT (JSON Web Tokens) for stateless authentication
  - Passlib with Bcrypt for secure password hashing
- **Template Engine**: Jinja2 (for server-side rendered HTML templates)
- **HTTP Client**: HTTPX (for making HTTP requests, used for AI integrations)
- **Environment Management**: Python-dotenv (for loading environment variables from .env file)

### Frontend Technologies
- **HTML5**: Markup language for structuring web content
- **CSS3**: Styling language for presentation
- **Bootstrap 5**: CSS framework for responsive, mobile-first design
- **Jinja2 Templates**: Server-side templating for dynamic HTML generation
- **Static Assets**: CSS, JavaScript, and images served via FastAPI's static files

### Database
- **MySQL 8.0**: Relational database management system
- **Connection**: Using PyMySQL driver via SQLAlchemy

### DevOps & Infrastructure
- **Containerization**: Docker (for consistent development and deployment environments)
- **Orchestration**: Docker Compose (for defining and running multi-container applications)
- **CI/CD**: GitHub Actions (for automated testing and deployment pipelines)

### Development Tools
- **Testing**: Pytest (testing framework)
- **Code Quality**: 
  - Ruff (fast Python linter and code formatter)
  - Black (code formatter)
  - Isort (import sorter)
- **Dependency Management**: pip (Python package installer) with requirements.txt

## Project Structure
```
├── app/
│   ├── api/          # API route modules (auth, courses, admin, etc.)
│   ├── core/         # Core configuration and settings
│   ├── db/           # Database session and models
│   └── main.py       # FastAPI application entry point
├── alembic/          # Database migration scripts
├── static/           # Static files (CSS, JS, images, uploads)
├── templates/        # Jinja2 HTML templates
├── tests/            # Test files
├── .github/          # GitHub workflows and configurations
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile        # Docker image definition
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment variables
└── README.md         # Project overview and basic instructions
```

## Ways to Run the Project

### 1. Local Development (Without Docker)

#### Prerequisites
- Python 3.12 or higher
- Git
- MySQL server (running locally or accessible via network)

#### Steps
```powershell
# Clone the repository (if not already done)
git clone <repository-url>
cd internship

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment example and configure
Copy-Item .env.example .env
# Edit .env file to set your DATABASE_URL and other variables

# Run the application
uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000

### 2. Using Docker Compose (Recommended for Development)

#### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose (included with Docker Desktop)

#### Steps
```powershell
# Copy environment example and configure (if needed)
Copy-Item .env.example .env
# Edit .env file as needed (default values work for local development)

# Build and start the containers
docker compose up --build

# To run in detached mode (background)
docker compose up -d --build

# To stop and remove containers
docker compose down

# To stop containers but preserve volumes
docker compose stop
```

The application will be available at http://localhost:8000
MySQL will be available at localhost:3306

### 3. Using Docker Compose for Production-like Setup

```powershell
# For production, you might want to:
docker compose -f docker-compose.yml up -d --build

# View logs
docker compose logs -f

# View running services
docker compose ps

# Execute commands inside the app container
docker compose exec app python -m pytest -q
```

### 4. Running Tests

#### Using Virtual Environment
```powershell
# Activate virtual environment if not already active
.\.venv\Scripts\Activate.ps1

# Run all tests
python -m pytest -q

# Run tests with coverage (if coverage.py is installed)
python -m pytest --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_auth.py -v
```

#### Using Docker Compose
```powershell
# Run tests inside the app container
docker compose exec app python -m pytest -q

# Or run a one-off container for tests
docker compose run --rm app python -m pytest -q
```

### 5. Database Management

#### With Docker Compose
```powershell
# Access MySQL shell
docker compose exec db mysql -uroot -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE}

# Or use mysql client from host (if installed)
mysql -h 127.0.0.1 -P 3306 -u root -p
```

#### Migration Management
```powershell
# Generate new migration (after model changes)
.\.venv\Scripts\Activate.ps1
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show migration history
alembic history
```

## Environment Variables

The project uses environment variables for configuration. Copy `.env.example` to `.env` and modify as needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `mysql+pymysql://root:password@db:3306/lms` |
| `SECRET_KEY` | Secret key for JWT signing | `change-me` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | `60` |
| `SMTP_HOST` | SMTP server host for emails | `localhost` |
| `SMTP_PORT` | SMTP server port | `1025` |
| `SMTP_USER` | SMTP username | *(empty)* |
| `SMTP_PASSWORD` | SMTP password | *(empty)* |
| `SMTP_USE_TLS` | Use TLS for SMTP | `False` |
| `SMTP_USE_SSL` | Use SSL for SMTP | `False` |
| `EMAIL_FROM` | Email sender address | `noreply@example.com` |
| `EMAIL_ENABLED` | Enable email functionality | `False` |
| `AI_ENABLED` | Enable AI features | `False` |
| `AI_PROVIDER_URL` | AI service provider URL | *(empty)* |
| `AI_API_KEY` | AI service API key | *(empty)* |
| `AI_DEFAULT_MODEL` | Default AI model | `gemini-text-1` |
| `AI_TEMPERATURE` | AI model temperature | `0.5` |

- For Google Gemini, use `AI_PROVIDER_URL=https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateMessage` and `AI_DEFAULT_MODEL=gemini-text-1`.
| `AI_TIMEOUT_SECONDS` | AI request timeout | `30` |
| `UPLOAD_FOLDER` | Directory for file uploads | `static/uploads` |
| `UPLOAD_MAX_SIZE` | Maximum upload size in bytes | `20000000` (20MB) |
| `TRUSTED_HOSTS` | Comma-separated trusted hosts | `localhost,127.0.0.1,testserver` |
| `FORCE_HTTPS` | Force HTTPS redirect | `False` |
| `GZIP_MIN_SIZE` | Minimum size for GZIP compression | `1000` |

## API Documentation

When the application is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide interactive API documentation based on the OpenAPI specification.

## Makefile Shortcuts (If Available)

If a Makefile is present in the project, you might have shortcuts like:
```powershell
make dev        # Start development environment
make test       # Run tests
make lint       # Run linting
make format     # Format code
make clean      # Clean up temporary files
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify MySQL service is running
   - Check DATABASE_URL in .env file
   - Ensure correct credentials and host/port

2. **Port Already in Use**
   - Another service is using port 8000
   - Change the port in docker-compose.yml or uvicorn command
   - Or stop the conflicting service

3. **Module Not Found Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

4. **Docker Volume Permissions**
   - On Windows, ensure Docker has access to the project directory
   - Try running Docker Desktop as administrator if needed

## Next Steps

After getting the project running:
1. Visit http://localhost:8000 to see the application
2. Register a new user account
3. Explore the API documentation at http://localhost:8000/docs
4. Check the admin dashboard (if implemented)
5. Review the code in the `app/` directory to understand the implementation