# Configuration Guide

This guide covers all configuration options for the Kenyan Fantasy League application, including environment variables, Django settings, and deployment configurations.

## Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize values:

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `your-very-secure-secret-key-here` | ✅ |
| `DEBUG` | Enable Django debug mode (0/1) | `1` | ✅ |
| `PG_USER` | PostgreSQL username | `root` | ✅ |
| `PG_PASSWORD` | PostgreSQL password | `secure_password` | ✅ |
| `POSTGRES_DB` | PostgreSQL database name | `fpl` | ✅ |
| `SIGNING_KEY` | JWT token signing key | `your-jwt-signing-key` | ✅ |

### Optional Variables

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` | Restrict in production |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` | For caching and tasks |
| `EMAIL_HOST` | SMTP server hostname | `localhost` | For user notifications |
| `EMAIL_PORT` | SMTP server port | `587` | Usually 587 or 465 |
| `EMAIL_HOST_USER` | SMTP username | - | Required for email |
| `EMAIL_HOST_PASSWORD` | SMTP password | - | Required for email |
| `CELERY_BROKER_URL` | Celery broker URL | Uses `REDIS_URL` | Task queue broker |
| `CELERY_RESULT_BACKEND` | Celery result backend | Uses `REDIS_URL` | Task result storage |

## Django Settings

The application uses Django's settings module system with environment-specific configurations:

### Settings Structure

```
config/settings/
├── __init__.py
├── base.py          # Common settings
├── development.py   # Development overrides
└── production.py    # Production overrides
```

### Base Settings (`base.py`)

Key configuration areas:

#### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('PG_USER'), 
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST': 'postgres-db',  # Docker service name
        'PORT': '5432',
    }
}
```

#### Installed Apps

```python
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_countries',
    'phonenumber_field',
    'django_filters',
    'djoser',
    'rest_framework_simplejwt',
    'djcelery_email',
    'django_celery_beat',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.profiles',
    'apps.kpl',
    'apps.fantasy',
]
```

#### REST Framework Configuration

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_THROTTLE_CLASSES': ('rest_framework.throttling.UserRateThrottle',),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '1000/min',
        'premium': '12/minute',
    },
}
```

#### JWT Configuration

```python
SIMPLE_JWT = {
    'AUTH_HEADERS_TYPES': ('Bearer', 'JWT'),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'SIGNING_KEY': os.getenv('SIGNING_KEY'),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
```

#### Authentication Backend (Djoser)

```python
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        'user_create': 'apps.accounts.serializers.CreateUserSerializer,',
        'user': 'apps.accounts.serializers.UserSerializer',
        'current_user': 'apps.accounts.serializers.UserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
}
```

## Celery Configuration

Background task processing is handled by Celery with Redis as the broker.

### Celery Settings

```python
# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'update-kpl-standings': {
        'task': 'apps.kpl.tasks.standings.get_kpl_table',
        'schedule': timedelta(days=1).total_seconds(),
    },
    'update-kpl-fixtures': {
        'task': 'apps.kpl.tasks.fixtures.get_kpl_fixtures', 
        'schedule': timedelta(days=2).total_seconds(),
    },
    'update-kpl-gameweek': {
        'task': 'apps.kpl.tasks.fixtures.update_active_gameweek',
        'schedule': timedelta(days=1).total_seconds(),
    },
}
```

### Task Types

| Task | Module | Schedule | Purpose |
|------|--------|----------|---------|
| `get_kpl_table` | `apps.kpl.tasks.standings` | Daily | Update league standings |
| `get_kpl_fixtures` | `apps.kpl.tasks.fixtures` | Every 2 days | Sync fixture data |
| `update_active_gameweek` | `apps.kpl.tasks.fixtures` | Daily | Update current gameweek |
| `get_kpl_players` | `apps.kpl.tasks.players` | Manual | Import player data |

## Logging Configuration

Comprehensive logging is configured for debugging and monitoring:

### Log Configuration

```python
LOG_LEVEL = "INFO"
LOG_DIR = BASE_DIR / "logs"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'fantasy_league.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'apps': {
            'level': 'INFO', 
            'handlers': ['console'],
            'propagate': False
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Log Files

| File | Content | Rotation |
|------|---------|----------|
| `logs/fantasy_league.log` | Application logs | 10MB, 5 files |
| Console output | Real-time logging | N/A |

## Docker Configuration

### Docker Compose Services

The application runs in multiple containers orchestrated by Docker Compose:

#### Service Configuration

```yaml
services:
  api:
    build: ./docker/local/django/
    container_name: api
    command: /start
    env_file: .env
    depends_on: [postgres-db, redis]
    
  client:
    build: ./client/
    container_name: client
    ports: ["3000:3000"]
    command: npm run dev -- --host 0.0.0.0
    
  postgres-db:
    image: postgres:12.0-alpine
    container_name: postgres-db
    ports: ["5432:5432"]
    environment:
      - POSTGRES_USER=${PG_USER}
      - POSTGRES_PASSWORD=${PG_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      
  redis:
    image: redis:latest
    container_name: redis
    
  nginx:
    build: ./docker/local/nginx/
    container_name: nginx
    ports: ["8080:80"]
    depends_on: [api]
    
  celery_worker:
    build: ./docker/local/django/
    container_name: worker
    command: /start-celeryworker
    env_file: .env
    depends_on: [redis, postgres-db]
    
  celery_beat:
    build: ./docker/local/django/
    container_name: beat
    command: /start-celerybeat
    env_file: .env
    depends_on: [redis, postgres-db]
    
  flower:
    build: ./docker/local/django/
    container_name: flower
    command: /start-flower
    ports: ["5557:5555"]
    env_file: .env
    depends_on: [redis, postgres-db]
```

### Volume Mounts

- **Source Code**: `.:/app` for live development
- **Static Files**: `static_volume:/app/staticfiles`
- **Media Files**: `media_volume:/app/mediafiles`
- **Database**: `postgres_data:/var/lib/postgresql/data/`

## Frontend Configuration

### Vue.js Configuration

The frontend is configured via several files:

#### Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "run-p type-check \"build-only {@}\" --",
    "preview": "vite preview",
    "build-only": "vite build",
    "type-check": "vue-tsc --build --force"
  }
}
```

#### Vite Configuration (`vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://api:8000',
        changeOrigin: true
      }
    }
  }
})
```

#### Tailwind CSS (`tailwind.config.js`)

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

## Production Configuration

### Security Settings

For production deployment, ensure these security configurations:

```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Database Configuration

Production database settings should use connection pooling:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,  # Connection pooling
        'OPTIONS': {
            'sslmode': 'require',  # SSL in production
        },
    }
}
```

### Static Files (Production)

```python
# Static files configuration for production
STATIC_URL = '/staticfiles/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'
```

## Environment-Specific Settings

### Development

```python
# development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Development-specific logging
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}
```

### Production

```python
# production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Production optimizations
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Validation

### Environment Validation Script

Create a script to validate configuration:

```python
# validate_config.py
import os
import sys

REQUIRED_VARS = [
    'SECRET_KEY',
    'DEBUG', 
    'PG_USER',
    'PG_PASSWORD',
    'POSTGRES_DB',
    'SIGNING_KEY',
]

def validate_environment():
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"Missing required environment variables: {missing}")
        sys.exit(1)
    
    print("✅ All required environment variables are set")

if __name__ == '__main__':
    validate_environment()
```

## Troubleshooting Configuration

### Common Issues

#### Environment Variables Not Loading

```bash
# Check if .env file exists
ls -la .env

# Verify environment variables in container
docker compose exec api env | grep SECRET_KEY
```

#### Database Connection Issues

```bash
# Test database connection
docker compose exec api python manage.py dbshell

# Check database logs
docker compose logs postgres-db
```

#### Redis Connection Issues

```bash
# Test Redis connection
docker compose exec api python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"

# Check Redis logs
docker compose logs redis
```

## Configuration Checklist

### Development Setup
- [ ] `.env` file created from `.env.example`
- [ ] Required environment variables set
- [ ] Docker containers running
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] Celery tasks running

### Production Deployment
- [ ] Production environment variables configured
- [ ] SSL certificates installed
- [ ] Static files collected
- [ ] Database backup strategy implemented
- [ ] Monitoring and logging configured
- [ ] Security headers enabled

---

*Proper configuration is crucial for application security, performance, and maintainability.*
