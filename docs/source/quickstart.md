# Quickstart Guide

Get the Kenyan Fantasy League up and running locally in under 10 minutes!

## Prerequisites

Ensure you have the following installed on your Windows machine:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) 
- [Git](https://git-scm.com/downloads)
- A text editor (VS Code recommended)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/kenyan-fantasy-league.git
cd kenyan-fantasy-league
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
# Copy the example environment file
cp .env.example .env
```

**Required Environment Variables:**

Edit `.env` file with these minimum required values:

```env
# Database Configuration
PG_USER=root
PG_PASSWORD=your_secure_password
POSTGRES_DB=fpl

# Django Settings  
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=1
SIGNING_KEY=your-jwt-signing-key

# Redis (default is fine for local development)
REDIS_URL=redis://redis:6379/0
```

### 3. Start the Application

Build and run all services with Docker Compose:

```bash
# Build the containers
docker compose build

# Start all services
docker compose up
```

This will start:
- **API Server**: Django backend at `http://localhost:8080/api/v1/`
- **Client**: Vue.js frontend at `http://localhost:3000`
- **PostgreSQL**: Database server
- **Redis**: For caching and Celery tasks
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task execution
- **Flower**: Task monitoring at `http://localhost:5557`

### 4. Initial Database Setup

In a new terminal, run the database migrations:

```bash
# Run database migrations
make migrate

# Create a superuser account
make superuser
```

### 5. Access the Application

- **Frontend**: Open [http://localhost:3000](http://localhost:3000)
- **API Admin**: Open [http://localhost:8080/guardian/](http://localhost:8080/guardian/)
- **API Docs**: Open [http://localhost:8080/api/v1/](http://localhost:8080/api/v1/)
- **Task Monitor**: Open [http://localhost:5557](http://localhost:5557)

## Verify Installation

1. **Frontend**: You should see the KFL homepage with login/register options
2. **Backend**: Admin interface should be accessible with your superuser credentials
3. **Tasks**: Flower should show active Celery workers
4. **Database**: Check that tables are created: `make manage-db`

## Common Issues

### Container Build Failures
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Port Conflicts
If ports 3000, 8080, or 5432 are already in use:
```bash
# Check what's using the ports
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8080"
netstat -ano | findstr ":5432"
```

### Database Connection Issues
```bash
# Verify database is running
docker compose ps postgres-db

# Check database logs
docker compose logs postgres-db
```

## Development Commands

Common development tasks using the Makefile:

```bash
# View all available commands
make

# Development workflow
make up          # Start services
make down        # Stop services
make migrate     # Run migrations
make test        # Run tests
make superuser   # Create admin user

# Code quality
make black       # Format Python code
make flake8      # Lint Python code
make test-html   # Run tests with coverage report
```

## Next Steps

- Read the [Architecture Overview](architecture.md) to understand the system design
- Check the [Configuration Guide](configuration.md) for detailed environment setup
- Explore the [API Documentation](api.md) for available endpoints
- Review [Contributing Guidelines](contributing.md) to start developing

## Need Help?

- Check [Troubleshooting](troubleshooting.md) for common solutions
- Review [Operations Guide](operations.md) for deployment and monitoring
- Open an issue on GitHub for bugs or feature requests

---

*Estimated setup time: 5-10 minutes*
