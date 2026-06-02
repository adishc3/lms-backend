# Deployment Guide

## Production Deployment

This guide covers deploying the LMS API to production using Docker and Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- MySQL database credentials configured
- Redis instance available
- Environment variables configured in `.env` file

### Quick Start with Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd internship

# Configure environment variables
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose up -d

# Run migrations (if needed)
docker-compose exec app python -m alembic upgrade head

# Check application health
curl http://localhost:8000/health
```

### Environment Variables

Key production environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://root:password@db:3306/lms` |
| `SECRET_KEY` | JWT signing secret (use secure random string) | `change-me` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `EMAIL_ENABLED` | Enable email notifications | `false` |
| `FORCE_HTTPS` | Redirect HTTP to HTTPS | `false` |
| `TRUSTED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |

### Health Checks

The application exposes two health check endpoints:

- `GET /health` - Basic health check (always passes if service is running)
- `GET /readiness` - Readiness check (verifies database connectivity)

```bash
# Basic health check
curl http://localhost:8000/health
# Response: {"status": "ok", "service": "lms-api"}

# Readiness check
curl http://localhost:8000/readiness
# Response: {"status": "ready"} or status 503 if not ready
```

### Docker Configuration

The production Dockerfile includes:

- **Multi-stage build**: Reduces final image size
- **Non-root user**: Runs as `appuser` (UID 1000) for security
- **Health check**: Container orchestration support
- **Multiple workers**: 4 Uvicorn workers for concurrent request handling
- **Environment setup**: `PYTHONUNBUFFERED` and `PYTHONDONTWRITEBYTECODE` configured

### Docker Compose Services

- **MySQL**: Database server with health checks and persistent volume
- **Redis**: In-memory cache and rate limiter backend
- **App**: FastAPI application with automatic restart policy

### Networking

Services communicate via Docker Compose networking:

- App connects to database at: `mysql://db:3306`
- App connects to Redis at: `redis://redis:6379`
- App exposed on port: `8000`

### File Uploads

User-submitted files are stored in `static/uploads/` volume, which is mounted from the host:

```bash
# Create uploads directory on host
mkdir -p ./static/uploads
```

### Rate Limiting

The application uses Redis-backed rate limiting with configurable thresholds:

```bash
# Configuration (in .env)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

Falls back to in-memory rate limiting if Redis is unavailable.

### Logs

View application logs:

```bash
# Stream logs from app service
docker-compose logs -f app

# View logs from specific service
docker-compose logs -f db
docker-compose logs -f redis
```

### Database Migrations

```bash
# Run migrations
docker-compose exec app python -m alembic upgrade head

# Create new migration
docker-compose exec app python -m alembic revision --autogenerate -m "Description"
```

### Stopping and Cleanup

```bash
# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Production Checklist

- [ ] Set `SECRET_KEY` to a secure random value
- [ ] Configure production database URL
- [ ] Enable HTTPS (`FORCE_HTTPS=true`)
- [ ] Configure trusted hosts
- [ ] Set up email service if needed
- [ ] Configure Redis for rate limiting
- [ ] Set up monitoring/alerting
- [ ] Configure backups for MySQL volume
- [ ] Set up log aggregation
- [ ] Review security headers in app middleware

### Monitoring

Monitor container health:

```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats
```

### Scaling

To run multiple app instances with load balancing:

```yaml
# In docker-compose.yml
  app:
    deploy:
      replicas: 3
```

Requires Docker Swarm or Kubernetes for orchestration.

### Troubleshooting

**Container won't start:**
- Check logs: `docker-compose logs app`
- Verify `.env` configuration
- Check database connectivity

**Health check failing:**
- Verify MySQL is running: `docker-compose logs db`
- Check Redis connectivity: `docker-compose logs redis`
- Verify database URL in environment

**Rate limiting not working:**
- Check Redis connection: `docker-compose exec redis redis-cli ping`
- Verify `REDIS_URL` is correctly set
