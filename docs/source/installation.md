# Installation Guide

This comprehensive guide covers all installation methods for the Kenyan Fantasy League project, from local development to production deployment.

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **Storage** | 10GB | 20GB+ |
| **CPU** | 2 cores | 4+ cores |

### Required Software

#### For Docker Setup (Recommended)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) 20.10+
- [Git](https://git-scm.com/downloads) 2.30+

#### For Manual Setup (Advanced)
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

## Quick Installation (Docker)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/kenyan-fantasy-league.git
cd kenyan-fantasy-league
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with required values:

```env
# Database
PG_USER=root
PG_PASSWORD=your_secure_password_here
POSTGRES_DB=fpl

# Django
SECRET_KEY=your-very-long-secret-key-here-50-characters-minimum
DEBUG=1
SIGNING_KEY=your-jwt-signing-key-here

# Optional: Email (for user registration)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Build and Start

```bash
# Build all containers
docker compose build

# Start all services
docker compose up -d

# Check if all services are running
docker compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE             STATUS
api                 "/start"                 api                 running
beat                "/start-celerybeat"      celery_beat         running
client              "docker-entrypoint.s…"   client              running
flower              "/start-flower"          flower              running
nginx               "/docker-entrypoint.…"   nginx               running
postgres-db         "docker-entrypoint.s…"   postgres-db         running
redis               "docker-entrypoint.s…"   redis               running
selenium            "/opt/bin/entry_poin…"   selenium            running
worker              "/start-celeryworker"    celery_worker       running
```

### 4. Database Setup

```bash
# Run database migrations
make migrate

# Create superuser account
make superuser
```

### 5. Verify Installation

Check that all services are accessible:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API**: [http://localhost:8080/api/v1/](http://localhost:8080/api/v1/)
- **Admin**: [http://localhost:8080/guardian/](http://localhost:8080/guardian/)
- **Flower**: [http://localhost:5557](http://localhost:5557)

## Manual Installation (Advanced)

### Backend Setup

#### 1. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Setup

**PostgreSQL:**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE fpl;
CREATE USER fpl_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fpl TO fpl_user;
\q
```

**Environment Variables:**
```bash
export PG_USER=fpl_user
export PG_PASSWORD=your_password
export POSTGRES_DB=fpl
export SECRET_KEY=your-secret-key
export DEBUG=1
export SIGNING_KEY=your-jwt-key
```

#### 3. Redis Setup

```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
```

#### 4. Django Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver 0.0.0.0:8000
```

#### 5. Celery Setup

Open new terminals for each:

```bash
# Terminal 1: Celery Worker
celery -A config worker --loglevel=info

# Terminal 2: Celery Beat
celery -A config beat --loglevel=info

# Terminal 3: Flower (optional)
celery -A config flower
```

### Frontend Setup

#### 1. Node.js Dependencies

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 2. Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## Platform-Specific Instructions

### Windows 10/11

#### Docker Desktop Setup

1. **Install Docker Desktop**
   - Download from [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Enable WSL2 backend during installation
   - Restart computer after installation

2. **WSL2 Setup (Recommended)**
   ```powershell
   # Enable WSL2
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # Install Ubuntu from Microsoft Store
   # Set WSL2 as default
   wsl --set-default-version 2
   ```

3. **Clone in WSL2**
   ```bash
   # Inside WSL2 terminal
   cd ~
   git clone https://github.com/your-org/kenyan-fantasy-league.git
   cd kenyan-fantasy-league
   ```

#### PowerShell Commands

```powershell
# Clone repository
git clone https://github.com/your-org/kenyan-fantasy-league.git
cd kenyan-fantasy-league

# Copy environment file
Copy-Item .env.example .env

# Build and start (use PowerShell or WSL2)
docker compose up --build -d
```

### macOS

#### Prerequisites

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# Install Git (if not installed)
brew install git
```

#### Setup

```bash
# Clone repository
git clone https://github.com/your-org/kenyan-fantasy-league.git
cd kenyan-fantasy-league

# Setup environment
cp .env.example .env
# Edit .env with your preferred editor

# Build and start
docker compose up --build -d
```

### Linux (Ubuntu/Debian)

#### Docker Installation

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

#### Project Setup

```bash
# Clone repository
git clone https://github.com/your-org/kenyan-fantasy-league.git
cd kenyan-fantasy-league

# Setup environment
cp .env.example .env
nano .env  # Edit with your values

# Build and start
docker-compose up --build -d
```

## Production Deployment

### Environment Variables

Create production `.env` file with secure values:

```env
# Security
DEBUG=0
SECRET_KEY=very-long-random-string-50-characters-minimum
SIGNING_KEY=another-secure-random-string-for-jwt

# Database (use managed service in production)
PG_USER=production_user
PG_PASSWORD=very_secure_database_password
POSTGRES_DB=fpl_production
DB_HOST=your-db-host.com
DB_PORT=5432

# Domains
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (production SMTP)
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@mg.yourdomain.com
EMAIL_HOST_PASSWORD=your-mailgun-password
EMAIL_USE_TLS=1

# Redis (use managed service)
REDIS_URL=redis://your-redis-host:6379/0

# Storage (for media files)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
```

### Docker Production

```bash
# Build for production
docker compose -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec api python manage.py migrate

# Collect static files
docker compose -f docker-compose.prod.yml exec api python manage.py collectstatic --noinput
```

### Server Requirements

**Minimum Production Server:**
- 2 CPU cores
- 4GB RAM
- 50GB SSD storage
- Ubuntu 20.04 LTS

**Recommended Production Server:**
- 4 CPU cores
- 8GB RAM
- 100GB SSD storage
- Load balancer
- Managed database (PostgreSQL)
- Managed cache (Redis)

## Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check what's using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # macOS/Linux

# Change ports in docker-compose.yml if needed
services:
  client:
    ports:
      - "3001:3000"  # Change external port
```

#### Database Connection Errors

```bash
# Check database container logs
docker compose logs postgres-db

# Test database connection
docker compose exec api python manage.py dbshell

# Reset database (development only)
docker compose down -v
docker compose up -d
make migrate
```

#### Container Build Failures

```bash
# Clean rebuild
docker compose down -v
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

#### Permission Issues (Linux/macOS)

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

### Getting Help

1. **Check logs**:
   ```bash
   docker compose logs api
   docker compose logs client
   docker compose logs postgres-db
   ```

2. **Verify environment**:
   ```bash
   docker compose exec api env | grep -E "SECRET_KEY|DEBUG|PG_"
   ```

3. **Database status**:
   ```bash
   docker compose exec api python manage.py check --database default
   ```

4. **Service health**:
   ```bash
   docker compose ps
   curl http://localhost:8080/api/v1/
   ```

## Next Steps

After successful installation:

1. **Read the [Quickstart Guide](quickstart.md)** for basic usage
2. **Check [Configuration](configuration.md)** for advanced settings
3. **Review [API Documentation](api.md)** for integration
4. **See [Contributing Guide](contributing.md)** for development

## Security Considerations

### Development Environment
- Use strong passwords in `.env`
- Don't commit `.env` files to version control
- Keep Docker and dependencies updated

### Production Environment
- Use HTTPS only
- Enable security headers
- Use managed database services
- Regular security updates
- Monitor access logs
- Implement backup strategies

---

*For production deployment assistance or custom installation requirements, please contact the development team.*

